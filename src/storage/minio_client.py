# src/storage/minio_client.py
from minio import Minio
from minio.error import S3Error
from src.config.settings import get_settings
from io import BytesIO
from datetime import timedelta

settings = get_settings()


class MinIOClient:
    """Client for MinIO/S3 operations."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            print(f"Error ensuring bucket: {e}")

    def upload(self, local_path: str, remote_path: str):
        """Upload local file."""
        self.client.fput_object(self.bucket, remote_path, local_path)

    def upload_bytes(self, data: bytes, remote_path: str):
        """Upload bytes."""
        self.client.put_object(
            self.bucket,
            remote_path,
            BytesIO(data),
            length=len(data)
        )

    def download(self, remote_path: str, local_path: str):
        """Download to local file."""
        self.client.fget_object(self.bucket, remote_path, local_path)

    def get_presigned_url(self, remote_path: str, expires: int = 3600) -> str:
        """Generate temporary download URL."""
        return self.client.presigned_get_object(
            self.bucket,
            remote_path,
            expires=timedelta(seconds=expires)
        )

    def delete(self, remote_path: str):
        """Delete file."""
        self.client.remove_object(self.bucket, remote_path)

    def delete_prefix(self, prefix: str):
        """Delete all files with given prefix."""
        objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
        for obj in objects:
            self.client.remove_object(self.bucket, obj.object_name)
