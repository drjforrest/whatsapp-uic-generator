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
        first_name: str,
        last_name: str,
        birth_year: str,
        mother_init: str,
        health_zone: str
    ) -> str:
        """
        Calculate SHA-256 hash of normalized inputs.

        This hash is used for duplicate detection without exposing
        the raw input data.

        Args:
            first_name: Normalized first name
            last_name: Normalized last name
            birth_year: Normalized birth year
            mother_init: Normalized mother's initial
            health_zone: Normalized health zone

        Returns:
            Hexadecimal SHA-256 hash
        """
        # Create deterministic concatenation
        raw_input = f"{first_name}|{last_name}|{birth_year}|{mother_init}|{health_zone}"

        # Hash without salt (for duplicate detection)
        return hashlib.sha256(raw_input.encode('utf-8')).hexdigest()

    def _generate_uic_code(
        self,
        first_name: str,
        last_name: str,
        birth_year: str,
        mother_init: str,
        health_zone: str
    ) -> str:
        """
        Generate the actual UIC code.

        NOTE: Parameter names don't match the placeholder questions!
        Current placeholder question mapping:
        - first_name = Answer to Q1 (birth year: 1985)
        - last_name = Answer to Q2 (mother's birthplace: Kinshasa)
        - birth_year = Answer to Q3 (person's first name: Jean)
        - mother_init = Answer to Q4 (day of month: 15)
        - health_zone = Answer to Q5 (family name: Kabila)

        Format: YYY-MMMMDD-FNNN-LLLL-HHHHH (customize as needed!)
        Where (current placeholder extraction):
        - YYY: Last 3 digits of birth year (Q1)
        - MMMM: First 4 letters of mother's birthplace (Q2)
        - DD: Day of month (Q4)
        - FNNN: First 3 letters of first name (Q3)
        - LLLL: First 4 letters of family name (Q5)
        - HHHHH: 5-character hash suffix for uniqueness

        Args:
            first_name: Answer to question 1 (normalized)
            last_name: Answer to question 2 (normalized)
            birth_year: Answer to question 3 (normalized)
            mother_init: Answer to question 4 (normalized)
            health_zone: Answer to question 5 (normalized)

        Returns:
            Formatted UIC code
        """
        # Extract components based on placeholder questions
        # CUSTOMIZE THESE EXTRACTIONS FOR YOUR ACTUAL QUESTIONS!

        year_last3 = first_name[-3:].rjust(3, '0')      # Q1: Last 3 digits of year
        mother_loc4 = last_name[:4].ljust(4, 'X')       # Q2: First 4 letters of location
        day_of_month = mother_init[:2].rjust(2, '0')    # Q4: Day of month
        first_name3 = birth_year[:3].ljust(3, 'X')      # Q3: First 3 letters of name
        family_name4 = health_zone[:4].ljust(4, 'X')    # Q5: First 4 letters of surname

        # Create salted hash for uniqueness
        raw_seed = f"{first_name}{last_name}{birth_year}{mother_init}{health_zone}"
        hash_input = f"{raw_seed}{self.salt}".encode('utf-8')
        full_hash = hashlib.sha256(hash_input).hexdigest().upper()

        # Take first 5 characters of hash
        hash_suffix = full_hash[:5]

        # Format final UIC - CUSTOMIZE THIS FORMAT!
        # Current format: YYY-MMMMDD-FNNN-LLLL-HHHHH
        uic_code = f"{year_last3}-{mother_loc4}{day_of_month}-{first_name3}-{family_name4}-{hash_suffix}"

        logger.debug(
            "Generated UIC code",
            uic_code=uic_code,
            components={
                "year_last3": year_last3,
                "mother_loc4": mother_loc4,
                "day": day_of_month,
                "first_name3": first_name3,
                "family_name4": family_name4,
                "hash": hash_suffix
            }
        )

        return uic_code

    def normalize_inputs(
        self,
        first_name: str,
        last_name: str,
        birth_year: str,
        mother_init: str,
        health_zone: str
    ) -> Tuple[str, str, str, str, str]:
        """
        Normalize all inputs for UIC generation.

        NOTE: Parameter names don't match placeholder questions!
        - first_name = Q1 answer (birth year)
        - last_name = Q2 answer (mother's birthplace)
        - birth_year = Q3 answer (person's first name)
        - mother_init = Q4 answer (day of month)
        - health_zone = Q5 answer (family name)

        Args:
            first_name: Answer to Q1 (raw)
            last_name: Answer to Q2 (raw)
            birth_year: Answer to Q3 (raw)
            mother_init: Answer to Q4 (raw)
            health_zone: Answer to Q5 (raw)

        Returns:
            Tuple of normalized inputs in same order
        """
        norm_q1 = self._normalize_text(first_name)    # Birth year
        norm_q2 = self._normalize_text(last_name)     # Mother's birthplace
        norm_q3 = self._normalize_text(birth_year)    # Person's first name
        norm_q4 = self._normalize_text(mother_init)   # Day of month
        norm_q5 = self._normalize_text(health_zone)   # Family name

        logger.info(
            "Normalized inputs",
            q1_birth_year=norm_q1,
            q2_mother_place=norm_q2,
            q3_first_name=norm_q3,
            q4_day=norm_q4,
            q5_family_name=norm_q5
        )

        return norm_q1, norm_q2, norm_q3, norm_q4, norm_q5

    async def check_existing_uic(
        self,
        db: AsyncSession,
        first_name: str,
        last_name: str,
        birth_year: str,
        mother_init: str,
        health_zone: str
    ) -> Optional[UICRecord]:
        """
        Check if a UIC already exists for these inputs.

        Args:
            db: Database session
            first_name: Normalized first name
            last_name: Normalized last name
            birth_year: Normalized birth year
            mother_init: Normalized mother's initial
            health_zone: Normalized health zone

        Returns:
            Existing UICRecord if found, None otherwise
        """
        input_hash = self._calculate_input_hash(
            first_name, last_name, birth_year, mother_init, health_zone
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
        first_name: str,
        last_name: str,
        birth_year: str,
        mother_init: str,
        health_zone: str
    ) -> Tuple[str, bool]:
        """
        Create or retrieve a UIC for the given inputs.

        Args:
            db: Database session
            phone_number: User's WhatsApp phone number
            first_name: Raw first name
            last_name: Raw last name
            birth_year: Raw birth year
            mother_init: Raw mother's initial
            health_zone: Raw health zone

        Returns:
            Tuple of (uic_code, is_new)
            - uic_code: The generated or existing UIC
            - is_new: True if newly created, False if existing
        """
        # Normalize all inputs
        norm_fn, norm_ln, norm_by, norm_mi, norm_hz = self.normalize_inputs(
            first_name, last_name, birth_year, mother_init, health_zone
        )

        # Check for existing UIC
        existing_record = await self.check_existing_uic(
            db, norm_fn, norm_ln, norm_by, norm_mi, norm_hz
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
            norm_fn, norm_ln, norm_by, norm_mi, norm_hz
        )

        input_hash = self._calculate_input_hash(
            norm_fn, norm_ln, norm_by, norm_mi, norm_hz
        )

        # Create database record
        uic_record = UICRecord(
            uic_code=uic_code,
            phone_number=phone_number,
            normalized_first_name=norm_fn,
            normalized_last_name=norm_ln,
            normalized_birth_year=norm_by,
            normalized_mother_init=norm_mi,
            normalized_health_zone=norm_hz,
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
