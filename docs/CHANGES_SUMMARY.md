# Code Changes Summary - UIC Format Update

**Date**: January 17, 2026
**Purpose**: Update UIC format and convert all bot messages to French for DRC deployment

## UIC Format Changes

### Old Format: `LLLFFFYCCG` (10 characters)
- LLL = First 3 letters of last name
- FFF = First 3 letters of first name
- Y = Last digit of birth year
- CC = 2-digit city code (e.g., "12")
- G = Gender code (M or F)
- Example: `KABJEA512M`

### New Format: `LLLFFFYCG` (10 characters)
- LLL = First 3 letters of last name
- FFF = First 3 letters of first name
- Y = Last digit of birth year (1 digit)
- C = 2-letter city code (e.g., "DA" for Dakar)
- G = Gender code (1 digit: 1=Homme, 2=Femme, 3=Trans, 4=Autre)
- Example: `MBEIBR7DA1`

## Files Modified

### 1. `app/services/flow_manager.py`
**Changes:**
- ✅ Added new validator `validate_gender_code()` - accepts 1, 2, 3, or 4
- ✅ Added new validator `validate_city_code()` - accepts exactly 2 letters
- ✅ Updated `validate_digits_only()` - French error messages
- ✅ Updated `validate_letters_only()` - French error messages
- ✅ Updated all conversation steps with French questions
- ✅ Updated UIC formula documentation in comments
- ✅ Changed default language from "en" to "fr"
- ✅ Updated WELCOME_MESSAGE_FR
- ✅ Updated COMPLETION_MESSAGE_FR
- ✅ Updated HELP message to French
- ✅ Updated RESTART message to French
- ✅ Changed "Got it!" to "Compris!"

**Question Examples:**
```
Question 1 sur 5:

Quelles sont les 3 premières lettres de votre nom de famille?

Exemple: MBE
```

```
Question 2 sur 5:

Quelles sont les 3 premières lettres de votre prénom?

Exemple: IBR
```

```
Question 5 sur 5:

Quel est votre code de genre?

1 = Homme
2 = Femme
3 = Trans
4 = Autre
```

### 2. `app/services/uic_service.py`
**Changes:**
- ✅ Updated `_generate_uic_code()` documentation
- ✅ Updated UIC formula comments: `LLLFFFYCCG` → `LLLFFFYCG`
- ✅ Changed city code handling from `rjust(2, '0')` to `ljust(2, 'X')` (letters not digits)
- ✅ Changed gender code handling (1 digit instead of M/F)
- ✅ Updated example in docstring: `KABJEA512M` → `MBEIBR7DA1`

### 3. `app/api/webhook.py`
**Changes:**
- ✅ Updated success message to French
- ✅ Updated existing UIC message to French
- ✅ Updated error message to French
- ✅ Changed "UIC" to "CIU" (Code d'Identification Unique)

**Final Message Examples:**
```
🎉 Votre Code d'Identification Unique a été généré!

📋 Votre CIU:
==============
  MBEIBR7DA1
==============

✅ Ce code est maintenant enregistré à votre nom.
```

### 4. `tests/test_uic_service.py`
**Changes:**
- ✅ Updated all test examples to use new format
- ✅ Changed `KABJEA512M` → `MBEIBR7DA1`
- ✅ Updated gender codes from M/F to 1/2
- ✅ Updated city codes from digits to letters
- ✅ Fixed padding tests for letter-based city codes

## Validation Rules

### Gender Code
- **Accepts**: 1, 2, 3, or 4
- **Rejects**: Any other number, letters, or special characters
- **Error message**: "Le code de genre doit être 1, 2, 3 ou 4"

### City Code
- **Accepts**: Exactly 2 letters (A-Z, case insensitive)
- **Rejects**: Numbers, special characters, or wrong length
- **Error message**: "Le code de ville doit contenir exactement 2 lettres"

### Birth Year
- **Accepts**: Single digit (0-9)
- **Error message**: "Veuillez entrer uniquement des chiffres"

## Testing

All tests updated to reflect new format. Run tests with:
```bash
pytest tests/test_uic_service.py -v
```

## Deployment Notes

1. All bot messages are now in French as required for DRC deployment
2. README.md still needs to be updated (pending approval)
3. City code validation accepts any 2 letters (no specific city list validation)
4. UIC length remains 10 characters
5. **NEW**: QR code feature available - toggle with `ENABLE_QR_CODE=true` in .env

## QR Code Feature (NEW)

### Overview
Optional feature that generates and sends QR codes containing the UIC to users via WhatsApp.

### How to Enable
Add to `.env` file:
```bash
ENABLE_QR_CODE=true
```

### How It Works
1. When enabled, after generating a UIC, a QR code image is created
2. QR code is saved to `static/qr_codes/MBEIBR7DA1.png`
3. Image is served via FastAPI static files at `/static/qr_codes/MBEIBR7DA1.png`
4. Twilio sends the image along with the text message using `media_url`

### Files Added
- `app/services/qr_service.py` - QR code generation service
- `static/qr_codes/` - Directory for storing QR code images
- `static/qr_codes/.gitkeep` - Keeps directory in git

### Files Modified for QR Feature
- `pyproject.toml` - Added `qrcode[pil]>=7.4.0` dependency
- `app/config.py` - Added `enable_qr_code` boolean setting
- `app/main.py` - Mount static files directory when feature enabled
- `app/api/webhook.py` - Generate and attach QR code to message
- `.env.example` - Added `ENABLE_QR_CODE` variable
- `.gitignore` - Ignore generated PNG files but keep directory

### Installation
```bash
pip install -e .
# or
pip install qrcode[pil]
```

### Notes
- Works with Twilio sandbox immediately
- For Meta Cloud API production, may require different approach (upload to Meta first)
- QR codes are stored permanently (optional cleanup available)
- Feature is completely optional - disabled by default
- No impact on performance when disabled
