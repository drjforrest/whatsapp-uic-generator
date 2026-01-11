"""
Database models for UIC records.
Stores generated UICs and their associated metadata.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UICRecord(Base):
    """
    Model for storing Unique Identifier Codes and their metadata.

    This table serves as:
    1. A registry of all issued UICs
    2. A duplicate prevention mechanism
    3. An audit trail for compliance
    """
    __tablename__ = "uic_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # The generated UIC
    uic_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="The generated Unique Identifier Code"
    )

    # User's phone number (for contact tracking, not identification)
    phone_number: Mapped[str] = mapped_column(
        String(20),
        index=True,
        nullable=False,
        comment="WhatsApp phone number (E.164 format)"
    )

    # Normalized input data (for duplicate detection)
    normalized_first_name: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Normalized first name initials"
    )
    normalized_last_name: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Normalized last name initials"
    )
    normalized_birth_year: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        comment="Normalized birth year"
    )
    normalized_mother_init: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        comment="Normalized mother's initial"
    )
    normalized_health_zone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Normalized health zone"
    )

    # Hash of the normalized inputs (for collision detection)
    input_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
        comment="SHA-256 hash of normalized inputs"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When the UIC was generated"
    )
    last_requested_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last time this UIC was requested"
    )

    # Status tracking
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this UIC is currently active"
    )

    # Optional notes (for administrative purposes)
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Administrative notes"
    )

    # Request count (for analytics)
    request_count: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
        comment="Number of times this UIC was requested"
    )

    # Composite index for efficient duplicate detection
    __table_args__ = (
        Index(
            'ix_uic_normalized_data',
            'normalized_first_name',
            'normalized_last_name',
            'normalized_birth_year',
            'normalized_mother_init',
            'normalized_health_zone'
        ),
    )

    def __repr__(self) -> str:
        return f"<UICRecord(uic_code='{self.uic_code}', phone='{self.phone_number}')>"


class ConversationSession(Base):
    """
    Model for tracking conversation state across webhook calls.

    In production, this would typically be in Redis.
    For POC with SQLite, we use this table.
    """
    __tablename__ = "conversation_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # User identifier
    phone_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
        comment="WhatsApp phone number (E.164 format)"
    )

    # Current conversation state
    current_step: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Current question index"
    )

    # Collected answers (stored as JSON-compatible format)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birth_year: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    mother_init: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    health_zone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Session metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When the session started"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last activity time"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="When the session expires"
    )

    # Language preference (for future French/Lingala support)
    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
        comment="User's preferred language"
    )

    def __repr__(self) -> str:
        return f"<ConversationSession(phone='{self.phone_number}', step={self.current_step})>"

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_complete(self) -> bool:
        """Check if all answers have been collected."""
        return all([
            self.first_name,
            self.last_name,
            self.birth_year,
            self.mother_init,
            self.health_zone
        ])
