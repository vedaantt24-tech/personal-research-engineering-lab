from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from app.core.config import settings

class StorageError(RuntimeError):
    pass

class LocalStorage:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: bytes, content_type: str | None = None) -> str:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def delete(self, key: str) -> None:
        path = self.root / key
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def path(self, key: str) -> Path:
        return self.root / key

class S3Storage:
    def __init__(self):
        try:
            import boto3
        except ImportError as exc:
            raise StorageError("S3 storage requires boto3") from exc
        bucket = settings.s3_bucket_name
        access_key = settings.s3_access_key_id
        secret_key = settings.s3_secret_access_key
        if not settings.s3_endpoint_url or not bucket or not access_key or not secret_key:
            raise StorageError("S3_ENDPOINT_URL, S3_BUCKET_NAME, S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY are required when STORAGE_DRIVER=s3")
        self.client = boto3.client(
            "s3", region_name=settings.s3_region, endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=access_key, aws_secret_access_key=secret_key,
        )
        self.bucket = bucket

    def save(self, key: str, data: bytes, content_type: str | None = None) -> str:
        args = {"Bucket": self.bucket, "Key": key, "Body": data}
        if content_type:
            args["ContentType"] = content_type
        self.client.put_object(**args)
        return key

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def public_url(self, key: str) -> str:
        return self.client.generate_presigned_url("get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=900)


def get_storage():
    if settings.storage_driver.lower() == "s3":
        return S3Storage()
    return LocalStorage(settings.media_root)
