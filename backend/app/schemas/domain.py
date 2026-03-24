from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


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


class ProductDetailOut(BaseModel):
    product: ProductOut
    mappings: list[VendorMappingOut]
    attachments: list[ProductAttachmentOut]
    notes: list[ProductNoteOut]


class DashboardSummary(BaseModel):
    total_active_products: int
    total_vendors: int
    products_with_attachments: int
    recent_import_jobs: list[ImportJobOut]
