"""
Quick test for QR code generation.

Run with: python tests/test_qr_service.py
"""
from app.services.qr_service import QRCodeService


def test_qr_generation():
    """Test basic QR code generation."""
    service = QRCodeService(output_dir="static/qr_codes")
    
    # Generate a test QR code
    uic_code = "MBEIBR7DA1"
    file_path, img_bytes = service.generate_qr_code(uic_code)
    
    print(f"✅ QR code generated successfully!")
    print(f"   File: {file_path}")
    print(f"   Size: {len(img_bytes)} bytes")
    
    # Verify file exists
    assert file_path.exists(), "QR code file was not created"
    assert len(img_bytes) > 0, "QR code image has no data"
    
    print(f"✅ QR code file verified at: {file_path}")
    
    # Test retrieval
    retrieved_path = service.get_qr_code_path(uic_code)
    assert retrieved_path == file_path, "Retrieved path doesn't match"
    
    print(f"✅ QR code retrieval works correctly")
    
    # Clean up test file
    deleted = service.delete_qr_code(uic_code)
    assert deleted, "Failed to delete QR code"
    
    print(f"✅ QR code cleanup works correctly")
    print("\n🎉 All QR code tests passed!")


if __name__ == "__main__":
    test_qr_generation()
