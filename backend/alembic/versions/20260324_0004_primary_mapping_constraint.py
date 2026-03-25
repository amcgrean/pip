"""enforce single primary mapping per product

Revision ID: 20260324_0004
Revises: 20260324_0003
Create Date: 2026-03-24 03:30:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260324_0004"
down_revision = "20260324_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_vendor_product_mappings_one_primary_per_product",
        "vendor_product_mappings",
        ["product_id"],
        unique=True,
        postgresql_where=sa.text("is_primary = true"),
    )


def downgrade() -> None:
    op.drop_index("uq_vendor_product_mappings_one_primary_per_product", table_name="vendor_product_mappings")
