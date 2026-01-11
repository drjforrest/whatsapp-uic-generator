# WhatsApp UIC Generator

A production-quality WhatsApp bot for generating Unique Identifier Codes (UICs) in the Democratic Republic of Congo (DRC) healthcare context. Built with FastAPI, Twilio, and SQLite.

## 🎯 Overview

This bot conducts an interactive conversation via WhatsApp to collect user information and generate a deterministic, privacy-preserving Unique Identifier Code. The same person will always receive the same UIC when providing the same information.

### Key Features

- **🔐 Privacy-Preserving**: Uses SHA-256 hashing with salt to generate anonymous yet deterministic codes
- **🌍 DRC Context-Aware**: Handles French accents, various name spellings, and local health zone data
- **💬 Interactive Flow**: Natural conversation flow with validation and error handling
- **📊 Production-Quality**: Structured logging, database persistence, comprehensive error handling
- **🔄 Duplicate Detection**: Prevents duplicate registrations automatically
- **🚀 Easy Deployment**: Works with Twilio sandbox and ngrok for POC, ready for production

## 📋 Requirements

- Python 3.12+
- Twilio account (free tier works for POC)
- ngrok (for local development with HTTPS)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
cd whatsapp-uic-generator

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Generate Secure Salt

```bash
python scripts/generate_salt.py
```

Copy the generated salt to your `.env` file.

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values:
# - UIC_SALT: Use the salt from step 2
# - TWILIO_ACCOUNT_SID: From Twilio Console
# - TWILIO_AUTH_TOKEN: From Twilio Console
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### 6. Expose with ngrok

In a new terminal:

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 7. Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to WhatsApp Sandbox
3. Set "When a message comes in" to: `https://your-ngrok-url.ngrok.io/whatsapp/webhook`
4. Save

### 8. Test on WhatsApp

1. Join the Twilio Sandbox (follow instructions in Twilio Console)
2. Send any message to start the conversation
3. Follow the prompts to generate your UIC

## 📖 How It Works

### Conversation Flow

The bot asks 5 questions in sequence. **Current questions are PLACEHOLDERS** - customize them for your use case!

Current placeholder questions (users provide full information):
1. **What year were you born?** → System extracts last 3 digits
2. **Where was your mother born?** → System extracts first 4 letters
3. **What is your first name?** → System extracts first 3 letters
4. **What day of the month were you born?** → System uses the number
5. **What is your family name?** → System extracts first 4 letters

**See [CUSTOMIZING_QUESTIONS.md](CUSTOMIZING_QUESTIONS.md) for how to change these to your actual questions.**

### UIC Generation

The UIC format (based on placeholder questions): `YYY-MMMMDD-FNNN-LLLL-HHHHH`

- **YYY**: Last 3 digits of birth year (Q1)
- **MMMM**: First 4 letters of mother's birthplace (Q2)
- **DD**: Day of month (Q4)
- **FNNN**: First 3 letters of first name (Q3)
- **LLLL**: First 4 letters of family name (Q5)
- **HHHHH**: 5-character hash for uniqueness

Example: `985-KINS15-JEA-KABI-A3F9D`

**Note**: This format matches the placeholder questions. Customize it for your actual questions in `app/services/uic_service.py`.

### Privacy & Security

- All inputs are normalized (accents removed, uppercase)
- SHA-256 hash with secure salt ensures privacy
- Same inputs always produce the same UIC
- No raw PII is stored after UIC generation
- Database records are encrypted at rest (in production)

## 🏗️ Architecture

```
app/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── database.py            # Database setup and session management
├── logging_config.py      # Structured logging configuration
├── models/
│   └── uic.py            # SQLAlchemy models
├── services/
│   ├── uic_service.py    # UIC generation logic
│   └── flow_manager.py   # Conversation flow management
└── api/
    └── webhook.py        # Twilio webhook endpoints
```

## 🔧 Configuration

All configuration is done via environment variables in `.env`:

