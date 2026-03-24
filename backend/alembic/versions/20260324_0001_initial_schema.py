"""initial schema

Revision ID: 20260324_0001
Revises: 
Create Date: 2026-03-24 00:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260324_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor_code", sa.String(length=50), nullable=False),
        sa.Column("vendor_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vendors_id"), "vendors", ["id"], unique=False)
    op.create_index(op.f("ix_vendors_vendor_code"), "vendors", ["vendor_code"], unique=True)
    op.create_index(op.f("ix_vendors_vendor_name"), "vendors", ["vendor_name"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("internal_sku", sa.String(length=80), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("product_type", sa.String(length=100), nullable=True),
        sa.Column("category_major", sa.String(length=100), nullable=True),
        sa.Column("category_minor", sa.String(length=100), nullable=True),
        sa.Column("species_or_material", sa.String(length=100), nullable=True),
        sa.Column("grade", sa.String(length=100), nullable=True),
        sa.Column("thickness", sa.String(length=50), nullable=True),
        sa.Column("width", sa.String(length=50), nullable=True),
        sa.Column("length", sa.String(length=50), nullable=True),
        sa.Column("unit_of_measure", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("branch_scope", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_internal_sku"), "products", ["internal_sku"], unique=True)
    op.create_index(op.f("ix_products_normalized_name"), "products", ["normalized_name"], unique=False)

    op.create_table(
        "import_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("inserted_rows", sa.Integer(), nullable=False),
        sa.Column("updated_rows", sa.Integer(), nullable=False),
        sa.Column("error_rows", sa.Integer(), nullable=False),
        sa.Column("error_log", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_import_jobs_id"), "import_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_import_jobs_status"), "import_jobs", ["status"], unique=False)

    op.create_table(
        "product_attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_attachments_id"), "product_attachments", ["id"], unique=False)
    op.create_index(op.f("ix_product_attachments_product_id"), "product_attachments", ["product_id"], unique=False)

    op.create_table(
        "product_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("note_text", sa.Text(), nullable=False),
        sa.Column("note_type", sa.String(length=50), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_notes_id"), "product_notes", ["id"], unique=False)
    op.create_index(op.f("ix_product_notes_product_id"), "product_notes", ["product_id"], unique=False)

    op.create_table(
        "vendor_product_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("vendor_sku", sa.String(length=100), nullable=False),
        sa.Column("vendor_description", sa.String(length=255), nullable=True),
        sa.Column("vendor_uom", sa.String(length=50), nullable=True),
        sa.Column("last_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vendor_id", "product_id", "vendor_sku", name="uq_vendor_product_sku"),
    )
    op.create_index(op.f("ix_vendor_product_mappings_id"), "vendor_product_mappings", ["id"], unique=False)
    op.create_index(op.f("ix_vendor_product_mappings_product_id"), "vendor_product_mappings", ["product_id"], unique=False)
    op.create_index(op.f("ix_vendor_product_mappings_vendor_id"), "vendor_product_mappings", ["vendor_id"], unique=False)
    op.create_index(op.f("ix_vendor_product_mappings_vendor_sku"), "vendor_product_mappings", ["vendor_sku"], unique=False)


def downgrade() -> None:
    op.drop_table("vendor_product_mappings")
    op.drop_table("product_notes")
    op.drop_table("product_attachments")
    op.drop_table("import_jobs")
    op.drop_table("products")
    op.drop_table("vendors")
    op.drop_table("users")
