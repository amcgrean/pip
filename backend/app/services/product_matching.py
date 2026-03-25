from dataclasses import dataclass

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.product_alias import ProductAlias
from app.models.vendor import Vendor
from app.models.vendor_product_mapping import VendorProductMapping
from app.schemas.domain import ProductMatchRequest, ProductMatchResponse, ProductMatchResult
from app.utils.text import normalize_text, tokenize

DEFAULT_MATCH_LIMIT = 5
MAX_MATCH_LIMIT = 20

HIGH_CONFIDENCE_THRESHOLD = 120
MEDIUM_CONFIDENCE_THRESHOLD = 60


@dataclass
class MappingScore:
    score: int
    reasons: list[str]
    mapping: VendorProductMapping | None


def _confidence(score: int) -> str:
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "medium"
    return "low"


def _score_mapping(
    mapping: VendorProductMapping,
    normalized_query_text: str,
    normalized_vendor_name: str,
    normalized_vendor_code: str,
    normalized_vendor_sku: str,
    query_tokens: set[str],
) -> MappingScore:
    score = 0
    reasons: list[str] = []
    vendor_name = normalize_text(mapping.vendor.vendor_name if mapping.vendor else "")
    vendor_code = normalize_text(mapping.vendor.vendor_code if mapping.vendor else "")
    mapping_vendor_sku = normalize_text(mapping.vendor_sku)
    mapping_vendor_desc = normalize_text(mapping.vendor_description)
    mapping_vendor_uom = normalize_text(mapping.vendor_uom)

    if normalized_vendor_sku and mapping_vendor_sku == normalized_vendor_sku:
        score += 140
        reasons.append("exact vendor_sku match")

    if normalized_vendor_name and vendor_name:
        if vendor_name == normalized_vendor_name:
            score += 35
            reasons.append("exact vendor_name match")
        elif normalized_vendor_name in vendor_name or vendor_name in normalized_vendor_name:
            score += 15
            reasons.append("partial vendor_name match")

    if normalized_vendor_code and vendor_code:
        if vendor_code == normalized_vendor_code:
            score += 35
            reasons.append("exact vendor_code match")
        elif normalized_vendor_code in vendor_code or vendor_code in normalized_vendor_code:
            score += 15
            reasons.append("partial vendor_code match")

    if normalized_query_text and mapping_vendor_sku and mapping_vendor_sku == normalized_query_text:
        score += 130
        reasons.append("query matches vendor_sku exactly")

    if normalized_query_text and mapping_vendor_desc and normalized_query_text in mapping_vendor_desc:
        score += 25
        reasons.append("query contained in vendor_description")
    if normalized_query_text and mapping_vendor_uom and normalized_query_text == mapping_vendor_uom:
        score += 18
        reasons.append("exact vendor_uom match")

    if query_tokens and mapping_vendor_desc:
        overlap = len(query_tokens & tokenize(mapping_vendor_desc))
        if overlap:
            token_points = min(overlap * 4, 20)
            score += token_points
            reasons.append(f"vendor_description token overlap ({overlap})")
    if query_tokens and mapping_vendor_uom:
        overlap = len(query_tokens & tokenize(mapping_vendor_uom))
        if overlap:
            token_points = min(overlap * 2, 6)
            score += token_points
            reasons.append(f"vendor_uom token overlap ({overlap})")

    if mapping.is_primary:
        score += 5
        reasons.append("primary vendor mapping")

    return MappingScore(score=score, reasons=reasons, mapping=mapping)


