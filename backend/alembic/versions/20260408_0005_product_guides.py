"""add product_guides and product_guide_items tables

Revision ID: 20260408_0005
Revises: 20260324_0004
Create Date: 2026-04-08 12:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260408_0005"
down_revision = "20260324_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_guides",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("cover_image_path", sa.String(500), nullable=True),
        sa.Column("section_order", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_product_guides_id", "product_guides", ["id"])

    op.create_table(
        "product_guide_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("guide_id", sa.Integer(), sa.ForeignKey("product_guides.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section_name", sa.String(100), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("override_description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("guide_id", "product_id", name="uq_guide_product"),
    )
    op.create_index("ix_product_guide_items_id", "product_guide_items", ["id"])
    op.create_index("ix_product_guide_items_guide_id", "product_guide_items", ["guide_id"])
    op.create_index("ix_product_guide_items_product_id", "product_guide_items", ["product_id"])


def downgrade() -> None:
    op.drop_table("product_guide_items")
    op.drop_table("product_guides")
