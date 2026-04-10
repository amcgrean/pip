from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class Vendor(TimestampMixin, Base):
    __tablename__ = "pip_vendors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vendor_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    mappings = relationship("VendorProductMapping", back_populates="vendor", cascade="all,delete")
