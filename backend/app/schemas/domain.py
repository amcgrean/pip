from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class VendorBase(BaseModel):
    vendor_code: str = Field(min_length=1, max_length=50)
    vendor_name: str = Field(min_length=1, max_length=255)
    is_active: bool = True


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    vendor_code: str | None = Field(default=None, min_length=1, max_length=50)
    vendor_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class VendorOut(VendorBase):
    id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    internal_sku: str = Field(min_length=1, max_length=80)
    normalized_name: str = Field(min_length=1, max_length=255)
    product_type: str | None = None
    category_major: str | None = None
    category_minor: str | None = None
    species_or_material: str | None = None
    grade: str | None = None
    thickness: str | None = None
    width: str | None = None
    length: str | None = None
    unit_of_measure: str | None = None
    description: str | None = None
    status: str = "active"
    branch_scope: str | None = None

    canonical_name: str | None = None
    display_name: str | None = None
    extended_description: str | None = None
    category: str | None = None
    subcategory: str | None = None
    finish: str | None = None
    treatment: str | None = None
    profile: str | None = None
    thickness_numeric: float | None = None
    width_numeric: float | None = None
    length_numeric: float | None = None
    keywords: str | None = None
    search_text: str | None = None
    master_search_text: str | None = None
    last_sold_date: date | None = None
    is_active: bool = True
    is_stock_item: bool = False
    match_priority: int | None = None
    source_system_id: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    internal_sku: str | None = None
    normalized_name: str | None = None
    product_type: str | None = None
    category_major: str | None = None
    category_minor: str | None = None
    species_or_material: str | None = None
    grade: str | None = None
    thickness: str | None = None
    width: str | None = None
    length: str | None = None
    unit_of_measure: str | None = None
    description: str | None = None
    status: str | None = None
    branch_scope: str | None = None

    canonical_name: str | None = None
    display_name: str | None = None
    extended_description: str | None = None
    category: str | None = None
    subcategory: str | None = None
    finish: str | None = None
    treatment: str | None = None
    profile: str | None = None
    thickness_numeric: float | None = None
    width_numeric: float | None = None
    length_numeric: float | None = None
    keywords: str | None = None
    search_text: str | None = None
    master_search_text: str | None = None
    last_sold_date: date | None = None
    is_active: bool | None = None
    is_stock_item: bool | None = None
    match_priority: int | None = None
    source_system_id: str | None = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    attachment_count: int = 0

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: list[ProductOut]
    meta: PaginationMeta


class VendorMappingBase(BaseModel):
    vendor_id: int
    product_id: int
    vendor_sku: str
    vendor_description: str | None = None
    vendor_uom: str | None = None
    last_cost: Decimal | None = None
    is_primary: bool = False


class VendorMappingCreate(VendorMappingBase):
    pass


class VendorMappingUpdate(BaseModel):
    vendor_sku: str | None = None
    vendor_description: str | None = None
    vendor_uom: str | None = None
    last_cost: Decimal | None = None
    is_primary: bool | None = None


