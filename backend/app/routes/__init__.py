from fastapi import APIRouter

from app.routes import attachments, auth, health, imports, mappings, notes, products, users, vendors

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(vendors.router)
api_router.include_router(products.router)
api_router.include_router(mappings.router)
api_router.include_router(attachments.router)
api_router.include_router(notes.router)
api_router.include_router(imports.router)
