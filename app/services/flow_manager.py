"""
Conversation Flow Manager.

Manages the state machine for multi-step conversations over WhatsApp.
Handles question sequencing, answer collection, and session management.

IMPORTANT: The questions ask for FULL information (e.g., "Where was your mother born?").
The UICService extracts what it needs (first 4 letters, last 3 digits, etc.).
Users should NOT be asked to manually extract parts of their data!
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.logging_config import get_logger
from app.models.uic import ConversationSession

logger = get_logger(__name__)


class ConversationStep:
    """Represents a single step in the conversation flow."""

    def __init__(
        self,
        key: str,
        question_en: str,
        question_fr: str,
        field_name: str,
        validator: Optional[callable] = None
    ):
        """
        Initialize conversation step.

        Args:
            key: Unique identifier for this step
            question_en: Question text in English
            question_fr: Question text in French
            field_name: Database field name to store the answer
            validator: Optional validation function
        """
        self.key = key
        self.question_en = question_en
        self.question_fr = question_fr
        self.field_name = field_name
        self.validator = validator

    def get_question(self, language: str = "en") -> str:
        """Get question text in specified language."""
        if language == "fr":
            return self.question_fr
        return self.question_en

    def validate(self, answer: str) -> tuple[bool, Optional[str]]:
        """
        Validate the answer.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.validator:
            return self.validator(answer)
        return True, None


def validate_digits_only(answer: str) -> tuple[bool, Optional[str]]:
    """Validate that answer contains only digits."""
    answer = answer.strip()

    if not answer.isdigit():
        return False, "Please enter only numbers (no letters or spaces)"

    if len(answer) < 2:
        return False, "Please enter at least 2 digits"

    return True, None


def validate_letters_only(answer: str) -> tuple[bool, Optional[str]]:
    """Validate that answer contains only letters."""
    answer = answer.strip()

    if not answer.isalpha():
        return False, "Please enter only letters (no numbers or special characters)"

    if len(answer) < 2:
        return False, "Please enter at least 2 letters"

    return True, None


def validate_not_empty(answer: str) -> tuple[bool, Optional[str]]:
    """Validate that answer is not empty."""
    if not answer or not answer.strip():
        return False, "Please provide an answer"

    if len(answer.strip()) < 1:
        return False, "Answer is too short"

    return True, None


