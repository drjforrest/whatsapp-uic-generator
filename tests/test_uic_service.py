"""
Tests for UICService.

Run with: pytest tests/test_uic_service.py
"""
import pytest

from app.services.uic_service import UICService


class TestUICServiceNormalization:
    """Test text normalization functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = UICService(salt="test_salt_for_testing")

    def test_normalize_removes_accents(self):
        """Test that French accents are removed."""
        result = self.service._normalize_text("Gédéon")
        assert result == "GEDEON"

        result = self.service._normalize_text("François")
        assert result == "FRANCOIS"

        result = self.service._normalize_text("Kanyinda")
        assert result == "KANYINDA"

    def test_normalize_uppercase(self):
        """Test that text is converted to uppercase."""
        result = self.service._normalize_text("jean")
        assert result == "JEAN"

        result = self.service._normalize_text("KaBiLa")
        assert result == "KABILA"

    def test_normalize_removes_special_chars(self):
        """Test that special characters are removed."""
        result = self.service._normalize_text("N'Djamena")
        assert result == "NDJAMENA"

        result = self.service._normalize_text("Jean-Paul")
        assert result == "JEANPAUL"

    def test_normalize_handles_empty(self):
        """Test that empty strings are handled."""
        result = self.service._normalize_text("")
        assert result == ""

        result = self.service._normalize_text("   ")
        assert result == ""

    def test_normalize_consistent(self):
        """Test that normalization is consistent."""
        result1 = self.service._normalize_text("Gédéon")
        result2 = self.service._normalize_text("gedeon")
        result3 = self.service._normalize_text("GEDEON")

        assert result1 == result2 == result3


class TestUICGeneration:
    """Test UIC code generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = UICService(salt="test_salt_for_testing")

    def test_generate_uic_format(self):
        """Test that UIC has correct format: LLLFFFYCG."""
        uic = self.service._generate_uic_code(
            last_name_code="MBE",
            first_name_code="IBR", 
            birth_year_digit="7",
            city_code="DA",
            gender_code="1"
        )

        # Format should be: LLLFFFYCG = 10 characters
        assert len(uic) == 10
        
        # Check components
        assert uic[:3] == "MBE"  # Last name code
        assert uic[3:6] == "IBR"  # First name code
        assert uic[6] == "7"      # Birth year digit
        assert uic[7:9] == "DA"   # City code (2 letters)
        assert uic[9] == "1"      # Gender code (1 digit)

    def test_generate_uic_deterministic(self):
        """Test that same inputs produce same UIC."""
        uic1 = self.service._generate_uic_code(
            "MBE", "IBR", "7", "DA", "1"
        )
        uic2 = self.service._generate_uic_code(
            "MBE", "IBR", "7", "DA", "1"
        )

        assert uic1 == uic2

    def test_generate_uic_different_inputs(self):
        """Test that different inputs produce different UICs."""
        uic1 = self.service._generate_uic_code(
            "MBE", "IBR", "7", "DA", "1"
        )
        uic2 = self.service._generate_uic_code(
            "MBE", "AMA", "7", "DA", "1"  # Different first name
        )

        assert uic1 != uic2

    def test_generate_uic_handles_short_codes(self):
        """Test that short codes are padded."""
        uic = self.service._generate_uic_code(
            "K", "J", "5", "D", "2"
        )

        # Should pad to proper length
        assert len(uic) == 10
        assert uic[:3] == "KXX"  # Padded with X
        assert uic[3:6] == "JXX"  # Padded with X
        assert uic[7:9] == "DX"   # Padded with X

    def test_normalize_inputs_complete(self):
        """Test complete input normalization."""
        lnc, fnc, byd, cc, gc = self.service.normalize_inputs(
            "MBE",
            "IBR",
            "7",
            "DA",
            "1"
        )

        assert lnc == "MBE"
        assert fnc == "IBR"
        assert byd == "7"
        assert cc == "DA"
        assert gc == "1"


class TestInputNormalization:
    """Test full input normalization pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = UICService(salt="test_salt_for_testing")

    def test_normalize_inputs_handles_variations(self):
        """Test that variations produce same normalized output."""
        result1 = self.service.normalize_inputs(
            "mbe", "ibr", "7", "da", "1"
        )
        result2 = self.service.normalize_inputs(
            "MBE", "IBR", "7", "DA", "1"
        )

        assert result1[0] == result2[0]  # last_name_code
        assert result1[1] == result2[1]  # first_name_code
        assert result1[2] == result2[2]  # birth_year_digit
        assert result1[3] == result2[3]  # city_code
        assert result1[4] == result2[4]  # gender_code

    def test_normalize_removes_accents_from_codes(self):
        """Test that accents are removed from name codes."""
        lnc, fnc, byd, cc, gc = self.service.normalize_inputs(
            "Gédéon",  # Should become GEDEON
            "François",  # Should become FRANCOIS
            "5",
            "12",
            "F"
        )

        assert lnc == "GEDEON"
        assert fnc == "FRANCOIS"


class TestCollisionPrevention:
    """Test that UIC generation works correctly."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = UICService(salt="test_salt_for_testing")

    def test_similar_codes_different_uics(self):
        """Test that similar but different inputs produce different UICs."""
        uic1 = self.service._generate_uic_code(
            "MBE", "IBR", "7", "DA", "1"
        )
        uic2 = self.service._generate_uic_code(
            "MBE", "IBR", "7", "DA", "2"  # Different gender
        )

        assert uic1 != uic2

    def test_complete_uic_examples(self):
        """Test complete UIC generation with real examples."""
        # Example 1: Homme from Dakar
        uic1 = self.service._generate_uic_code(
            last_name_code="MBE",
            first_name_code="IBR",
            birth_year_digit="7",
            city_code="DA",
            gender_code="1"
        )
        assert uic1 == "MBEIBR7DA1"

        # Example 2: Femme from Kinshasa  
        uic2 = self.service._generate_uic_code(
            last_name_code="MOB",
            first_name_code="MAR",
            birth_year_digit="3",
            city_code="KI",
            gender_code="2"
        )
        assert uic2 == "MOBMAR3KI2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
