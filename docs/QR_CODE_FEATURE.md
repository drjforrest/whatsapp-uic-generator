# QR Code Feature Guide

## Overview

The WhatsApp UIC Generator now includes an optional QR code feature that generates and sends scannable QR codes containing the user's UIC via WhatsApp.

## Feature Toggle

This feature is **disabled by default** and can be enabled via environment variable:

```bash
# In your .env file
ENABLE_QR_CODE=true
```

## How It Works

### User Experience

When the QR code feature is enabled:

1. User completes the 5 questions as normal
2. Bot generates the UIC code (e.g., `MBEIBR7DA1`)
3. Bot sends text message with the UIC
4. Bot also sends a QR code image containing the UIC
5. User can scan the QR code with any QR scanner to see their UIC

### Technical Flow

1. **Generate UIC** - Normal UIC generation via `UICService`
2. **Create QR Code** - `QRCodeService` generates PNG image
3. **Save to Disk** - Saved to `static/qr_codes/MBEIBR7DA1.png`
4. **Build URL** - Constructs public URL (e.g., `https://your-server.com/static/qr_codes/MBEIBR7DA1.png`)
5. **Send via Twilio** - Attaches image URL to WhatsApp message using `media_url`

## Installation

### 1. Install Dependencies

```bash
# Install the qrcode library with PIL support
pip install qrcode[pil]

# Or install all dependencies
pip install -e .
```

### 2. Enable Feature

Add to your `.env` file:

```bash
ENABLE_QR_CODE=true
```

### 3. Restart Application

```bash
# Stop the application
# Then restart
python -m app.main
```

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_QR_CODE` | boolean | `false` | Enable/disable QR code generation |

### Static Files

When enabled, FastAPI serves QR codes from:
- **Directory**: `static/qr_codes/`
- **URL Pattern**: `/static/qr_codes/{UIC}.png`
- **Example**: `https://your-server.com/static/qr_codes/MBEIBR7DA1.png`

## For Twilio Sandbox (Testing)

✅ **Works immediately** with Twilio sandbox - no additional configuration needed.

Twilio will:
1. Fetch the QR code image from your server
2. Deliver it to the user via WhatsApp

**Requirements:**
- Your server must be publicly accessible via HTTPS
- ngrok can be used for local testing

## For Meta Cloud API (Production)

⚠️ **Requires additional work** for production deployment with Meta's WhatsApp Cloud API.

### Option 1: Upload to Meta First

Meta Cloud API requires uploading media to their servers first:

```python
# 1. Upload QR code to Meta
POST https://graph.facebook.com/v18.0/{phone_number_id}/media
Content-Type: multipart/form-data

# 2. Get media_id
response = {"id": "media_id_here"}

# 3. Send message with media_id
POST https://graph.facebook.com/v18.0/{phone_number_id}/messages
{
  "messaging_product": "whatsapp",
  "to": "{recipient_number}",
  "type": "image",
  "image": {
    "id": "media_id_here",
    "caption": "Your UIC: MBEIBR7DA1"
  }
}
```

### Option 2: Use Public URL

Meta can also fetch from public HTTPS URLs:

```python
{
  "messaging_product": "whatsapp",
  "to": "{recipient_number}",
  "type": "image",
  "image": {
    "link": "https://your-server.com/static/qr_codes/MBEIBR7DA1.png",
    "caption": "Your UIC: MBEIBR7DA1"
  }
}
```

**Requirements:**
- Must be publicly accessible HTTPS URL
- No authentication required
- Image must be < 5MB

## File Structure

```
whatsapp-uic-generator/
  app/
    services/
      qr_service.py          # QR code generation logic
    main.py                  # Static files mounting
    api/
      webhook.py             # QR code integration
  static/
    qr_codes/
      .gitkeep               # Keep directory in git
      MBEIBR7DA1.png         # Generated QR codes (not in git)
  tests/
    test_qr_service.py       # QR service tests
```

## Storage Management

### Automatic Cleanup (Optional)

QR codes are stored permanently by default. To enable auto-cleanup:

