"""
WhatsApp webhook endpoints for Twilio integration.
"""
from fastapi import APIRouter, Form, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.twiml.messaging_response import MessagingResponse

from app.database import get_db
from app.logging_config import get_logger
from app.services.flow_manager import FlowManager
from app.services.uic_service import UICService

logger = get_logger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["webhook"])

# Initialize services
flow_manager = FlowManager()
uic_service = UICService()


@router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(None),
    db: AsyncSession = Depends(get_db)
) -> Response:
    """
    Main webhook endpoint for incoming WhatsApp messages from Twilio.

    This endpoint:
    1. Receives messages from Twilio (via Form data)
    2. Processes the conversation flow
    3. Generates UIC when conversation is complete
    4. Returns TwiML response to send message back to user

    Args:
        From: WhatsApp phone number (E.164 format, e.g., whatsapp:+1234567890)
        Body: Message text from user
        MessageSid: Twilio message identifier
        db: Database session (injected)

    Returns:
        TwiML XML response for Twilio
    """
    # Clean phone number (remove whatsapp: prefix)
    phone_number = From.replace("whatsapp:", "")

    logger.info(
        "Received WhatsApp message",
        phone_number=phone_number,
        message_length=len(Body),
        message_sid=MessageSid
    )

    try:
        # Process the message through flow manager
        result = await flow_manager.process_message(
            db=db,
            phone_number=phone_number,
            message=Body
        )

        response_text = result["response"]

        # If conversation is complete, generate UIC
        if result["is_complete"] and result["collected_data"]:
            collected_data = result["collected_data"]

            logger.info(
                "Generating UIC",
                phone_number=phone_number,
                data_keys=list(collected_data.keys())
            )

            # Generate UIC
            uic_code, is_new = await uic_service.create_uic(
                db=db,
                phone_number=phone_number,
                first_name=collected_data["first_name"],
                last_name=collected_data["last_name"],
                birth_year=collected_data["birth_year"],
                mother_init=collected_data["mother_init"],
                health_zone=collected_data["health_zone"]
            )

            # Prepare final message
            if is_new:
                response_text = (
                    f"🎉 Your Unique Identifier Code has been generated!\n\n"
                    f"📋 Your UIC:\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"  {uic_code}\n"
                    f"━━━━━━━━━━━━━━\n\n"
                    f"✅ This code is now registered in your name.\n\n"
                    f"💡 Save this code! You can request it again by starting a new conversation.\n\n"
                    f"Type RESTART to generate a new UIC or update information."
                )
            else:
                response_text = (
                    f"📋 Your existing UIC:\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"  {uic_code}\n"
                    f"━━━━━━━━━━━━━━\n\n"
                    f"ℹ️ This code was previously generated with the same information.\n\n"
                    f"Type RESTART if you need to update your information."
                )

            logger.info(
                "UIC delivered",
                phone_number=phone_number,
                uic_code=uic_code,
                is_new=is_new
            )

        # Create Twilio TwiML response
        twiml_response = MessagingResponse()
        twiml_response.message(response_text)

        # Return as XML
        return Response(
            content=str(twiml_response),
            media_type="application/xml"
        )

    except Exception as e:
        logger.error(
            "Error processing webhook",
            phone_number=phone_number,
            error=str(e),
            exc_info=True
        )

        # Send error message to user
        error_response = MessagingResponse()
        error_response.message(
            "❌ Sorry, an error occurred. Please type RESTART to try again or contact support."
        )

        return Response(
            content=str(error_response),
            media_type="application/xml"
        )


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for monitoring.

    Returns:
        Status dictionary
    """
    return {
        "status": "healthy",
        "service": "whatsapp-uic-generator",
        "version": "0.1.0"
    }


@router.post("/cleanup")
async def cleanup_sessions(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Manual endpoint to cleanup expired sessions.

    This would typically be called by a cron job.

    Returns:
        Count of cleaned up sessions
    """
    count = await flow_manager.cleanup_expired_sessions(db)

    logger.info("Manual cleanup triggered", sessions_removed=count)

    return {
        "status": "success",
        "sessions_cleaned": count
    }
