from sqlalchemy import Boolean, Date, Float, Integer, String, Text
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

    canonical_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extended_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    finish: Mapped[str | None] = mapped_column(String(100), nullable=True)
    treatment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile: Mapped[str | None] = mapped_column(String(100), nullable=True)
    thickness_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    width_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    length_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    search_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    master_search_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_sold_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_stock_item: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    match_priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_system_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    mappings = relationship("VendorProductMapping", back_populates="product", cascade="all,delete")
    attachments = relationship("ProductAttachment", back_populates="product", cascade="all,delete")
    notes = relationship("ProductNote", back_populates="product", cascade="all,delete")
    aliases = relationship("ProductAlias", back_populates="product", cascade="all,delete")
    images = relationship("ProductImage", back_populates="product", cascade="all,delete")
    documents = relationship("ProductDocument", back_populates="product", cascade="all,delete")
