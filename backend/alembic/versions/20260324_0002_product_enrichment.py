"""product enrichment schema

Revision ID: 20260324_0002
Revises: 20260324_0001
Create Date: 2026-03-24 00:30:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260324_0002"
down_revision = "20260324_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("canonical_name", sa.String(length=255), nullable=True))
    op.add_column("products", sa.Column("display_name", sa.String(length=255), nullable=True))
    op.add_column("products", sa.Column("extended_description", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("category", sa.String(length=100), nullable=True))
    op.add_column("products", sa.Column("subcategory", sa.String(length=100), nullable=True))
    op.add_column("products", sa.Column("finish", sa.String(length=100), nullable=True))
    op.add_column("products", sa.Column("treatment", sa.String(length=100), nullable=True))
    op.add_column("products", sa.Column("profile", sa.String(length=100), nullable=True))
    op.add_column("products", sa.Column("thickness_numeric", sa.Float(), nullable=True))
    op.add_column("products", sa.Column("width_numeric", sa.Float(), nullable=True))
    op.add_column("products", sa.Column("length_numeric", sa.Float(), nullable=True))
    op.add_column("products", sa.Column("keywords", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("search_text", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("master_search_text", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("last_sold_date", sa.Date(), nullable=True))
    op.add_column("products", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("products", sa.Column("is_stock_item", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("products", sa.Column("match_priority", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("source_system_id", sa.String(length=100), nullable=True))

    op.create_table(
        "product_aliases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("alias_text", sa.String(length=255), nullable=False),
        sa.Column("alias_type", sa.String(length=50), nullable=True),
        sa.Column("is_preferred", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "alias_text", name="uq_product_alias_product_text"),
    )
    op.create_index(op.f("ix_product_aliases_id"), "product_aliases", ["id"], unique=False)
    op.create_index(op.f("ix_product_aliases_product_id"), "product_aliases", ["product_id"], unique=False)

    op.create_table(
        "product_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("image_type", sa.String(length=50), nullable=True),
        sa.Column("alt_text", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "storage_path", name="uq_product_image_product_path"),
    )
    op.create_index(op.f("ix_product_images_id"), "product_images", ["id"], unique=False)
    op.create_index(op.f("ix_product_images_product_id"), "product_images", ["product_id"], unique=False)

    op.create_table(
        "product_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=True),
        sa.Column("attachment_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["attachment_id"], ["product_attachments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "document_type", "title", name="uq_product_document_identity"),
    )
    op.create_index(op.f("ix_product_documents_id"), "product_documents", ["id"], unique=False)
    op.create_index(op.f("ix_product_documents_product_id"), "product_documents", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_table("product_documents")
    op.drop_table("product_images")
    op.drop_table("product_aliases")

    op.drop_column("products", "source_system_id")
    op.drop_column("products", "match_priority")
    op.drop_column("products", "is_stock_item")
    op.drop_column("products", "is_active")
    op.drop_column("products", "last_sold_date")
    op.drop_column("products", "master_search_text")
    op.drop_column("products", "search_text")
    op.drop_column("products", "keywords")
    op.drop_column("products", "length_numeric")
    op.drop_column("products", "width_numeric")
    op.drop_column("products", "thickness_numeric")
    op.drop_column("products", "profile")
    op.drop_column("products", "treatment")
    op.drop_column("products", "finish")
    op.drop_column("products", "subcategory")
    op.drop_column("products", "category")
    op.drop_column("products", "extended_description")
    op.drop_column("products", "display_name")
    op.drop_column("products", "canonical_name")
