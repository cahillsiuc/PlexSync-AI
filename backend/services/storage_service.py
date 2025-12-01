"""
File Storage Service
Handles invoice file storage (local or cloud)
"""
from pathlib import Path
from typing import Optional
import shutil
import uuid
from config import settings
from loguru import logger


class StorageService:
    """
    Handles file storage for invoices
    Supports local storage (can be extended for S3, etc.)
    """

    def __init__(self):
        self.storage_path = Path(settings.storage_path)
        self.storage_type = settings.storage_type
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024
        self.allowed_types = settings.allowed_file_types

        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_file(
        self,
        file_content: bytes,
        file_name: str,
        invoice_id: Optional[int] = None
    ) -> str:
        """
        Save uploaded file

        Args:
            file_content: File content as bytes
            file_name: Original file name
            invoice_id: Optional invoice ID for organization

        Returns:
            Path to saved file
        """
        # Validate file
        self._validate_file(file_content, file_name)

        # Generate unique filename
        file_ext = Path(file_name).suffix.lower()
        unique_name = f"{uuid.uuid4()}{file_ext}"

        # Organize by invoice ID if provided
        if invoice_id:
            invoice_dir = self.storage_path / str(invoice_id)
            invoice_dir.mkdir(exist_ok=True)
            file_path = invoice_dir / unique_name
        else:
            file_path = self.storage_path / unique_name

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"Saved file: {file_path}")
        return str(file_path)

    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content

        Args:
            file_path: Path to file

        Returns:
            File content or None if not found
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        with open(path, "rb") as f:
            return f.read()

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file

        Args:
            file_path: Path to file

        Returns:
            True if deleted, False otherwise
        """
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
        return False

    def _validate_file(self, file_content: bytes, file_name: str):
        """Validate file before saving"""
        # Check file size
        if len(file_content) > self.max_file_size:
            raise ValueError(
                f"File size {len(file_content)} exceeds maximum {self.max_file_size}"
            )

        # Check file type
        file_ext = Path(file_name).suffix.lower().replace(".", "")
        if file_ext not in self.allowed_types:
            raise ValueError(
                f"File type {file_ext} not allowed. Allowed: {self.allowed_types}"
            )


# Singleton instance
storage_service = StorageService()

