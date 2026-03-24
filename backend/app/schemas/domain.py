from datetime import datetime

from pydantic import BaseModel


class VendorOut(BaseModel):
    id: int
    vendor_code: str
    vendor_name: str
    is_active: bool

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    internal_sku: str
    normalized_name: str
    status: str
    branch_scope: str | None

    class Config:
        from_attributes = True


class ImportJobOut(BaseModel):
    id: int
    source_type: str
    file_name: str
    status: str
    total_rows: int
    created_at: datetime

    class Config:
        from_attributes = True
