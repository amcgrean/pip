"""product matching indexes

Revision ID: 20260324_0003
Revises: 20260324_0002
Create Date: 2026-03-24 01:15:00

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260324_0003"
down_revision = "20260324_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_product_aliases_alias_text", "product_aliases", ["alias_text"], unique=False)
    op.create_index(
        "ix_vendor_product_mappings_vendor_id_vendor_sku",
        "vendor_product_mappings",
        ["vendor_id", "vendor_sku"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_vendor_product_mappings_vendor_id_vendor_sku", table_name="vendor_product_mappings")
    op.drop_index("ix_product_aliases_alias_text", table_name="product_aliases")