class FlowManager:
    """
    Manages conversation flow and session state.

    Handles:
    1. Question sequencing
    2. Answer validation and storage
    3. Session lifecycle management
    4. Timeout handling
    """

    # Define the conversation flow
    # NOTE: These are PLACEHOLDER questions - customize for your specific use case!
    # Users answer with FULL information; the system extracts what it needs (first letters, last digits, etc.)
    STEPS = [
        ConversationStep(
            key="first_name",
            question_en=(
                "Question 1 of 5:\n\n"
                "What year were you born?\n\n"
                "Example: 1985"
            ),
            question_fr=(
                "Question 1 sur 5:\n\n"
                "Quelle année êtes-vous né(e)?\n\n"
                "Exemple: 1985"
            ),
            field_name="first_name",
            validator=validate_not_empty
        ),
        ConversationStep(
            key="last_name",
            question_en=(
                "Question 2 of 5:\n\n"
                "Where was your mother born? (City or village)\n\n"
                "Example: Kinshasa"
            ),
            question_fr=(
                "Question 2 sur 5:\n\n"
                "Où est née votre mère? (Ville ou village)\n\n"
                "Exemple: Kinshasa"
            ),
            field_name="last_name",
            validator=validate_not_empty
        ),
        ConversationStep(
            key="birth_year",
            question_en=(
                "Question 3 of 5:\n\n"
                "What is your first name?\n\n"
                "Example: Jean"
            ),
            question_fr=(
                "Question 3 sur 5:\n\n"
                "Quel est votre prénom?\n\n"
                "Exemple: Jean"
            ),
            field_name="birth_year",
            validator=validate_not_empty
        ),
        ConversationStep(
            key="mother_init",
            question_en=(
                "Question 4 of 5:\n\n"
                "What day of the month were you born?\n\n"
                "Example: 15"
            ),
            question_fr=(
                "Question 4 sur 5:\n\n"
                "Quel jour du mois êtes-vous né(e)?\n\n"
                "Exemple: 15"
            ),
            field_name="mother_init",
            validator=validate_not_empty
        ),
        ConversationStep(
            key="health_zone",
            question_en=(
                "Question 5 of 5:\n\n"
                "What is your family name?\n\n"
                "Example: Kabila"
            ),
            question_fr=(
                "Question 5 sur 5:\n\n"
                "Quel est votre nom de famille?\n\n"
                "Exemple: Kabila"
            ),
            field_name="health_zone",
            validator=validate_not_empty
        ),
    ]

    WELCOME_MESSAGE_EN = (
        "👋 Welcome to the UIC Generator!\n\n"
        "I will ask you 5 questions to generate your Unique Identifier Code (UIC).\n\n"
        "📋 Your UIC is:\n"
        "• Unique to you\n"
        "• Private and secure\n"
        "• Can be regenerated if needed\n\n"
        "Type RESTART anytime to start over.\n"
        "Type HELP for assistance.\n\n"
        "Let's begin! 🚀"
    )

    WELCOME_MESSAGE_FR = (
        "👋 Bienvenue au Générateur UIC!\n\n"
        "Je vais vous poser 5 questions pour générer votre Code d'Identification Unique (UIC).\n\n"
        "📋 Votre UIC est:\n"
        "• Unique pour vous\n"
        "• Privé et sécurisé\n"
        "• Peut être régénéré si nécessaire\n\n"
        "Tapez RESTART pour recommencer.\n"
        "Tapez HELP pour de l'aide.\n\n"
        "Commençons! 🚀"
    )

    COMPLETION_MESSAGE_EN = (
        "✅ Thank you! I have all the information.\n\n"
        "Generating your secure UIC...\n"
        "⏳ Please wait..."
    )

    COMPLETION_MESSAGE_FR = (
        "✅ Merci! J'ai toutes les informations.\n\n"
        "Génération de votre UIC sécurisé...\n"
        "⏳ Veuillez patienter..."
    )

    def __init__(self):
        """Initialize FlowManager."""
        logger.info("FlowManager initialized", total_steps=len(self.STEPS))

    async def get_or_create_session(
        self,
        db: AsyncSession,
        phone_number: str,
        language: str = "en"
    ) -> ConversationSession:
        """
        Get existing session or create new one.

        Args:
            db: Database session
            phone_number: User's WhatsApp phone number
            language: Preferred language (en or fr)

        Returns:
            ConversationSession instance
        """
        # Try to find existing session
        stmt = select(ConversationSession).where(
            ConversationSession.phone_number == phone_number
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if session:
            # Check if expired
            if session.is_expired:
                logger.info("Session expired, creating new one", phone_number=phone_number)
                await db.delete(session)
                await db.commit()
                session = None
            else:
                logger.info(
                    "Found existing session",
                    phone_number=phone_number,
                    step=session.current_step
                )
                return session

        # Create new session
        expires_at = datetime.utcnow() + timedelta(minutes=settings.session_timeout_minutes)

        session = ConversationSession(
            phone_number=phone_number,
            current_step=0,
            language=language,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=expires_at
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        logger.info("Created new session", phone_number=phone_number)

        return session

    async def restart_session(self, db: AsyncSession, phone_number: str) -> None:
        """
        Restart conversation by deleting existing session.

        Args:
            db: Database session
            phone_number: User's WhatsApp phone number
        """
        stmt = delete(ConversationSession).where(
            ConversationSession.phone_number == phone_number
        )
        await db.execute(stmt)
        await db.commit()

        logger.info("Session restarted", phone_number=phone_number)

    async def process_message(
        self,
        db: AsyncSession,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Process incoming message and return appropriate response.

        Args:
            db: Database session
            phone_number: User's WhatsApp phone number
            message: User's message

        Returns:
            Dictionary with:
            - response: Text to send back to user
            - is_complete: Whether conversation is complete
            - collected_data: Dictionary of collected answers (if complete)
        """
        message = message.strip()

        # Handle special commands
        if message.upper() == "RESTART":
            await self.restart_session(db, phone_number)
            return {
                "response": self.WELCOME_MESSAGE_EN + "\n\n" + self.STEPS[0].get_question(),
                "is_complete": False,
                "collected_data": None
            }

        if message.upper() == "HELP":
            help_text = (
                "📖 Help:\n\n"
                "Commands:\n"
                "• RESTART - Start over from the beginning\n"
                "• HELP - Show this message\n\n"
                "I will ask you 5 questions to generate your UIC.\n"
                "Answer each question truthfully and press send."
            )
            return {
                "response": help_text,
                "is_complete": False,
                "collected_data": None
            }

        # Get or create session
        session = await self.get_or_create_session(db, phone_number)

        # If step is 0, this is a welcome message
        if session.current_step == 0 and not message:
            response = self.WELCOME_MESSAGE_EN + "\n\n" + self.STEPS[0].get_question()
            return {
                "response": response,
                "is_complete": False,
                "collected_data": None
            }

        # Get current step
        current_step = self.STEPS[session.current_step]

        # Validate answer
        is_valid, error_message = current_step.validate(message)

        if not is_valid:
            logger.warning(
                "Validation failed",
                phone_number=phone_number,
                step=current_step.key,
                error=error_message
            )
            return {
                "response": f"❌ {error_message}\n\n{current_step.get_question(session.language)}",
                "is_complete": False,
                "collected_data": None
            }

        # Store answer
        setattr(session, current_step.field_name, message)
        session.updated_at = datetime.utcnow()

        logger.info(
            "Answer stored",
            phone_number=phone_number,
            step=current_step.key,
            answer_length=len(message)
        )

        # Move to next step
        session.current_step += 1

        # Check if conversation is complete
        if session.current_step >= len(self.STEPS):
            # Collect all data
            collected_data = {
                "first_name": session.first_name,
                "last_name": session.last_name,
                "birth_year": session.birth_year,
                "mother_init": session.mother_init,
                "health_zone": session.health_zone,
            }

            # Delete session (conversation complete)
            await db.delete(session)
            await db.commit()

            logger.info(
                "Conversation complete",
                phone_number=phone_number,
                collected_fields=list(collected_data.keys())
            )

            return {
                "response": self.COMPLETION_MESSAGE_EN,
                "is_complete": True,
                "collected_data": collected_data
            }

        # Continue to next question
        await db.commit()

        next_step = self.STEPS[session.current_step]
        response = f"✅ Got it!\n\n{next_step.get_question(session.language)}"

        return {
            "response": response,
            "is_complete": False,
            "collected_data": None
        }

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """
        Clean up expired sessions.

        Args:
            db: Database session

        Returns:
            Number of sessions deleted
        """
        stmt = delete(ConversationSession).where(
            ConversationSession.expires_at < datetime.utcnow()
        )

        result = await db.execute(stmt)
        await db.commit()

        count = result.rowcount
        logger.info("Cleaned up expired sessions", count=count)

        return count