def _score_product(
    product: Product,
    normalized_query_text: str,
    normalized_vendor_name: str,
    normalized_vendor_code: str,
    normalized_vendor_sku: str,
) -> ProductMatchResult:
    score = 0
    reasons: list[str] = []

    def add(points: int, reason: str):
        nonlocal score
        score += points
        reasons.append(reason)

    query_tokens = tokenize(normalized_query_text)

    internal_sku = normalize_text(product.internal_sku)
    normalized_name = normalize_text(product.normalized_name)
    canonical_name = normalize_text(product.canonical_name)
    display_name = normalize_text(product.display_name)
    description = normalize_text(product.description)
    keywords = normalize_text(product.keywords)
    search_text = normalize_text(product.search_text)
    master_search_text = normalize_text(product.master_search_text)

    if normalized_query_text and internal_sku == normalized_query_text:
        add(125, "exact internal_sku match")

    for alias in product.aliases:
        alias_text = normalize_text(alias.alias_text)
        if not alias_text or not normalized_query_text:
            continue
        if alias_text == normalized_query_text:
            add(95, "exact alias match")
            break
        if normalized_query_text in alias_text:
            add(35, "query contained in alias")
            break

    product_names = (
        (normalized_name, "exact normalized_name match"),
        (canonical_name, "exact canonical_name match"),
        (display_name, "exact display_name match"),
    )
    if normalized_query_text:
        for field_value, reason in product_names:
            if field_value and field_value == normalized_query_text:
                add(85, reason)

        if master_search_text and normalized_query_text in master_search_text:
            add(40, "query contained in master_search_text")
        if search_text and normalized_query_text in search_text:
            add(30, "query contained in search_text")
        if keywords and normalized_query_text in keywords:
            add(20, "query contained in keywords")
        if description and normalized_query_text in description:
            add(15, "query contained in description")

    searchable_tokens = set()
    for value in (
        internal_sku,
        normalized_name,
        canonical_name,
        display_name,
        description,
        keywords,
        search_text,
        master_search_text,
    ):
        searchable_tokens.update(tokenize(value))
    for alias in product.aliases:
        searchable_tokens.update(tokenize(alias.alias_text))
    if query_tokens:
        overlap = len(query_tokens & searchable_tokens)
        if overlap:
            token_points = min(overlap * 3, 24)
            add(token_points, f"product token overlap ({overlap})")

    mapping_scores = [
        _score_mapping(
            mapping=m,
            normalized_query_text=normalized_query_text,
            normalized_vendor_name=normalized_vendor_name,
            normalized_vendor_code=normalized_vendor_code,
            normalized_vendor_sku=normalized_vendor_sku,
            query_tokens=query_tokens,
        )
        for m in product.mappings
    ]
    best_mapping = max(mapping_scores, key=lambda m: m.score, default=MappingScore(score=0, reasons=[], mapping=None))
    score += best_mapping.score
    reasons.extend(best_mapping.reasons)

    unique_reasons = list(dict.fromkeys(reasons))
    mapping = best_mapping.mapping
    return ProductMatchResult(
        product_id=product.id,
        internal_sku=product.internal_sku,
        normalized_name=product.normalized_name,
        display_name=product.display_name,
        canonical_name=product.canonical_name,
        score=score,
        confidence=_confidence(score),
        match_reasons=unique_reasons,
        matched_vendor_name=mapping.vendor.vendor_name if mapping and mapping.vendor else None,
        matched_vendor_code=mapping.vendor.vendor_code if mapping and mapping.vendor else None,
        matched_vendor_sku=mapping.vendor_sku if mapping else None,
        matched_vendor_description=mapping.vendor_description if mapping else None,
        matched_vendor_uom=mapping.vendor_uom if mapping else None,
        is_primary_vendor_mapping=mapping.is_primary if mapping else None,
    )


