from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class VendorProductMapping(TimestampMixin, Base):
    __tablename__ = "vendor_product_mappings"
    __table_args__ = (
        UniqueConstraint("vendor_id", "product_id", "vendor_sku", name="uq_vendor_product_sku"),
        Index("ix_vendor_product_mappings_vendor_id_vendor_sku", "vendor_id", "vendor_sku"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    vendor_sku: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    vendor_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vendor_uom: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    vendor = relationship("Vendor", back_populates="mappings")
    product = relationship("Product", back_populates="mappings")
