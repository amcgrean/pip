"""PDF generation for Product Guides using ReportLab."""

import io
import json
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.product import Product
from app.models.product_guide import ProductGuide, ProductGuideItem
from app.models.product_image import ProductImage

# Beisser brand colors
BEISSER_BLUE = colors.HexColor("#1565C0")
BEISSER_DARK = colors.HexColor("#1a1a2e")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
BORDER_GRAY = colors.HexColor("#e0e0e0")
TEXT_DARK = colors.HexColor("#212121")
TEXT_SECONDARY = colors.HexColor("#757575")


def _get_styles():
    """Build custom paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontSize=32,
        leading=38,
        textColor=BEISSER_DARK,
        alignment=TA_CENTER,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        leading=18,
        textColor=TEXT_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading1"],
        fontSize=20,
        leading=26,
        textColor=colors.white,
        spaceBefore=0,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "ProductName",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
    ))
    styles.add(ParagraphStyle(
        "ProductDetail",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=TEXT_SECONDARY,
    ))
    styles.add(ParagraphStyle(
        "SKU",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        fontName="Courier",
        textColor=BEISSER_BLUE,
    ))
    styles.add(ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontSize=7,
        textColor=TEXT_SECONDARY,
        alignment=TA_CENTER,
    ))
    return styles


def _resolve_image_path(storage_path: str | None) -> str | None:
    """Resolve a product image's storage_path to an absolute file path."""
    if not storage_path:
        return None
    # storage_path might be a URL or a relative path
    if storage_path.startswith(("http://", "https://")):
        return None  # Can't embed URLs directly; would need to download
    base_dir = Path(settings.local_storage_dir)
    full_path = base_dir / storage_path
    if full_path.exists():
        return str(full_path)
    # Try just the path as-is
    if Path(storage_path).exists():
        return storage_path
    return None


def _build_cover_page(story, guide_name: str, guide_description: str | None, styles):
    """Add a cover page to the story."""
    story.append(Spacer(1, 2 * inch))

    # Company name
    story.append(Paragraph("BEISSER LUMBER", styles["CoverSubtitle"]))
    story.append(Spacer(1, 8))

    # Guide title
    story.append(Paragraph(guide_name, styles["CoverTitle"]))

    if guide_description:
        story.append(Spacer(1, 12))
        story.append(Paragraph(guide_description, styles["CoverSubtitle"]))

    story.append(Spacer(1, 1.5 * inch))

    # Decorative line
    line_table = Table([[""]],  colWidths=[4 * inch])
    line_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 2, BEISSER_BLUE),
    ]))
    story.append(line_table)

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Product Reference Guide", styles["CoverSubtitle"]))
    story.append(PageBreak())


def _build_section_header(section_name: str, styles):
    """Create a styled section header banner."""
    header_table = Table(
        [[Paragraph(section_name.upper(), styles["SectionHeader"])]],
        colWidths=[7.3 * inch],
        rowHeights=[0.5 * inch],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BEISSER_BLUE),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROUNDEDCORNERS", [4, 4, 0, 0]),
    ]))
    return header_table


def _build_product_table(items: list, styles) -> Table | None:
    """Build a table of products for a section."""
    if not items:
        return None

    # Table header
    header_row = [
        Paragraph("<b>Image</b>", styles["ProductDetail"]),
        Paragraph("<b>SKU</b>", styles["ProductDetail"]),
        Paragraph("<b>Product</b>", styles["ProductDetail"]),
        Paragraph("<b>Species / Material</b>", styles["ProductDetail"]),
        Paragraph("<b>Dimensions</b>", styles["ProductDetail"]),
        Paragraph("<b>Profile / Finish</b>", styles["ProductDetail"]),
    ]

    data = [header_row]

    for item in items:
        # Try to load image
        img_cell = ""
        image_path = _resolve_image_path(item.get("primary_image_path"))
        if image_path:
            try:
                img_cell = Image(image_path, width=0.6 * inch, height=0.6 * inch)
                img_cell.hAlign = "CENTER"
            except Exception:
                img_cell = ""

        # Build dimension string
        dims = []
        if item.get("thickness"):
            dims.append(item["thickness"])
        if item.get("width"):
            dims.append(item["width"])
        if item.get("length"):
            dims.append(item["length"])
        dim_str = " x ".join(dims) if dims else "-"

        # Profile / Finish
        pf_parts = []
        if item.get("profile"):
            pf_parts.append(item["profile"])
        if item.get("finish"):
            pf_parts.append(item["finish"])
        pf_str = " / ".join(pf_parts) if pf_parts else "-"

        # Product name - use override or normalized_name
        product_name = item.get("override_description") or item.get("normalized_name") or "-"

        row = [
            img_cell,
            Paragraph(item.get("internal_sku", ""), styles["SKU"]),
            Paragraph(product_name, styles["ProductName"]),
            Paragraph(item.get("species_or_material") or "-", styles["ProductDetail"]),
            Paragraph(dim_str, styles["ProductDetail"]),
            Paragraph(pf_str, styles["ProductDetail"]),
        ]
        data.append(row)

    col_widths = [0.8 * inch, 1.0 * inch, 2.0 * inch, 1.2 * inch, 1.1 * inch, 1.2 * inch]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        # All cells
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("LINEBELOW", (0, 0), (-1, 0), 1, BEISSER_BLUE),
    ]

    # Alternate row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#fafafa")))

    table.setStyle(TableStyle(style_commands))
    return table