def match_products(db: Session, payload: ProductMatchRequest) -> ProductMatchResponse:
    normalized_query_text = normalize_text(payload.query_text)
    normalized_vendor_name = normalize_text(payload.vendor_name)
    normalized_vendor_code = normalize_text(payload.vendor_code)
    normalized_vendor_sku = normalize_text(payload.vendor_sku)
    raw_query_text = (payload.query_text or "").strip()
    raw_vendor_sku = (payload.vendor_sku or "").strip()
    raw_vendor_code = (payload.vendor_code or "").strip()

    search_fragments = [value for value in (normalized_query_text, normalized_vendor_name, normalized_vendor_code, normalized_vendor_sku) if value]
    if not search_fragments:
        return ProductMatchResponse(matches=[])

    candidate_conditions = []
    if normalized_query_text:
        term = f"%{normalized_query_text}%"
        candidate_conditions.extend(
            [
                Product.internal_sku.ilike(term),
                Product.normalized_name.ilike(term),
                Product.description.ilike(term),
                Product.canonical_name.ilike(term),
                Product.display_name.ilike(term),
                Product.keywords.ilike(term),
                Product.search_text.ilike(term),
                Product.master_search_text.ilike(term),
                Product.aliases.any(ProductAlias.alias_text.ilike(term)),
                Product.mappings.any(
                    or_(
                        VendorProductMapping.vendor_sku.ilike(term),
                        VendorProductMapping.vendor_description.ilike(term),
                        VendorProductMapping.vendor_uom.ilike(term),
                    )
                ),
            ]
        )
        # Also search using the raw query text to catch cases where normalization
        # converts punctuation to spaces (e.g. "SKU-1" normalizes to "sku 1" but
        # the raw form "sku-1" still matches stored "SKU-1" via ilike).
        if raw_query_text and raw_query_text.lower() != normalized_query_text:
            raw_term = f"%{raw_query_text}%"
            candidate_conditions.extend(
                [
                    Product.internal_sku.ilike(raw_term),
                    Product.aliases.any(ProductAlias.alias_text.ilike(raw_term)),
                    Product.mappings.any(VendorProductMapping.vendor_sku.ilike(raw_term)),
                ]
            )
    if normalized_vendor_name:
        candidate_conditions.append(
            Product.mappings.any(
                VendorProductMapping.vendor.has(Vendor.vendor_name.ilike(f"%{normalized_vendor_name}%"))
            )
        )
    if normalized_vendor_code:
        candidate_conditions.append(
            Product.mappings.any(
                VendorProductMapping.vendor.has(Vendor.vendor_code.ilike(f"%{normalized_vendor_code}%"))
            )
        )
    if normalized_vendor_sku:
        candidate_conditions.append(
            Product.mappings.any(VendorProductMapping.vendor_sku.ilike(f"%{normalized_vendor_sku}%"))
        )
        # Also search with the raw vendor_sku in case normalization changes punctuation to spaces
        if raw_vendor_sku and raw_vendor_sku.lower() != normalized_vendor_sku:
            candidate_conditions.append(
                Product.mappings.any(VendorProductMapping.vendor_sku.ilike(f"%{raw_vendor_sku}%"))
            )

    if normalized_vendor_code and normalized_vendor_sku:
        candidate_conditions.append(
            Product.mappings.any(
                and_(
                    VendorProductMapping.vendor_sku.ilike(f"%{normalized_vendor_sku}%"),
                    VendorProductMapping.vendor.has(Vendor.vendor_code.ilike(f"%{normalized_vendor_code}%")),
                )
            )
        )
        # Also check with raw values
        if (raw_vendor_sku and raw_vendor_sku.lower() != normalized_vendor_sku) or (raw_vendor_code and raw_vendor_code.lower() != normalized_vendor_code):
            candidate_conditions.append(
                Product.mappings.any(
                    and_(
                        VendorProductMapping.vendor_sku.ilike(f"%{raw_vendor_sku}%"),
                        VendorProductMapping.vendor.has(Vendor.vendor_code.ilike(f"%{raw_vendor_code}%")),
                    )
                )
            )

    candidates = (
        db.query(Product)
        .filter(or_(*candidate_conditions))
        .options(
            joinedload(Product.aliases),
            joinedload(Product.mappings).joinedload(VendorProductMapping.vendor),
        )
        .limit(250)
        .all()
    )

    scored = [
        _score_product(
            product=product,
            normalized_query_text=normalized_query_text,
            normalized_vendor_name=normalized_vendor_name,
            normalized_vendor_code=normalized_vendor_code,
            normalized_vendor_sku=normalized_vendor_sku,
        )
        for product in candidates
    ]
    scored = [item for item in scored if item.score > 0]
    scored.sort(key=lambda item: (-item.score, item.product_id))

    limit = max(1, min(payload.limit or DEFAULT_MATCH_LIMIT, MAX_MATCH_LIMIT))
    return ProductMatchResponse(matches=scored[:limit])
