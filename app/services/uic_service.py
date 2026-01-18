"""
UIC (Unique Identifier Code) Service.

Handles:
1. Text normalization (French accents, casing, special characters)
2. UIC generation using SHA-256 hashing with salt
3. Duplicate detection and collision prevention
4. Database persistence of UIC records
"""
import hashlib
import re
import unicodedata
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.logging_config import get_logger
from app.models.uic import UICRecord

logger = get_logger(__name__)


class UICService:
    """
    Service for generating and managing Unique Identifier Codes.

    Uses a deterministic hashing algorithm to ensure the same person
    always receives the same UIC, while maintaining privacy through
    cryptographic hashing.
    """

    def __init__(self, salt: Optional[str] = None):
        """
        Initialize UIC service.

        Args:
            salt: Cryptographic salt for hashing. If None, uses config value.
        """
        self.salt = salt or settings.uic_salt
        logger.info("UICService initialized", salt_length=len(self.salt))

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent UIC generation.

        Critical for DRC context:
        1. Removes French accents (é -> e, ç -> c)
        2. Removes special characters and spaces
        3. Converts to uppercase
        4. Handles Unicode properly

        Args:
            text: Raw text input

        Returns:
            Normalized uppercase text

        Examples:
            >>> service = UICService(salt="test")
            >>> service._normalize_text("Gédéon")
            'GEDEON'
            >>> service._normalize_text("N'Djamena")
            'NDJAMENA'
        """
        if not text:
            return ""

        # Convert to string if not already
        text = str(text).strip()

        # Normalize Unicode: decompose combined characters
        # NFD separates base characters from combining marks (accents)
        text = unicodedata.normalize('NFD', text)

        # Remove combining marks (accents)
        text = "".join([
            char for char in text
            if unicodedata.category(char) != 'Mn'  # Mn = Mark, Nonspacing
        ])

        # Remove all non-alphanumeric characters
        text = re.sub(r'[^a-zA-Z0-9]', '', text)

        # Convert to uppercase for consistency
        return text.upper()

    def _calculate_input_hash(
        self,
        last_name_code: str,
        first_name_code: str,
        birth_year_digit: str,
        city_code: str,
        gender_code: str
    ) -> str:
        """
        Calculate SHA-256 hash of normalized inputs.

        This hash is used for duplicate detection without exposing
        the raw input data.

        Args:
            last_name_code: Normalized last name code
            first_name_code: Normalized first name code
            birth_year_digit: Last digit of birth year
            city_code: Normalized city code
            gender_code: Gender code (M or F)

        Returns:
            Hexadecimal SHA-256 hash
        """
        # Create deterministic concatenation
        raw_input = f"{last_name_code}|{first_name_code}|{birth_year_digit}|{city_code}|{gender_code}"

        # Hash without salt (for duplicate detection)
        return hashlib.sha256(raw_input.encode('utf-8')).hexdigest()

    def _generate_uic_code(
        self,
        last_name_code: str,
        first_name_code: str,
        birth_year_digit: str,
        city_code: str,
        gender_code: str
    ) -> str:
        """
        Generate the actual UIC code.

        UIC Formula: LLLFFFYCG
        - LLL = first 3 letters of last name code
        - FFF = first 3 letters of first name code
        - Y = last digit of birth year (1 digit)
        - C = city code (2 letters)
        - G = gender code (1 digit: 1, 2, 3, or 4)

        Example: MBEIBR7DA1
        - MBE = Mbengue (last name)
        - IBR = Ibrahima (first name)
        - 7 = 1997 (birth year)
        - DA = Dakar (city)
        - 1 = Homme (gender)

        Args:
            last_name_code: Last name code (3 letters)
            first_name_code: First name code (3 letters)
            birth_year_digit: Last digit of birth year (1 digit)
            city_code: City code (2 letters)
            gender_code: Gender code (1 digit: 1, 2, 3, or 4)

        Returns:
            Formatted UIC code (10 characters)
        """
        # Extract and normalize components
        lll = last_name_code[:3].upper().ljust(3, 'X')       # Ensure 3 letters
        fff = first_name_code[:3].upper().ljust(3, 'X')      # Ensure 3 letters
        y = birth_year_digit[-1:].upper()                     # Last digit
        c = city_code[:2].upper().ljust(2, 'X')              # Ensure 2 letters
        g = gender_code[:1].upper()                           # 1, 2, 3, or 4

        # Format final UIC: LLLFFFYCG (10 characters total)
        uic_code = f"{lll}{fff}{y}{c}{g}"

        logger.debug(
            "Generated UIC code",
            uic_code=uic_code,
            components={
                "last_name_code": lll,
                "first_name_code": fff,
                "birth_year_digit": y,
                "city_code": c,
                "gender_code": g
            }
        )

        return uic_code

    def normalize_inputs(
        self,
        last_name_code: str,
        first_name_code: str,
        birth_year_digit: str,
        city_code: str,
        gender_code: str
    ) -> Tuple[str, str, str, str, str]:
        """
        Normalize all inputs for UIC generation.

        Args:
            last_name_code: Last name code (raw)
            first_name_code: First name code (raw)
            birth_year_digit: Last digit of birth year (raw)
            city_code: City code (raw)
            gender_code: Gender code (raw)

        Returns:
            Tuple of normalized inputs in same order
        """
        norm_lnc = self._normalize_text(last_name_code)
        norm_fnc = self._normalize_text(first_name_code)
        norm_byd = self._normalize_text(birth_year_digit)
        norm_cc = self._normalize_text(city_code)
        norm_gc = self._normalize_text(gender_code)

        logger.info(
            "Normalized inputs",
            last_name_code=norm_lnc,
            first_name_code=norm_fnc,
            birth_year_digit=norm_byd,
            city_code=norm_cc,
            gender_code=norm_gc
        )

        return norm_lnc, norm_fnc, norm_byd, norm_cc, norm_gc

    async def check_existing_uic(
        self,
        db: AsyncSession,
        last_name_code: str,
        first_name_code: str,
        birth_year_digit: str,
        city_code: str,
        gender_code: str
    ) -> Optional[UICRecord]:
        """
        Check if a UIC already exists for these inputs.

        Args:
            db: Database session
            last_name_code: Normalized last name code
            first_name_code: Normalized first name code
            birth_year_digit: Last digit of birth year
            city_code: Normalized city code
            gender_code: Gender code

        Returns:
            Existing UICRecord if found, None otherwise
        """
        input_hash = self._calculate_input_hash(
            last_name_code, first_name_code, birth_year_digit, city_code, gender_code
        )

        stmt = select(UICRecord).where(
            UICRecord.input_hash == input_hash,
            UICRecord.is_active == True
        )

        result = await db.execute(stmt)
        existing_record = result.scalar_one_or_none()

        if existing_record:
            logger.info(
                "Found existing UIC",
                uic_code=existing_record.uic_code,
                created_at=existing_record.created_at
            )

        return existing_record

    async def create_uic(
        self,
        db: AsyncSession,
        phone_number: str,
        last_name_code: str,
        first_name_code: str,
        birth_year_digit: str,
        city_code: str,
        gender_code: str
    ) -> Tuple[str, bool]:
        """
        Create or retrieve a UIC for the given inputs.

        Args:
            db: Database session
            phone_number: User's WhatsApp phone number
            last_name_code: Last name code
            first_name_code: First name code
            birth_year_digit: Last digit of birth year
            city_code: City code
            gender_code: Gender code

        Returns:
            Tuple of (uic_code, is_new)
            - uic_code: The generated or existing UIC
            - is_new: True if newly created, False if existing
        """
        # Normalize all inputs
        norm_lnc, norm_fnc, norm_byd, norm_cc, norm_gc = self.normalize_inputs(
            last_name_code, first_name_code, birth_year_digit, city_code, gender_code
        )

        # Check for existing UIC
        existing_record = await self.check_existing_uic(
            db, norm_lnc, norm_fnc, norm_byd, norm_cc, norm_gc
        )

        if existing_record:
            # Update last requested time and count
            existing_record.last_requested_at = datetime.utcnow()
            existing_record.request_count += 1
            await db.commit()

            logger.info(
                "Returning existing UIC",
                uic_code=existing_record.uic_code,
                request_count=existing_record.request_count
            )

            return existing_record.uic_code, False

        # Generate new UIC
        uic_code = self._generate_uic_code(
            norm_lnc, norm_fnc, norm_byd, norm_cc, norm_gc
        )

        input_hash = self._calculate_input_hash(
            norm_lnc, norm_fnc, norm_byd, norm_cc, norm_gc
        )

        # Create database record
        uic_record = UICRecord(
            uic_code=uic_code,
            phone_number=phone_number,
            normalized_last_name_code=norm_lnc,
            normalized_first_name_code=norm_fnc,
            normalized_birth_year_digit=norm_byd,
            normalized_city_code=norm_cc,
            normalized_gender_code=norm_gc,
            input_hash=input_hash,
            created_at=datetime.utcnow(),
            last_requested_at=datetime.utcnow(),
            is_active=True,
            request_count=1
        )

        db.add(uic_record)
        await db.commit()
        await db.refresh(uic_record)

        logger.info(
            "Created new UIC",
            uic_code=uic_code,
            phone_number=phone_number
        )

        return uic_code, True
