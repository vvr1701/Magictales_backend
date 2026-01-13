"""
Cloudflare R2 Storage Service
Handles image and PDF uploads, downloads, and signed URL generation.
"""

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import httpx
from typing import Optional
import structlog
from io import BytesIO

from app.config import get_settings
from app.core.exceptions import StorageError

logger = structlog.get_logger()


class StorageService:
    """
    Service for managing file storage in Cloudflare R2.

    Storage structure:
    - /uploads/{preview_id}/photo.jpg       # Original photos
    - /final/{preview_id}/page_XX.jpg       # High-res images
    - /previews/{preview_id}/page_XX.jpg    # Watermarked previews
    - /final/{preview_id}/book.pdf          # Generated PDFs
    """

    def __init__(self):
        self.settings = get_settings()
        self._s3_client = None

    @property
    def s3_client(self):
        """Lazy-load S3 client for R2."""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                's3',
                endpoint_url=self.settings.r2_endpoint_url,
                aws_access_key_id=self.settings.r2_access_key_id,
                aws_secret_access_key=self.settings.r2_secret_access_key,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
        return self._s3_client

    async def upload_image_from_buffer(
        self,
        image_buffer: BytesIO,
        path: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Upload image from BytesIO buffer to R2 and return public URL.

        Args:
            image_buffer: BytesIO buffer containing image data
            path: Path in bucket (e.g., "previews/preview_id/page_01.jpg")
            content_type: MIME type

        Returns:
            Public URL of uploaded image
        """
        # Convert BytesIO buffer to bytes
        image_buffer.seek(0)  # Ensure we're at the beginning
        image_bytes = image_buffer.read()

        # Use the existing upload_image method
        return await self.upload_image(image_bytes, path, content_type)

    async def upload_image(
        self,
        image_bytes: bytes,
        path: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Upload image to R2 and return public URL.

        Args:
            image_bytes: Image file content
            path: Path in bucket (e.g., "final/preview_id/page_01.jpg")
            content_type: MIME type

        Returns:
            Public URL of uploaded image
        """
        try:
            logger.info("Uploading image to R2", path=path, size_bytes=len(image_bytes))

            self.s3_client.put_object(
                Bucket=self.settings.r2_bucket_name,
                Key=path,
                Body=image_bytes,
                ContentType=content_type,
                CacheControl='public, max-age=31536000',  # Cache for 1 year
            )

            # Construct public URL
            public_url = f"{self.settings.r2_public_url}/{path}"

            logger.info("Image uploaded successfully", path=path, url=public_url)
            return public_url

        except ClientError as e:
            logger.error("Failed to upload image to R2", path=path, error=str(e))
            raise StorageError(f"Failed to upload image: {str(e)}")

    async def upload_pdf(
        self,
        pdf_bytes: bytes,
        path: str
    ) -> str:
        """
        Upload PDF to R2 and return public URL.

        Args:
            pdf_bytes: PDF file content
            path: Path in bucket (e.g., "final/preview_id/book.pdf")

        Returns:
            Public URL of uploaded PDF
        """
        try:
            logger.info("Uploading PDF to R2", path=path, size_bytes=len(pdf_bytes))

            self.s3_client.put_object(
                Bucket=self.settings.r2_bucket_name,
                Key=path,
                Body=pdf_bytes,
                ContentType='application/pdf',
                CacheControl='public, max-age=86400',  # Cache for 1 day
            )

            public_url = f"{self.settings.r2_public_url}/{path}"

            logger.info("PDF uploaded successfully", path=path, url=public_url)
            return public_url

        except ClientError as e:
            logger.error("Failed to upload PDF to R2", path=path, error=str(e))
            raise StorageError(f"Failed to upload PDF: {str(e)}")

    def generate_signed_url(
        self,
        path: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate time-limited signed URL for downloading files.

        Args:
            path: Path in bucket
            expires_in: Expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL
        """
        try:
            logger.info("Generating signed URL", path=path, expires_in=expires_in)

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.settings.r2_bucket_name,
                    'Key': path
                },
                ExpiresIn=expires_in
            )

            logger.info("Signed URL generated", path=path)
            return url

        except ClientError as e:
            logger.error("Failed to generate signed URL", path=path, error=str(e))
            raise StorageError(f"Failed to generate signed URL: {str(e)}")

    async def download_image(self, url: str) -> bytes:
        """
        Download image from URL.

        Args:
            url: Image URL (can be from R2 or external like Fal.ai)

        Returns:
            Image bytes
        """
        try:
            logger.info("Downloading image", url=url[:100] if url else None)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                image_bytes = response.content
                logger.info("Image downloaded", url=url[:100] if url else None, size_bytes=len(image_bytes))
                return image_bytes

        except httpx.HTTPError as e:
            logger.error("Failed to download image", url=url[:100] if url else None, error=str(e))
            raise StorageError(f"Failed to download image: {str(e)}")

    async def download_and_upload(
        self,
        source_url: str,
        dest_path: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Download image from URL and upload to R2.

        Useful for saving AI-generated images from external services.

        Args:
            source_url: URL to download from
            dest_path: Destination path in R2
            content_type: MIME type

        Returns:
            Public URL of uploaded image
        """
        if not source_url:
            raise StorageError("Cannot download image: source_url is None or empty")

        image_bytes = await self.download_image(source_url)
        return await self.upload_image(image_bytes, dest_path, content_type)

    async def delete_file(self, path: str) -> None:
        """
        Delete a single file from R2.

        Args:
            path: Path in bucket
        """
        try:
            logger.info("Deleting file from R2", path=path)

            self.s3_client.delete_object(
                Bucket=self.settings.r2_bucket_name,
                Key=path
            )

            logger.info("File deleted successfully", path=path)

        except ClientError as e:
            logger.error("Failed to delete file from R2", path=path, error=str(e))
            raise StorageError(f"Failed to delete file: {str(e)}")

    async def delete_folder(self, path_prefix: str) -> int:
        """
        Delete all objects under a path prefix (folder).

        Args:
            path_prefix: Path prefix (e.g., "previews/preview_id/")

        Returns:
            Number of objects deleted
        """
        try:
            logger.info("Deleting folder from R2", path_prefix=path_prefix)

            # List all objects with the prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=self.settings.r2_bucket_name,
                Prefix=path_prefix
            )

            delete_count = 0

            for page in pages:
                if 'Contents' not in page:
                    continue

                # Prepare objects for batch deletion
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]

                # Delete batch
                self.s3_client.delete_objects(
                    Bucket=self.settings.r2_bucket_name,
                    Delete={'Objects': objects_to_delete}
                )

                delete_count += len(objects_to_delete)

            logger.info("Folder deleted successfully", path_prefix=path_prefix, count=delete_count)
            return delete_count

        except ClientError as e:
            logger.error("Failed to delete folder from R2", path_prefix=path_prefix, error=str(e))
            raise StorageError(f"Failed to delete folder: {str(e)}")

    async def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in R2.

        Args:
            path: Path in bucket

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.settings.r2_bucket_name,
                Key=path
            )
            return True
        except ClientError:
            return False

    async def get_file_size(self, path: str) -> int:
        """
        Get file size in bytes.

        Args:
            path: Path in bucket

        Returns:
            File size in bytes
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.settings.r2_bucket_name,
                Key=path
            )
            return response['ContentLength']
        except ClientError as e:
            logger.error("Failed to get file size", path=path, error=str(e))
            raise StorageError(f"Failed to get file size: {str(e)}")
