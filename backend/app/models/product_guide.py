from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class ProductGuide(TimestampMixin, Base):
    __tablename__ = "pip_product_guides"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    cover_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    section_order: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array: ["Casing","Base","Crown"]
    created_by: Mapped[int | None] = mapped_column(ForeignKey("pip_users.id"), nullable=True)

    items: Mapped[list["ProductGuideItem"]] = relationship(
        "ProductGuideItem",
        back_populates="guide",
        cascade="all,delete-orphan",
        order_by="ProductGuideItem.sort_order",
    )


class ProductGuideItem(TimestampMixin, Base):
    __tablename__ = "pip_product_guide_items"
    __table_args__ = (
        UniqueConstraint("guide_id", "product_id", name="uq_pip_guide_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    guide_id: Mapped[int] = mapped_column(
        ForeignKey("pip_product_guides.id", ondelete="CASCADE"), index=True, nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("pip_products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    section_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    override_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    guide: Mapped["ProductGuide"] = relationship("ProductGuide", back_populates="items")
    product = relationship("Product", back_populates="guide_items")