| Variable | Description | Required |
|----------|-------------|----------|
| `UIC_SALT` | Secure salt for hashing (min 16 chars) | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Yes |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Yes |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | No (defaults to sandbox) |
| `DATABASE_URL` | SQLAlchemy database URL | No (defaults to SQLite) |
| `SESSION_TIMEOUT_MINUTES` | Session expiration time | No (default: 15) |
| `LOG_LEVEL` | Logging level | No (default: INFO) |
| `DEBUG` | Enable debug mode | No (default: False) |

## 📊 Database Schema

### UICRecord Table

Stores all generated UICs with:
- UIC code and creation timestamp
- Normalized input data for duplicate detection
- Request count and last requested time
- Phone number for audit trail

### ConversationSession Table

Manages conversation state:
- Current step in conversation
- Collected answers
- Session expiration
- Language preference

## 🧪 Testing

### Manual Testing

Send these commands in WhatsApp:

- `RESTART` - Start a new conversation
- `HELP` - Show help message

### Automated Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_uic_service.py
```

## 🚀 Deployment

### Production Considerations

**DO NOT use for production:**
- SQLite (use PostgreSQL instead)
- Twilio Sandbox (get verified WhatsApp Business number)
- ngrok (use proper hosting with SSL)

**DO use for production:**
- All other code and architecture
- Database models and schema
- Security practices (salt, hashing)
- Error handling and logging

### Deployment Options

1. **Heroku/Render**: Easy deployment with automatic SSL
2. **AWS Lambda**: Serverless with API Gateway
3. **DigitalOcean/AWS EC2**: Traditional VPS hosting
4. **Docker**: Containerized deployment (Dockerfile needed)

### Environment Variables in Production

Ensure all sensitive values are:
- Stored in secure secret management (AWS Secrets Manager, etc.)
- Never committed to version control
- Rotated regularly
- Backed up securely

## 📝 Commands Reference

### Special WhatsApp Commands

- `RESTART` - Clear session and start over
- `HELP` - Display help information

### API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /whatsapp/webhook` - Main webhook (called by Twilio)
- `GET /whatsapp/health` - Webhook health check
- `POST /whatsapp/cleanup` - Manual session cleanup

## 🐛 Troubleshooting

### "Configuration error: UIC salt must be at least 16 characters"

Run `python scripts/generate_salt.py` and add the generated salt to `.env`

### "Twilio webhook returns 404"

Ensure:
1. ngrok is running and forwarding to port 8000
2. Twilio webhook URL includes `/whatsapp/webhook`
3. Your FastAPI server is running

### "Session expired" messages

Increase `SESSION_TIMEOUT_MINUTES` in `.env` or respond faster during testing

### Database errors

Re-run `python scripts/init_db.py` to recreate tables

## 📚 Additional Documentation

See [SETUP.md](SETUP.md) for detailed setup instructions.

## 🎨 Customization

### Changing the Questions

The bot currently uses placeholder questions. To customize:

1. Edit `app/services/flow_manager.py`
2. Modify the `STEPS` list with your questions
3. Choose appropriate validators
4. Test thoroughly

**See [CUSTOMIZING_QUESTIONS.md](CUSTOMIZING_QUESTIONS.md) for detailed instructions.**

### Supported Languages

- English (default)
- French (built-in)
- Add more by editing question text in `flow_manager.py`

## 🤝 Contributing

This is a proof-of-concept for DRC healthcare context. For production use, consider:

1. Customizing the 5 questions for your specific use case
2. Adding language selection (French/Lingala/others)
3. Implementing Redis for session management
4. Adding authentication for admin endpoints
5. Creating admin dashboard for UIC management
6. Adding analytics and reporting

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

Jamie Forrest - Applied Data Scientist specializing in global health and contextual integrity

## 🙏 Acknowledgments

Built for healthcare workers and researchers in the Democratic Republic of Congo working on privacy-preserving patient identification systems.

---

**⚠️ POC Notice**: This implementation uses SQLite, Twilio Sandbox, and ngrok for proof-of-concept. For production deployment, these should be replaced with PostgreSQL, verified WhatsApp Business number, and proper hosting infrastructure.
