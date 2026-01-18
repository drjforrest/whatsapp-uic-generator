"""
QR Code Generation Service.

Handles generation and management of QR codes for UICs.
"""
import io
import os
from pathlib import Path
from typing import Optional

import qrcode
from qrcode.image.pil import PilImage

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class QRCodeService:
    """Service for generating QR codes from UICs."""

    def __init__(self, output_dir: str = "static/qr_codes"):
        """
        Initialize QR code service.

        Args:
            output_dir: Directory to save QR code images
        """
        self.output_dir = Path(output_dir)
        self._ensure_output_dir()
        logger.info("QRCodeService initialized", output_dir=str(self.output_dir))

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("QR code output directory ready", path=str(self.output_dir))

    def generate_qr_code(
        self,
        uic_code: str,
        save_to_disk: bool = True
    ) -> tuple[Path, bytes]:
        """
        Generate QR code for a UIC.

        Args:
            uic_code: The UIC string to encode
            save_to_disk: Whether to save the image to disk

        Returns:
            Tuple of (file_path, image_bytes)
        """
        logger.info("Generating QR code", uic_code=uic_code)

        # Create QR code
        qr = qrcode.QRCode(
            version=1,  # Auto-size based on data
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )

        qr.add_data(uic_code)
        qr.make(fit=True)

        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Save to disk if requested
        file_path = self.output_dir / f"{uic_code}.png"
        if save_to_disk:
            with open(file_path, 'wb') as f:
                f.write(img_bytes)
            logger.info("QR code saved", path=str(file_path), size_bytes=len(img_bytes))

        return file_path, img_bytes

    def get_qr_code_path(self, uic_code: str) -> Optional[Path]:
        """
        Get path to existing QR code file.

        Args:
            uic_code: The UIC to look up

        Returns:
            Path to QR code file if it exists, None otherwise
        """
        file_path = self.output_dir / f"{uic_code}.png"
        if file_path.exists():
            logger.debug("Found existing QR code", path=str(file_path))
            return file_path
        return None

    def delete_qr_code(self, uic_code: str) -> bool:
        """
        Delete a QR code file.

        Args:
            uic_code: The UIC whose QR code to delete

        Returns:
            True if file was deleted, False if it didn't exist
        """
        file_path = self.output_dir / f"{uic_code}.png"
        if file_path.exists():
            file_path.unlink()
            logger.info("QR code deleted", uic_code=uic_code)
            return True
        return False

    def cleanup_old_qr_codes(self, max_age_days: int = 7) -> int:
        """
        Delete QR codes older than specified days.

        Args:
            max_age_days: Maximum age in days before deletion

        Returns:
            Number of files deleted
        """
        import time
        from datetime import datetime, timedelta

        cutoff_time = time.time() - (max_age_days * 86400)
        deleted_count = 0

        for qr_file in self.output_dir.glob("*.png"):
            if qr_file.stat().st_mtime < cutoff_time:
                qr_file.unlink()
                deleted_count += 1

        if deleted_count > 0:
            logger.info(
                "Cleaned up old QR codes",
                deleted_count=deleted_count,
                max_age_days=max_age_days
            )

        return deleted_count