class VendorMappingOut(VendorMappingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    vendor_name: str | None = None
    vendor_code: str | None = None

    class Config:
        from_attributes = True


class ProductNoteCreate(BaseModel):
    note_text: str = Field(min_length=1)
    note_type: str = "general"


class ProductNoteOut(BaseModel):
    id: int
    product_id: int
    note_text: str
    note_type: str
    created_by: int | None
    created_by_name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductAttachmentOut(BaseModel):
    id: int
    product_id: int
    file_name: str
    file_path: str
    file_type: str | None
    uploaded_by: int | None
    created_at: datetime
    download_url: str

    class Config:
        from_attributes = True


class ProductAliasOut(BaseModel):
    id: int
    product_id: int
    alias_text: str
    alias_type: str | None
    is_preferred: bool
    source: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductImageOut(BaseModel):
    id: int
    product_id: int
    storage_path: str
    image_type: str | None
    alt_text: str | None
    sort_order: int
    source: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductDocumentOut(BaseModel):
    id: int
    product_id: int
    document_type: str
    title: str
    file_url: str | None
    attachment_id: int | None
    source: str | None
    effective_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportJobOut(BaseModel):
    id: int
    source_type: str
    file_name: str
    status: str
    total_rows: int
    inserted_rows: int
    updated_rows: int
    error_rows: int
    error_log: str | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class ImportSummary(BaseModel):
    id: int
    total_rows: int
    inserted: int
    updated: int
    errored: int
    status: str


class ImportJobListResponse(BaseModel):
    items: list[ImportJobOut]
    meta: PaginationMeta


class ScraperSyncRequest(BaseModel):
    records: list[dict] = Field(..., min_length=1)


class ScraperSyncResponse(BaseModel):
    id: int
    total_rows: int
    products_inserted: int
    products_updated: int
    matched_to_stock: int
    images_inserted: int
    images_updated: int
    errored: int
    status: str


class ProductDetailOut(BaseModel):
    product: ProductOut
    mappings: list[VendorMappingOut]
    attachments: list[ProductAttachmentOut]
    notes: list[ProductNoteOut]
    aliases: list[ProductAliasOut]
    images: list[ProductImageOut]
    documents: list[ProductDocumentOut]


class ProductMatchRequest(BaseModel):
    query_text: str | None = Field(default=None, max_length=500)
    vendor_name: str | None = Field(default=None, max_length=255)
    vendor_code: str | None = Field(default=None, max_length=50)
    vendor_sku: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=5, ge=1, le=20)

    @model_validator(mode="after")
    def validate_at_least_one_signal(self):
        if not any(
            value and value.strip()
            for value in (self.query_text, self.vendor_name, self.vendor_code, self.vendor_sku)
        ):
            raise ValueError("At least one matching signal is required")
        return self


class ProductMatchResult(BaseModel):
    product_id: int
    internal_sku: str
    normalized_name: str
    display_name: str | None = None
    canonical_name: str | None = None
    score: int
    confidence: str
    match_reasons: list[str]
    matched_vendor_name: str | None = None
    matched_vendor_code: str | None = None
    matched_vendor_sku: str | None = None
    matched_vendor_description: str | None = None
    matched_vendor_uom: str | None = None
    is_primary_vendor_mapping: bool | None = None


class ProductMatchResponse(BaseModel):
    matches: list[ProductMatchResult]


class DashboardSummary(BaseModel):
    total_active_products: int
    total_vendors: int
    products_with_attachments: int
    recent_import_jobs: list[ImportJobOut]


# ---------------------------------------------------------------------------
# Product Guide schemas
# ---------------------------------------------------------------------------

class GuideItemCreate(BaseModel):
    product_id: int
    section_name: str | None = None
    sort_order: int = 0
    override_description: str | None = None


class GuideItemOut(BaseModel):
    id: int
    product_id: int
    section_name: str | None = None
    sort_order: int = 0
    override_description: str | None = None
    # Flattened product fields for display
    internal_sku: str = ""
    normalized_name: str = ""
    display_name: str | None = None
    thickness: str | None = None
    width: str | None = None
    length: str | None = None
    species_or_material: str | None = None
    profile: str | None = None
    finish: str | None = None
    category_major: str | None = None
    category_minor: str | None = None
    primary_image_path: str | None = None

    class Config:
        from_attributes = True


class GuideCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class GuideUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    section_order: list[str] | None = None


class GuideOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    status: str = "draft"
    section_order: list[str] = []
    item_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class GuideDetailOut(BaseModel):
    guide: GuideOut
    items: list[GuideItemOut]


class GuideListResponse(BaseModel):
    items: list[GuideOut]
    meta: PaginationMeta


class GuideBulkReorderRequest(BaseModel):
    items: list[dict]  # [{"id": 1, "sort_order": 0, "section_name": "Casing"}, ...]
