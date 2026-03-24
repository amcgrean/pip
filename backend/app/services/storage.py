import re
from pathlib import Path
from uuid import uuid4

from app.core.config import settings

SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


class LocalStorageService:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        name = Path(filename).name.strip()
        cleaned = SAFE_FILENAME_RE.sub("_", name)
        return cleaned[:200] or "attachment"

    def save_product_attachment(self, product_id: int, filename: str, content: bytes) -> tuple[str, str]:
        safe_name = self.sanitize_filename(filename)
        target_dir = self.root / "products" / str(product_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / f"{uuid4().hex}_{safe_name}"
        dest.write_bytes(content)
        relative = dest.relative_to(self.root)
        return str(dest), str(relative)


storage_service = LocalStorageService(settings.local_storage_dir)
