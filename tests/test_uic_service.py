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

        result = self.service._normalize_text("Kinshasa (Gombe)")
        assert result == "KINSHASA"  # Note: this will remove everything after space

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
        """Test that UIC has correct format."""
        uic = self.service._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASA"
        )

        # Format should be: FNLN-BYMI-HHHHH
        assert len(uic) == 15  # 4 + 1 + 3 + 1 + 5 + 1 = 15
        assert uic[4] == "-"
        assert uic[8] == "-"

        # Check components
        parts = uic.split("-")
        assert len(parts) == 3
        assert parts[0] == "JEKA"  # JE from Jean, KA from Kabila
        assert parts[1] == "85M"   # 85 from 1985, M from Marie
        assert len(parts[2]) == 5  # 5-char hash

    def test_generate_uic_deterministic(self):
        """Test that same inputs produce same UIC."""
        uic1 = self.service._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASA"
        )
        uic2 = self.service._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASA"
        )

        assert uic1 == uic2

    def test_generate_uic_different_inputs(self):
        """Test that different inputs produce different UICs."""
        uic1 = self.service._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASA"
        )
        uic2 = self.service._generate_uic_code(
            "PAUL", "KABILA", "1985", "M", "KINSHASA"
        )

        assert uic1 != uic2

    def test_generate_uic_handles_short_names(self):
        """Test that short names are padded."""
        uic = self.service._generate_uic_code(
            "J", "K", "1985", "M", "KINSHASA"
        )

        parts = uic.split("-")
        assert len(parts[0]) == 4  # Should be padded with X

    def test_normalize_inputs_expands_year(self):
        """Test that 2-digit years are expanded."""
        fn, ln, by, mi, hz = self.service.normalize_inputs(
            "Jean", "Kabila", "85", "M", "Kinshasa"
        )

        assert by == "1985"  # Should expand to 1985

        # Test for recent years
        fn, ln, by, mi, hz = self.service.normalize_inputs(
            "Jean", "Kabila", "05", "M", "Kinshasa"
        )

        assert by == "2005"  # Should expand to 2005


class TestInputNormalization:
    """Test full input normalization pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = UICService(salt="test_salt_for_testing")

    def test_normalize_inputs_complete(self):
        """Test complete input normalization."""
        fn, ln, by, mi, hz = self.service.normalize_inputs(
            "Gédéon",
            "Kanyinda",
            "1990",
            "Marie",
            "Kinshasa"
        )

        assert fn == "GEDEON"
        assert ln == "KANYINDA"
        assert by == "1990"
        assert mi == "MARIE"
        assert hz == "KINSHASA"

    def test_normalize_inputs_handles_variations(self):
        """Test that variations produce same normalized output."""
        result1 = self.service.normalize_inputs(
            "gédéon", "KANYINDA", "90", "m", "kinshasa"
        )
        result2 = self.service.normalize_inputs(
            "Gédéon", "Kanyinda", "1990", "M", "Kinshasa"
        )

        assert result1[0] == result2[0]  # first_name
        assert result1[1] == result2[1]  # last_name
        assert result1[2] == result2[2]  # birth_year
        assert result1[3] == result2[3]  # mother_init
        assert result1[4] == result2[4]  # health_zone


class TestCollisionPrevention:
    """Test that UIC generation prevents collisions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = UICService(salt="test_salt_for_testing")

    def test_different_salts_different_uics(self):
        """Test that different salts produce different UICs."""
        service1 = UICService(salt="salt1")
        service2 = UICService(salt="salt2")

        uic1 = service1._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASA"
        )
        uic2 = service2._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASA"
        )

        # Prefixes should be same, but hashes should differ
        assert uic1[:9] == uic2[:9]  # JEKA-85M-
        assert uic1[9:] != uic2[9:]  # Hash part should differ

    def test_similar_names_different_uics(self):
        """Test that similar but different inputs produce different UICs."""
        uic1 = self.service._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASA"
        )
        uic2 = self.service._generate_uic_code(
            "JEAN", "KABILA", "1985", "M", "KINSHASAA"  # One extra A
        )

        assert uic1 != uic2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
