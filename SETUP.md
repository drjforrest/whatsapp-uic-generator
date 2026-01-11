# Setup Guide - WhatsApp UIC Generator

Detailed step-by-step setup instructions for the WhatsApp UIC Generator.

## Prerequisites

Before starting, ensure you have:

- [ ] Python 3.12 or higher installed
- [ ] pip package manager
- [ ] A Twilio account (free tier is sufficient)
- [ ] ngrok installed for local HTTPS tunneling
- [ ] A WhatsApp-capable phone

## Step 1: Python Environment Setup

### 1.1 Check Python Version

```bash
python3 --version
# Should show Python 3.12 or higher
```

### 1.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows
```

You should see `(.venv)` in your terminal prompt.

### 1.3 Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install the package in editable mode
pip install -e .

# Verify installation
python -c "import fastapi; print('FastAPI installed successfully')"
```

## Step 2: Twilio Setup

### 2.1 Create Twilio Account

1. Go to [Twilio Sign Up](https://www.twilio.com/try-twilio)
2. Complete registration (free trial works perfectly)
3. Verify your phone number

### 2.2 Access WhatsApp Sandbox

1. Log into [Twilio Console](https://console.twilio.com/)
2. Navigate to: **Messaging** → **Try it out** → **Send a WhatsApp message**
3. You'll see a sandbox number (e.g., `+1 415 523 8886`)
4. You'll see a join code (e.g., `join side-orbit`)

### 2.3 Join Sandbox on Your Phone

1. Save the Twilio sandbox number in your phone
2. Send the join code via WhatsApp to that number
3. Wait for confirmation message

### 2.4 Get Your Credentials

1. In Twilio Console, go to **Account** → **Settings**
2. Copy your **Account SID**
3. Copy your **Auth Token** (click to reveal)

**Keep these secret!**

## Step 3: Generate Security Salt

The UIC salt is critical for security and uniqueness.

```bash
# Generate a secure salt
python scripts/generate_salt.py
```

This will output something like:

```
🔐 UIC Salt Generator
==================================================

Generated salt (length: 43 characters):

  xY9kL2mN4pQ6rS8tU0vW1xY3zA5bC7dE9fG1hI3jK5

📋 Add this to your .env file:

  UIC_SALT="xY9kL2mN4pQ6rS8tU0vW1xY3zA5bC7dE9fG1hI3jK5"

⚠️  Keep this secret and never commit it to version control!
```

**Copy the generated salt** - you'll need it in the next step.

## Step 4: Configure Environment Variables

### 4.1 Create .env File

```bash
# Copy the example
cp .env.example .env

# Edit with your favorite editor
nano .env
# OR
vim .env
# OR
code .env  # VS Code
```

### 4.2 Fill in Values

Update these required fields in `.env`:

```bash
# Security - PASTE YOUR GENERATED SALT HERE
UIC_SALT="xY9kL2mN4pQ6rS8tU0vW1xY3zA5bC7dE9fG1hI3jK5"

# Twilio Configuration - PASTE YOUR CREDENTIALS HERE
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token_here"

# Leave this as default for sandbox
TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886"
```

### 4.3 Verify Configuration

```bash
# Test that config loads correctly
python -c "from app.config import settings; print(f'Config OK: {settings.app_name}')"
```

Should output: `Config OK: WhatsApp UIC Generator`

## Step 5: Initialize Database

### 5.1 Create Database Tables

```bash
python scripts/init_db.py
```

You should see:

```
✅ Database tables created successfully!
Database file location: ./uic_database.db
```

### 5.2 Verify Database

```bash
# Check that database file exists
ls -lh uic_database.db

# Optional: Inspect with sqlite3
sqlite3 uic_database.db ".tables"
# Should show: conversation_sessions  uic_records
```

## Step 6: Start the Application

### 6.1 Run FastAPI Server

```bash
# Start with auto-reload (development mode)
uvicorn app.main:app --reload --port 8000

# You should see:
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open!**

### 6.2 Test Locally

Open a new terminal and test the health endpoint:

```bash
curl http://localhost:8000/health
```

Should return:

```json
{
  "status": "healthy",
  "service": "WhatsApp UIC Generator",
  "version": "0.1.0"
}
```

## Step 7: Expose with ngrok

### 7.1 Install ngrok

**macOS:**
```bash
brew install ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

**Windows:**
Download from [ngrok.com/download](https://ngrok.com/download)

### 7.2 Create ngrok Account (Optional but Recommended)

1. Go to [ngrok.com](https://ngrok.com)
2. Sign up for free account
3. Get your authtoken
4. Configure: `ngrok config add-authtoken YOUR_TOKEN`

### 7.3 Start ngrok Tunnel

In a **new terminal**:

```bash
ngrok http 8000
```

You'll see output like:

```
Session Status                online
Account                       your@email.com
Version                       3.x.x
Region                        United States (us)
Forwarding                    https://abc123xyz.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123xyz.ngrok.io`)

**Keep this terminal open!**

### 7.4 Test ngrok Tunnel

```bash
# In another terminal
curl https://abc123xyz.ngrok.io/health
```

Should return the same health check response.

## Step 8: Configure Twilio Webhook

### 8.1 Set Webhook URL

1. Go back to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Scroll to **Sandbox Configuration**
4. Find **"When a message comes in"**
5. Set to: `https://abc123xyz.ngrok.io/whatsapp/webhook` (use YOUR ngrok URL)
6. Set HTTP method to **POST**
7. Click **Save**

### 8.2 Verify Webhook

Twilio will test the webhook when you save. You should see:

- ✅ Green checkmark next to the URL
- In your FastAPI terminal: `INFO: Received WhatsApp message...` (if they send test message)

## Step 9: Test the Bot!

### 9.1 Start Conversation

On your phone, open WhatsApp and send **any message** to the Twilio sandbox number.

You should receive:

```
👋 Welcome to the UIC Generator!

I will ask you 5 questions to generate your Unique Identifier Code (UIC).

📋 Your UIC is:
• Unique to you
• Private and secure
• Can be regenerated if needed

Type RESTART anytime to start over.
Type HELP for assistance.

Let's begin! 🚀

What is your first name? (Prénom)

Example: Jean
```

### 9.2 Complete Conversation

Answer the 5 questions:

1. **First name**: Jean
2. **Last name**: Kabila
3. **Birth year**: 1985
4. **Mother's initial**: M
5. **Health zone**: Kinshasa

You should receive your UIC:

```
🎉 Your Unique Identifier Code has been generated!

📋 Your UIC:
━━━━━━━━━━━━━━
  JEKA-85M-A3F9D
━━━━━━━━━━━━━━

✅ This code is now registered in your name.

💡 Save this code! You can request it again by starting a new conversation.

Type RESTART to generate a new UIC or update information.
```

### 9.3 Test Commands

- Type `RESTART` - Should start a new conversation
- Type `HELP` - Should show help message

### 9.4 Test Duplicate Detection

Start a new conversation (type `RESTART`) and answer with the **exact same information**.

You should receive:

```
📋 Your existing UIC:
━━━━━━━━━━━━━━
  JEKA-85M-A3F9D
━━━━━━━━━━━━━━

ℹ️ This code was previously generated with the same information.

Type RESTART if you need to update your information.
```

## Step 10: Monitor and Debug

### 10.1 Watch Logs

In your FastAPI terminal, you'll see structured logs:

```
INFO: Received WhatsApp message phone_number="+1234567890" message_length=4
INFO: Found existing session phone_number="+1234567890" step=1
INFO: Answer stored phone_number="+1234567890" step="first_name"
```

### 10.2 Inspect Database

```bash
# View all UICs
sqlite3 uic_database.db "SELECT uic_code, phone_number, created_at FROM uic_records;"

# Count total UICs
sqlite3 uic_database.db "SELECT COUNT(*) FROM uic_records;"

# View active sessions
sqlite3 uic_database.db "SELECT phone_number, current_step FROM conversation_sessions;"
```

### 10.3 Common Issues

**Issue: "Configuration error: UIC salt..."**
- Solution: Re-run `python scripts/generate_salt.py` and update `.env`

**Issue: Webhook returns 404**
- Check ngrok URL is correct
- Ensure webhook path is `/whatsapp/webhook`
- Verify FastAPI server is running

**Issue: No response in WhatsApp**
- Check FastAPI terminal for errors
- Verify webhook is saved in Twilio
- Test webhook URL directly with curl

**Issue: "Session expired"**
- Sessions expire after 15 minutes
- Type RESTART to begin again
- Increase `SESSION_TIMEOUT_MINUTES` in `.env` for longer sessions

## Step 11: Optional Enhancements

### 11.1 Enable Debug Mode

In `.env`:

```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

Restart the server. You'll now see detailed debug logs and can access:
- API docs at `http://localhost:8000/docs`
- ReDoc at `http://localhost:8000/redoc`

### 11.2 Add French Language Support

The bot has French questions built-in. To enable:

1. Edit `app/services/flow_manager.py`
2. Modify `WELCOME_MESSAGE_EN` to `WELCOME_MESSAGE_FR`
3. Add language detection logic

### 11.3 Session Cleanup

Run periodic cleanup of expired sessions:

```bash
# Manual cleanup
curl -X POST http://localhost:8000/whatsapp/cleanup
```

For production, add this to a cron job.

## Next Steps

- [ ] Test with multiple users
- [ ] Verify duplicate detection works correctly
- [ ] Test with French accents (Gédéon, François)
- [ ] Review logs for any errors
- [ ] Plan production deployment strategy

## Production Deployment

See [README.md](README.md) for production deployment considerations.

**Remember:** For production, replace:
- SQLite → PostgreSQL
- Twilio Sandbox → Verified WhatsApp Business Number
- ngrok → Proper hosting with SSL (Heroku, AWS, etc.)

## Support

If you encounter issues:

1. Check the logs in your FastAPI terminal
2. Verify all configuration in `.env`
3. Test endpoints with curl
4. Review Twilio webhook logs in console

---

**🎉 Congratulations!** You now have a fully functional WhatsApp UIC Generator bot!
