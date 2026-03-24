from pathlib import Path
from uuid import uuid4

from app.core.config import settings


class LocalStorageService:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_product_attachment(self, product_id: int, filename: str, content: bytes) -> str:
        safe_name = filename.replace("/", "_").replace("..", "_")
        target_dir = self.root / "products" / str(product_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / f"{uuid4().hex}_{safe_name}"
        dest.write_bytes(content)
        return str(dest)


storage_service = LocalStorageService(settings.local_storage_dir)