def generate_guide_pdf(db: Session, guide_id: int) -> bytes | None:
    """Generate a PDF for a product guide. Returns bytes or None if guide not found."""
    guide = db.query(ProductGuide).filter(ProductGuide.id == guide_id).first()
    if not guide:
        return None

    # Load items with products and images
    items = (
        db.query(ProductGuideItem)
        .options(joinedload(ProductGuideItem.product).joinedload(Product.images))
        .filter(ProductGuideItem.guide_id == guide_id)
        .order_by(ProductGuideItem.sort_order)
        .all()
    )

    # Parse section order
    section_order = []
    if guide.section_order:
        try:
            section_order = json.loads(guide.section_order)
        except (json.JSONDecodeError, TypeError):
            pass

    # Build items lookup by section
    sections: dict[str, list[dict]] = {}
    unsectioned: list[dict] = []

    for item in items:
        p = item.product
        primary_image = None
        if p and p.images:
            sorted_imgs = sorted(p.images, key=lambda i: i.sort_order)
            primary_image = sorted_imgs[0].storage_path if sorted_imgs else None

        item_data = {
            "id": item.id,
            "product_id": item.product_id,
            "section_name": item.section_name,
            "sort_order": item.sort_order,
            "override_description": item.override_description,
            "internal_sku": p.internal_sku if p else "",
            "normalized_name": p.normalized_name if p else "",
            "display_name": p.display_name if p else None,
            "thickness": p.thickness if p else None,
            "width": p.width if p else None,
            "length": p.length if p else None,
            "species_or_material": p.species_or_material if p else None,
            "profile": p.profile if p else None,
            "finish": p.finish if p else None,
            "primary_image_path": primary_image,
        }

        section = item.section_name or ""
        if section:
            sections.setdefault(section, []).append(item_data)
        else:
            unsectioned.append(item_data)

    # Build PDF
    buffer = io.BytesIO()
    styles = _get_styles()

    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(TEXT_SECONDARY)
        canvas.drawCentredString(
            letter[0] / 2,
            0.5 * inch,
            f"{guide.name}  |  Page {doc.page}",
        )
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    story: list = []

    # Cover page
    _build_cover_page(story, guide.name, guide.description, styles)

    # Sections in order
    ordered_sections = []
    for s in section_order:
        if s in sections:
            ordered_sections.append(s)
    # Add any sections not in the explicit order
    for s in sections:
        if s not in ordered_sections:
            ordered_sections.append(s)

    for section_name in ordered_sections:
        section_items = sections[section_name]
        story.append(_build_section_header(section_name, styles))
        story.append(Spacer(1, 8))

        table = _build_product_table(section_items, styles)
        if table:
            story.append(table)
        story.append(Spacer(1, 20))

    # Unsectioned items
    if unsectioned:
        story.append(_build_section_header("Other Products", styles))
        story.append(Spacer(1, 8))
        table = _build_product_table(unsectioned, styles)
        if table:
            story.append(table)

    # Handle empty guide
    if not items:
        story.append(Spacer(1, 1 * inch))
        story.append(Paragraph(
            "No products have been added to this guide yet.",
            styles["CoverSubtitle"],
        ))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
