# Twilio WhatsApp Sandbox Setup

## Step 1: Find Your Sandbox Details

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. You'll see:
   - **Sandbox phone number** (e.g., `+1 415 523 8886`)
   - **Your join code** (e.g., `join clever-house`)

## Step 2: Join the Sandbox on WhatsApp

1. **Save the number**: Save the sandbox number in your phone contacts
   - Name it something like "Twilio Sandbox"

2. **Open WhatsApp** on your phone

3. **Send the join message**:
   - Open a chat with the Twilio Sandbox number
   - Send your unique join code (e.g., `join clever-house`)
   - You should receive a confirmation message within seconds

**Example:**
```
You: join clever-house

Twilio Sandbox:
✅ Twilio Sandbox: ⚡️ Congratulations! You've joined the sandbox!
You can now send/receive messages in this conversation.
```

## Step 3: Configure Your Webhook

**IMPORTANT**: Before testing, you must set up your webhook URL!

1. On the same Twilio Sandbox page, scroll down to **"Sandbox Configuration"**

2. Find the field: **"When a message comes in"**

3. Enter your webhook URL:
   - Format: `https://your-ngrok-url.ngrok.io/whatsapp/webhook`
   - Method: **POST**

4. Click **"Save"**

### Getting Your ngrok URL:

```bash
# Start your FastAPI server (terminal 1)
uvicorn app.main:app --reload

# Start ngrok (terminal 2)
ngrok http 8000

# Copy the HTTPS URL from ngrok output
# Example: https://abc123def456.ngrok.io
```

Then set webhook to: `https://abc123def456.ngrok.io/whatsapp/webhook`

## Step 4: Test Your Bot!

1. In WhatsApp, send any message to the Twilio Sandbox number
2. You should receive the welcome message from your bot
3. Answer the 5 questions
4. Receive your UIC!

## Troubleshooting

### "No response from bot"

**Check:**
1. ✅ FastAPI server is running (`uvicorn app.main:app --reload`)
2. ✅ ngrok is running (`ngrok http 8000`)
3. ✅ Webhook URL is set correctly in Twilio (with `/whatsapp/webhook`)
4. ✅ You've joined the sandbox (send join code first)

**View logs:**
- Check your FastAPI terminal for incoming requests
- Check Twilio Console → Monitor → Logs → Errors

### "Invalid join code"

- Make sure you're using YOUR unique join code from the Twilio Console
- Each Twilio account has a different join code
- The code changes if you regenerate it

### "Need to rejoin sandbox"

Sandbox connections expire after 3 days of inactivity. Just send the join code again.

## Common Sandbox Numbers

Most Twilio accounts use one of these:
- `+1 415 523 8886` (US)
- Different numbers for other regions

But always check your console for YOUR specific number!

## Next Steps After Sandbox

For production:
1. Get a verified WhatsApp Business Account
2. Register your own phone number
3. Get approved by WhatsApp
4. Update `.env` with your production number

For POC/testing, the sandbox works perfectly! 🎉
