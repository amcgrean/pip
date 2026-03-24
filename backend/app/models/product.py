from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internal_sku: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    product_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_major: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_minor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    species_or_material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    thickness: Mapped[str | None] = mapped_column(String(50), nullable=True)
    width: Mapped[str | None] = mapped_column(String(50), nullable=True)
    length: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit_of_measure: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    branch_scope: Mapped[str | None] = mapped_column(String(100), nullable=True)

    mappings = relationship("VendorProductMapping", back_populates="product", cascade="all,delete")
    attachments = relationship("ProductAttachment", back_populates="product", cascade="all,delete")
    notes = relationship("ProductNote", back_populates="product", cascade="all,delete")