```python
# In a scheduled task or cron job
from app.services.qr_service import QRCodeService

qr_service = QRCodeService()
# Delete QR codes older than 7 days
deleted_count = qr_service.cleanup_old_qr_codes(max_age_days=7)
```

### Manual Cleanup

```bash
# Delete all QR codes
rm static/qr_codes/*.png

# Or keep the directory
rm static/qr_codes/*.png && touch static/qr_codes/.gitkeep
```

## Security Considerations

### 1. Public URLs

QR code images are publicly accessible at predictable URLs:
- `https://your-server.com/static/qr_codes/MBEIBR7DA1.png`

**Mitigation:**
- UICs are already privacy-preserving (hashed, no PII)
- Consider temporary URLs that expire
- Or implement authentication middleware

### 2. Storage

QR codes are stored on disk:
- Could grow over time if not cleaned up
- Consider cloud storage (S3, R2) for production

### 3. HTTPS Required

All QR code URLs must use HTTPS in production for WhatsApp delivery.

## Testing

### Test QR Code Generation

```bash
# Run the test
python tests/test_qr_service.py
```

Expected output:
```
✅ QR code generated successfully!
   File: static/qr_codes/MBEIBR7DA1.png
   Size: 1234 bytes
✅ QR code file verified at: static/qr_codes/MBEIBR7DA1.png
✅ QR code retrieval works correctly
✅ QR code cleanup works correctly

🎉 All QR code tests passed!
```

### Test End-to-End

1. Set `ENABLE_QR_CODE=true` in `.env`
2. Restart application
3. Send message to WhatsApp bot
4. Complete the 5 questions
5. Verify you receive both:
   - Text message with UIC
   - QR code image

### Test with ngrok (Local Development)

```bash
# Start ngrok
ngrok http 8000

# Update Twilio webhook to ngrok URL
https://abc123.ngrok.io/whatsapp/webhook

# Test bot - QR codes will be served via ngrok
```

## Troubleshooting

### QR Code Not Appearing

**Check 1**: Feature enabled?
```bash
grep ENABLE_QR_CODE .env
# Should show: ENABLE_QR_CODE=true
```

**Check 2**: Dependencies installed?
```bash
pip list | grep qrcode
# Should show: qrcode 7.4.0 or higher
```

**Check 3**: Static directory exists?
```bash
ls -la static/qr_codes/
# Should exist with .gitkeep file
```

**Check 4**: Check logs
```bash
grep "QR code" logs/app.log
# Should show QR generation and attachment
```

### "Image Not Found" Error

**Issue**: Twilio can't fetch the QR code

**Solutions**:
1. Verify server is publicly accessible
2. Check HTTPS is working
3. Test URL manually: `curl https://your-server.com/static/qr_codes/MBEIBR7DA1.png`
4. Check file permissions on `static/` directory

### QR Code File Permission Errors

```bash
# Fix permissions
chmod 755 static/qr_codes
chmod 644 static/qr_codes/*.png
```

## Performance Impact

### When Disabled (Default)

- **Zero impact** - QRCodeService is not initialized
- No additional dependencies loaded
- No file operations

### When Enabled

- **QR Generation**: ~50-100ms per code
- **File Write**: ~10-20ms
- **Total Overhead**: ~100ms per UIC generation
- **Disk Usage**: ~1-2 KB per QR code image

## Recommendations

### For Testing/POC

✅ **Enable it!** Works great with Twilio sandbox.

```bash
ENABLE_QR_CODE=true
```

### For Production

Consider:
- Storage strategy (local vs cloud)
- Cleanup policy (auto-delete after X days)
- URL security (temporary signed URLs)
- Meta Cloud API integration

## Support

For issues or questions about the QR code feature:
1. Check logs: `logs/app.log`
2. Run tests: `python tests/test_qr_service.py`
3. Review this guide
4. Check the GitHub repository

---

**Last Updated**: January 17, 2026  
**Feature Version**: 1.0  
**Status**: Production-ready for Twilio, Requires adaptation for Meta Cloud API
