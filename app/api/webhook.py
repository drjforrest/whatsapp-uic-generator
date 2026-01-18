"""
WhatsApp webhook endpoints for Twilio integration.
"""
from fastapi import APIRouter, Form, Depends, Response, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.twiml.messaging_response import MessagingResponse

from app.config import settings
from app.database import get_db
from app.logging_config import get_logger
from app.services.flow_manager import FlowManager
from app.services.uic_service import UICService
from app.services.qr_service import QRCodeService

logger = get_logger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["webhook"])

# Initialize services
flow_manager = FlowManager()
uic_service = UICService()
qr_service = QRCodeService() if settings.enable_qr_code else None


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
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
                last_name_code=collected_data["last_name_code"],
                first_name_code=collected_data["first_name_code"],
                birth_year_digit=collected_data["birth_year_digit"],
                city_code=collected_data["city_code"],
                gender_code=collected_data["gender_code"]
            )

            # Prepare final message
            if is_new:
                response_text = (
                    f"🎉 Votre Code d'Identification Unique a été généré!\n\n"
                    f"📋 Votre CIU:\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"  {uic_code}\n"
                    f"━━━━━━━━━━━━━━\n\n"
                    f"✅ Ce code est maintenant enregistré à votre nom.\n\n"
                    f"💡 Sauvegardez ce code! Vous pouvez le redemander en commençant une nouvelle conversation.\n\n"
                )
                if settings.enable_qr_code:
                    response_text += "📱 Vous recevrez également un code QR pour un accès facile.\n\n"
                response_text += "Tapez RESTART pour générer un nouveau CIU ou mettre à jour vos informations."
            else:
                response_text = (
                    f"📋 Votre CIU existant:\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"  {uic_code}\n"
                    f"━━━━━━━━━━━━━━\n\n"
                    f"ℹ️ Ce code a été généré précédemment avec les mêmes informations.\n\n"
                )
                if settings.enable_qr_code:
                    response_text += "📱 Vous recevrez également un code QR.\n\n"
                response_text += "Tapez RESTART si vous devez mettre à jour vos informations."

            logger.info(
                "UIC delivered",
                phone_number=phone_number,
                uic_code=uic_code,
                is_new=is_new
            )

        # Create Twilio TwiML response
        twiml_response = MessagingResponse()
        message = twiml_response.message(response_text)

        # Add QR code if feature is enabled and conversation is complete
        if settings.enable_qr_code and result["is_complete"] and qr_service:
            try:
                # Generate QR code
                qr_path, qr_bytes = qr_service.generate_qr_code(uic_code)
                
                # Build public URL for QR code
                # Get the request's base URL
                base_url = str(request.base_url).rstrip('/')
                qr_url = f"{base_url}/static/qr_codes/{uic_code}.png"
                
                # Add media URL to Twilio message
                message.media(qr_url)
                
                logger.info(
                    "QR code attached to message",
                    uic_code=uic_code,
                    qr_url=qr_url
                )
            except Exception as qr_error:
                logger.error(
                    "Failed to generate/attach QR code",
                    uic_code=uic_code,
                    error=str(qr_error),
                    exc_info=True
                )
                # Don't fail the whole request, just log the error

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
            "❌ Désolé, une erreur s'est produite. Veuillez taper RESTART pour réessayer ou contacter le support."
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
