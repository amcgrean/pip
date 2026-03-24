from sqlalchemy.orm import Session

from app.models.product_alias import ProductAlias
from app.models.product_document import ProductDocument
from app.models.product_image import ProductImage


def list_aliases_for_product(db: Session, product_id: int):
    return (
        db.query(ProductAlias)
        .filter(ProductAlias.product_id == product_id)
        .order_by(ProductAlias.is_preferred.desc(), ProductAlias.alias_text.asc())
        .all()
    )


def list_images_for_product(db: Session, product_id: int):
    return (
        db.query(ProductImage)
        .filter(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order.asc(), ProductImage.id.asc())
        .all()
    )


def list_documents_for_product(db: Session, product_id: int):
    return (
        db.query(ProductDocument)
        .filter(ProductDocument.product_id == product_id)
        .order_by(ProductDocument.document_type.asc(), ProductDocument.title.asc())
        .all()
    )
