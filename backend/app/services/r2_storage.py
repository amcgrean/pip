"""Cloudflare R2 object storage service.

Provides upload/download/delete for product images and attachments.
Falls back to local disk when R2 is not configured.
"""

import io
import logging
from pathlib import Path

import boto3
from botocore.config import Config

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_r2_client():
    """Lazy-init the S3-compatible R2 client."""
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
    return _client


def upload_file(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Upload a file to R2 (or local disk fallback).

    Returns the public URL or local path.
    """
    if settings.r2_enabled:
        client = _get_r2_client()
        client.put_object(
            Bucket=settings.r2_bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        logger.info("Uploaded to R2: %s (%d bytes)", key, len(data))
        if settings.r2_public_url:
            return f"{settings.r2_public_url.rstrip('/')}/{key}"
        return f"r2://{settings.r2_bucket_name}/{key}"

    # Local fallback
    local_path = Path(settings.local_storage_dir) / key
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(data)
    logger.info("Saved locally: %s (%d bytes)", local_path, len(data))
    return str(local_path)


def download_file(key: str) -> bytes | None:
    """Download a file from R2 (or local disk fallback)."""
    if settings.r2_enabled:
        try:
            client = _get_r2_client()
            response = client.get_object(Bucket=settings.r2_bucket_name, Key=key)
            return response["Body"].read()
        except Exception:
            logger.warning("Failed to download from R2: %s", key)
            return None

    local_path = Path(settings.local_storage_dir) / key
    if local_path.exists():
        return local_path.read_bytes()
    return None


def delete_file(key: str) -> bool:
    """Delete a file from R2 (or local disk fallback)."""
    if settings.r2_enabled:
        try:
            client = _get_r2_client()
            client.delete_object(Bucket=settings.r2_bucket_name, Key=key)
            logger.info("Deleted from R2: %s", key)
            return True
        except Exception:
            logger.warning("Failed to delete from R2: %s", key)
            return False

    local_path = Path(settings.local_storage_dir) / key
    if local_path.exists():
        local_path.unlink()
        return True
    return False


def get_public_url(key: str) -> str:
    """Get the public URL for a stored file."""
    if settings.r2_enabled and settings.r2_public_url:
        return f"{settings.r2_public_url.rstrip('/')}/{key}"
    return f"/api/v1/attachments/files/{key}"
