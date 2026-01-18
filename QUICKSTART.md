# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- git
- Python 3.12+
- Twilio account (development only)
- ngrok installed
- Meta Cloud account

**NOTE** This QuickStart guide and the accompanying README.md are prepared for deployment on a Linux server. For deployment on a Windows server (rare, but possible), there is a rough guide in the FR directory, but I cannot confirm its accuracy.

## 0. Clone the Repository
```
git clone https://github.com/drjforrest/whatsapp-uic-generator.git
cd whatsapp-uic-generator
```

## 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## 2. Generate Security Salt

```bash
python scripts/generate_salt.py
```

Copy the output.

## 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with:
# - Generated salt
# - Twilio credentials (from console.twilio.com)
```

## 4. Initialize Database

```bash
python scripts/init_db.py
```

## 5. Start Services

**Terminal 1 - FastAPI:**
```bash
./scripts/run_dev.sh
# OR: uvicorn app.main:app --reload
```

**Terminal 2 - ngrok:**
```bash
ngrok http 8000
# Copy the HTTPS URL
```

## 6. Configure Twilio

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to WhatsApp Sandbox
3. Set webhook to: `https://YOUR-NGROK-URL/whatsapp/webhook`
4. Save

## 7. Test on WhatsApp

1. Join Twilio sandbox (send join code to sandbox number)
2. Send any message to start
3. Answer 5 placeholder questions (provide full information):
   - What year were you born? (e.g., 1985)
   - Where was your mother born? (e.g., Kinshasa)
   - What is your first name? (e.g., Jean)
   - What day were you born? (e.g., 15)
   - What is your family name? (e.g., Kabila)
4. Receive your UIC!

**Note**: These are placeholder questions - the system automatically extracts what it needs (first letters, last digits, etc.). See [CUSTOMIZING_QUESTIONS.md](CUSTOMIZING_QUESTIONS.md) to change them.

## Test Commands

- `RESTART` - Start over
- `HELP` - Show help

## Troubleshooting

**No response?**
- Check FastAPI terminal for errors
- Verify ngrok is running
- Confirm webhook URL in Twilio

**Configuration error?**
- Re-run `python scripts/generate_salt.py`
- Check `.env` has all required fields

**Database error?**
- Re-run `python scripts/init_db.py`

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed instructions
- Read [README.md](README.md) for architecture details
- Run tests: `pytest tests/`

## Production Notes

For production, replace:
- ✅ SQLite → PostgreSQL
- ✅ Twilio Sandbox → Verified WhatsApp Business
- ✅ ngrok → Proper hosting (Heroku, AWS, etc.)

All other code is production-ready!
