# DRC Backgrounder on UUID Implementation
- Present 3 scenarios
	- Biometric fingerprinting - suggest an organization like Simprints and approximately how long it would take
	- ?
	- WhatsApp code retrieval
	Generating Unique Codes Now
	I'm currently focused on the practical implementation of a WhatsApp bot to issue Unique Identifier Codes (UIC). My thoughts center on the DRC context, anticipating language requirements (French/English) and cultural nuances for effective deployment. The goal is to design a system that is easily accessible and adaptable to the local population.
	Analyzing Low-Resource Issues
	I'm now deep-diving into the nitty-gritty of low-resource environments. The central issue is how to provide robust connectivity in the DRC context. My thought process has evolved to factor in the limited bandwidth and potential unreliability. I'm focusing on crafting a streamlined series of questions to generate unique codes. This will require me to carefully consider and define the question logic to ensure uniqueness. I've also figured out I need to use the WhatsApp Business Platform, and how to get set up.
	Establishing Bot Parameters
	My thoughts now revolve around the essential setup steps for the WhatsApp bot. I'm focusing on business verification requirements, a "clean" phone number, and message templates, specifically considering both "Business-Initiated" and "User-Initiated" flows. Also, I need to decide on hosting the UIC generation logic. I'm also carefully crafting the bot's tone and exploring the need for ethical considerations regarding privacy and data security. Finally, I'm confirming up-to-date WhatsApp API requirements and remembering to mention the easier-to-use Cloud API.
	Hi Jamie, this sounds like a critical project. Implementing a Unique Identifier Code (UIC) in the DRC—especially for healthcare or clinical research—requires a solution that is both accessible and robust. WhatsApp is an excellent choice for the DRC context given its high penetration and low data requirements.
	To develop an official WhatsApp bot (rather than using unofficial, risky "gray-market" libraries), you must use the WhatsApp Business Platform (Cloud API).
	Here are the specific steps to obtain the developer credentials and set up the environment:
	#### Step 1: Create a Meta Developer Account
	The WhatsApp API is managed through Meta’s developer portal.
	1. Go to developers.facebook.com.
	2. Log in with your Facebook account and complete the registration to become a "Meta Developer."
	3. Click "Create App."
	4. Select the "Other" use case, and then choose "Business" as the app type.
	#### Step 2: Set Up the WhatsApp Product
	1. Once the app is created, you will see a dashboard with various Meta products. Click "Set Up" on the WhatsApp tile.
	2. You will be asked to select or create a Meta Business Account (this is different from your personal profile).
	3. Meta will generate a Temporary Access Token and a Test Phone Number for you to begin development immediately.
	#### Step 3: Register a Production Phone Number
	To move out of the "Sandbox" environment:
	1. You need a phone number that is not currently registered with a personal or business WhatsApp app. (If it is, you must delete the existing account associated with that number).
	2. In the WhatsApp settings within the Meta Dashboard, go to "API Setup" and add your production number.
	3. You will verify this number via SMS or a voice call.
	#### Step 4: Obtain Permanent Credentials
	For a production bot in the DRC, you cannot use temporary tokens (which expire every 24 hours).
	1. Go to your Meta Business Suite (business.facebook.com).
	2. Go to Settings > Users > System Users.
	3. Create a new System User and generate a Permanent Access Token. Ensure you grant this user the whatsapp_business_messaging and whatsapp_business_management permissions.
	4. Note down three key IDs:
		- Phone Number ID: Identifies the specific number sending messages.
		- WhatsApp Business Account ID (WABA ID): Identifies your business entity.
		- Permanent Access Token: Your bearer token for API calls.
	#### Implementation Considerations for the UIC Bot
	Since you are an applied data scientist, you'll likely be handling the backend logic (the "UIC engine"). Here is how to structure the flow for the DRC context:
	#### 1. The Logic (The "Engine")
	Since the UIC must be unique but based on repeatable answers (e.g., first letters of name, birth year, gender, etc.), you will likely want to:
	- Have the bot collect 5–7 variables via a series of questions.
	- Pipe those strings into a hashing algorithm (like SHA-256) or a concatenation-based code.
	- Data Integrity: In the DRC, names can have various spellings. You might want to implement a "soundex" or fuzzy matching logic if you are checking for existing codes in a database.
	#### 2. Message Templates
	Under the WhatsApp Business API, if your bot initiates the conversation (Business-Initiated), you must use pre-approved templates. If the user starts the conversation (User-Initiated), the bot can respond with "Free-form" messages for a 24-hour window. For a UIC issuer, I recommend a user-initiated flow (e.g., "Text 'CODE' to start").
	#### 3. Webhook Setup
	You will need a backend server (using Flask/Python or Node.js) to receive the messages from Meta.
	- The Workflow: User sends message → Meta sends a Webhook (POST request) to your server → Your script processes the answer/calculates the UIC → Your server sends a POST request back to Meta to deliver the reply.
	#### 4. Privacy & Contextual Integrity
	Given your interest in contextual integrity and your work in global health:
	- Encryption: WhatsApp messages are encrypted in transit, but once they reach your webhook/database, they are "at rest." Ensure your backend complies with DRC's Law on Protection of Personal Data (or similar international standards like GDPR).
	- Anonymity: Since the UIC is often used to maintain anonymity in sensitive clinical settings (like HIV or TB research in the DRC), ensure the bot deletes the raw PII (Personally Identifiable Information) after generating the hash/code.
	Would you like a Python code snippet (using Flask) to handle the webhook part of this bot logic? I can also provide the instructions for using Ngrok to test the bot locally before deploying it to a server.




Developing a DRC UIC Bot
I'm currently focused on designing a WhatsApp bot for generating Unique Identifier Codes (UIC) in the DRC. The core function involves a question-and-response flow, which leads to the issuance of a unique code. The probability of duplicates needs rigorous assessment. I'm exploring FastAPI as a backend framework.
Evaluating Hosting Solutions
I've been examining hosting options for the UIC bot, comparing development/testing solutions like Ngrok with cloud services such as AWS, GCP, Azure, Heroku, and Digital Ocean for international deployment. The asynchronous nature of FastAPI, essential for handling high chat traffic, strongly supports its selection. To validate the choice, I've confirmed that the bot needs a public HTTPS endpoint for Meta's webhooks, and the need for state management (question tracking) and data persistence (user responses) has been identified, driving the need to choose between solutions such as Redis and database implementations.
Defining the Deployment Stack
I'm now solidifying the deployment strategy. Docker is non-negotiable for consistency. I'm focusing on securing the WhatsApp integration with SSL/HTTPS. My primary concerns are connectivity within the DRC, data sovereignty considerations, and the best way to handle the stateless nature of WhatsApp through a session manager. My current stack includes Python, FastAPI, Docker, Redis for state management, and Nginx as a reverse proxy. I'm assessing cloud platforms like Render or Heroku for initial deployment vs. AWS or GCP for scalability, with data residency in mind.
Prioritizing Backend Design
I'm now looking closely at the backend framework choices, mainly comparing FastAPI and Flask regarding scalability and concurrency, which are critical for the anticipated chat volume. I'm revisiting the "contextual integrity" concept, and how the UIC generation fits into a stateless or stateful backend.
You are absolutely correct. FastAPI is the superior choice over Flask for this use case, particularly because it is natively asynchronous.
Since WhatsApp interactions (webhooks) happen in real-time and often involve "bursty" traffic, FastAPI’s ability to handle concurrent requests without blocking is essential for a smooth user experience in the DRC.
#### 1. Why FastAPI for this UIC Engine?
- Asynchronicity: WhatsApp sends a separate POST request for every message sent by the user. FastAPI handles these async calls efficiently.
- Data Validation: Using Pydantic models within FastAPI allows you to strictly validate the inputs for the UIC (e.g., ensuring a birth year is exactly 4 digits) before the hashing algorithm ever touches them.
- Speed: It’s one of the fastest Python frameworks available, which helps keep the bot’s response time low on potentially unstable 3G/4G networks in the DRC.
#### 2. Hosting Requirements
To host a WhatsApp bot for the Meta Business API, your environment must meet these four specific requirements:
#### A. Public HTTPS Endpoint (SSL/TLS)
Meta will not send webhook data to an http:// address. It must be https://.
- For Development: Use ngrok to tunnel your local FastAPI port (usually 8000) to a public URL.
- For Production: You need a valid SSL certificate (Let's Encrypt is the standard and is free).
#### B. Persistence Layer (State Management)
This is the most critical technical hurdle. WhatsApp is stateless. Meta sends your server a "message received" event, but your server won't inherently know if this is the user's answer to Question 1 (First Name) or Question 5 (Village).
- Requirement: You need a small database or cache to track the "session state" for each phone_number.
- Recommendation: Redis is ideal for this. It’s a key-value store where you can store { "phone_number": "current_step_3" } with a 15-minute expiration.
#### C. Compute (Server)
- Cloud Providers:
	- Render or Fly.io: The easiest "Platform as a Service" (PaaS) options. They handle SSL automatically and integrate with GitHub.
	- AWS (Lambda or EC2): If you use AWS Lambda (via Mangum), you can have a "serverless" bot that only costs money when someone is actually using it.
	- DigitalOcean: A basic $5/month "Droplet" (VPS) is sufficient to handle thousands of UIC requests.
- Geographic Note: Since you are working in the DRC, consider hosting in an AWS Africa (Cape Town) or Azure South Africa region to minimize latency.
#### D. Containerization (Optional but Recommended)
I strongly recommend wrapping your FastAPI app in a Docker container. This ensures that the environment you build in Vancouver is identical to the one running on a server in the DRC or a cloud data center.
#### 3. Proposed Tech Stack for the UIC Bot
			Component
			Technology
			Language
			Python 3.10+
			API Framework
			FastAPI
			State/Session Management
			Redis (to track which question the user is on)
			UIC Logic
			Custom Python Class (likely using hashlib for SHA-256)
			Deployment
			Docker
			Web Server
			Uvicorn (running inside the container)
			Reverse Proxy
			Nginx (to handle SSL certificate)
#### A Note on Public Health Integrity
Since you have a background in contextual integrity and trust, you might consider where the salt for the UIC hash is stored. If the bot is meant to be truly privacy-preserving, the secret salt should be stored in an Environment Variable (never in the code) and the raw answers (Name, etc.) should be purged from the Redis cache the second the UIC is generated and sent back to the user.
Would you like me to draft a basic "Stateless-to-Stateful" logic flow in Python showing how to track the questions using Redis?

Initiating Demo Development
I'm starting a demo of a WhatsApp bot designed to generate UICs. I'm keen on circumventing the Meta Cloud account creation for now, sticking to a streamlined demo approach. My focus is on getting the basic functionality of the bot working, without getting bogged down by the complexities of API setup at this stage. I'll focus on Jamie's DRC project.
Evaluating API Alternatives
I've considered several API backbones, focusing on expediency, and have narrowed down viable options. Meta's strict requirements necessitate exploring alternatives. The Twilio WhatsApp Sandbox offers an industry-standard route. I'm also finding Telegram is an excellent proof-of-concept alternative, mirroring the API structure. I'm prioritizing minimal setup friction for this demonstration.
Exploring Demonstration Options
I'm now considering the best method for showcasing the UIC logic. I've realized that a Streamlit UI, designed for "Global Health" stakeholders, could effectively demonstrate the UIC generation process. The Twilio Sandbox offers a simple solution, avoiding Meta account setup. However, Telegram presents a truly free and instant option. I also want to address the friction of Meta's setup directly.
Choosing WhatsApp Implementation
I've decided to prioritize the Twilio WhatsApp Sandbox due to its balance of simplicity and functionality. The central element here is the "Simulated Session" logic – essentially, a state machine – that guides the conversation. I'm aiming to provide a concise code snippet for this, using FastAPI and a straightforward dictionary-based state system rather than Redis to keep things simple for now.
Yes, absolutely. In fact, for a researcher or consultant building a POC (Proof of Concept), I almost always recommend avoiding the Meta Cloud account initially. It is notoriously slow to set up and requires business verification that can take weeks.
Here are the three best ways to build a "look-feel-act" demo without a Meta account:
#### 1. The Twilio WhatsApp Sandbox (Recommended)
Twilio acts as a "proxy" between you and Meta. They have a pre-approved Meta Business account that you can use for testing.
- How it works: You create a free Twilio account, go to the WhatsApp Sandbox, and "join" the sandbox by texting a specific code (e.g., "join side-orbit") to a Twilio-owned WhatsApp number.
- Pros: You get to use the actual WhatsApp app on your phone.
- Setup time: 5 minutes.
- Integration: It works perfectly with FastAPI. You just point the Twilio Webhook URL to your FastAPI endpoint (using ngrok).
#### 2. The "Telegram Proxy" Method
From a logic standpoint, a Telegram bot and a WhatsApp bot are nearly identical: they are both Webhook-driven.
- How it works: You use Telegram's "BotFather" to create a bot in 30 seconds. You write your FastAPI code to handle Telegram’s JSON format instead of WhatsApp's.
- Pros: Zero friction, no "joining a sandbox" for every person who wants to test it, and it's 100% free.
- Key Insight: Since you are demonstrating the UIC generation logic and the user flow, the platform matters less than the experience. You can tell your DRC colleagues: "The logic is ready; we just swap the API connector when we move to production."
#### 3. Streamlit or Gradio (The "Web-Chat" Simulation)
If the goal is to show the DRC stakeholders how the variables (Name, DOB, Location) result in a unique UIC code and demonstrate that collisions are improbable:
- How it works: Use Streamlit. It’s a Python library used heavily in Data Science. You can build a "Chat-like" interface in about 50 lines of code.
- Pros: You don't need ngrok or any phone-based apps. You can host the demo on "Streamlit Community Cloud" for free, and anyone with a link can try it.
#### How to structure the Demo Logic (The "State Machine")
Regardless of which demo method you choose, you need a State Machine in your FastAPI app to remember which question the user is on. Since this is a demo, you can use a simple Python Dictionary instead of Redis to save time.
Example Demo Logic (FastAPI):
```from fastapi import FastAPI, Request
import hashlib

app = FastAPI()

# Temporary "Database" to track user progress
# In production, use Redis.
user_sessions = {}

QUESTIONS = [
    "What are the first two letters of your given name?",
    "What are the first two letters of your family name?",
    "In which year were you born? (YYYY)",
    "What is the first letter of your mother's given name?",
    "What is the name of the health zone where you were born?"
]

def generate_uic(data_list):
    # The logic Jamie's colleagues in DRC are looking for
    raw_string = "|".join(data_list).upper().strip()
    return hashlib.sha256(raw_string.encode()).hexdigest()[:10].upper()

@app.post("/webhook")
async def handle_message(request: Request):
    data = await request.form()
    user_phone = data.get("From")  # Twilio sends the phone number
    user_msg = data.get("Body").strip()

    # Initializing a new session
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {"step": 0, "answers": []}
        return f"Welcome. Let's generate your UIC. {QUESTIONS[0]}"

    session = user_sessions[user_phone]
    current_step = session["step"]

    # Store the answer
    session["answers"].append(user_msg)

    # Move to next question
    if current_step < len(QUESTIONS) - 1:
        session["step"] += 1
        return QUESTIONS[session["step"]]
    else:
        # All questions answered - generate UIC
        uic = generate_uic(session["answers"])
        del user_sessions[user_phone] # Clear session
        return f"Thank you. Your Unique Identifier Code (UIC) is: {uic}"
```
#### Next Steps Recommendation:
1. Set up a Twilio account (it’s free to start).
2. Use ngrok to expose your local FastAPI port 8000 to the web.
3. Point the Twilio "A message comes in" Webhook to your ngrok URL.
4. Test it on your own phone. You will see the WhatsApp messages arriving and your FastAPI code responding in the terminal.
This setup allows you to refine the UIC algorithm and the question flow with your DRC colleagues before you ever have to deal with Meta's corporate bureaucracy. Shall I help you with the specific hashing/UIC logic to ensure the "highly improbable" collision requirement is met?

Developing a Solution
I'm focusing on crafting a reliable system. My current direction involves a WhatsApp bot using Twilio, FastAPI, and Python to generate Unique Identifier Codes (UIC). The challenge is ensuring the code generation is robust, and the UIC is virtually unique by using questions that will provide highly unlikely matches. I'm exploring the specifics of those questions.
Outlining the Module
I'm now sketching the UIC_service.py module. Input validation is key, especially considering potential data inconsistencies like accents and casing. I'm focusing on normalization, using SHA-256 for a robust, human-readable UIC. I've begun to break the module down into classes versus functions, normalization methods, UIC generation methods, and verification methods. I will consider using the first two letters of first and last names.
Refining the Algorithm
I'm now refining the core algorithm for the UIC generation. I'm focusing on the input data: year of birth and gender. To make it more secure, I'll incorporate the first letter of the mother's name and the birth location (health zone or village) into the hash. I am considering imports of hashlib, re, and unicodedata. I plan to use unicodedata.normalize('NFKD', ...) for character normalization, which is vital given the DRC's French influence. A "salt" is essential for security.
To ensure the UIC (Unique Identifier Code) generation is consistent—meaning the same person always gets the same code regardless of whether they type in ALL CAPS or use accents (common in French-speaking DRC)—the service needs robust normalization before hashing.
Here is a structured sketch for uic_service.py. This design follows clean architecture principles, separating the string "cleaning" from the "cryptographic" generation.
#### uic_service.py
```import hashlib
import unicodedata
import re

class UICService:
    def __init__(self, salt: str = "DRC-HEALTH-SECURE-2024"):
        """
        The salt is crucial. It ensures that even if someone knows the
        hashing algorithm, they can't reverse engineer the UIC without
        this secret string.
        """
        self.salt = salt

    def _normalize_text(self, text: str) -> str:
        """
        Critical for DRC context:
        1. Removes French accents (é -> e).
        2. Removes special characters/spaces.
        3. Converts to Uppercase.
        """
        if not text:
            return ""

        # Convert to NFC to handle accents properly
        text = unicodedata.normalize('NFD', text)
        text = "".join([c for c in text if unicodedata.category(c) != 'Mn'])

        # Remove non-alphanumeric characters and uppercase
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        return text.upper()

    def create_uic(self,
                   first_name: str,
                   last_name: str,
                   birth_year: str,
                   mother_init: str,
                   birth_zone: str) -> str:
        """
        Generates the unique identifier based on 5 parameters.
        Adjust the logic below to match your specific UIC protocol.
        """

        # 1. Normalize all inputs
        fn = self._normalize_text(first_name)[:2]     # First 2 of Given Name
        ln = self._normalize_text(last_name)[:2]      # First 2 of Family Name
        by = self._normalize_text(birth_year)[-2:]    # Last 2 of Birth Year
        mi = self._normalize_text(mother_init)[:1]    # First letter of Mother's name
        bz = self._normalize_text(birth_zone)[:3]     # First 3 of Health Zone

        # 2. Create the raw concatenated string (The "Seed")
        # Example: JA-DO-85-M-KIN (Jane Doe, 1985, Mother Maria, Kinshasa)
        raw_seed = f"{fn}{ln}{by}{mi}{bz}"

        # 3. Create a salted hash for uniqueness & privacy
        # We add the salt so names cannot be guessed by trial and error
        hash_input = f"{raw_seed}{self.salt}".encode('utf-8')
        full_hash = hashlib.sha256(hash_input).hexdigest().upper()

        # 4. Format the final output
        # We take a slice of the hash (e.g., 8 chars) for human readability
        # but prepend the seed initials for clinical verification.
        unique_suffix = full_hash[:6]

        return f"{fn}{ln}-{by}{mi}-{unique_suffix}"

# --- Example Usage for Testing ---
if __name__ == "__main__":
    service = UICService()

    # Test case: Verifying that accents and casing don't change the UIC
    uic1 = service.create_uic("Gédéon", "Kanyinda", "1990", "M", "Gombe")
    uic2 = service.create_uic("gedeon", "KANYINDA", "90", "m", "GOMBE")

    print(f"UIC 1: {uic1}")
    print(f"UIC 2: {uic2}")
    assert uic1 == uic2
```
#### Key Logic Features for your DRC Context:
1. unicodedata Normalization: This is vital. In the DRC, some users might type "Kinshasa" while others type "Kinshasá." Without normalization, these would result in two different UICs for the same person.
2. Collison Probability:
	- By using initials (fn, ln, by, mi, bz) you create a "base" that already has high variance.
	- Adding the SHA-256 hash suffix ensures that even if two people have identical initials and birth years, the probability of them having the same 6-character hash suffix is $1 \text{ in } 16^6$ (over 16 million), which is effectively "highly improbable" for a specific health zone population.
3. Privacy (Contextual Integrity):
	- By using a salt, you ensure that the UIC is an Anonymous yet Determinative identifier.
	- If a database is leaked, an attacker cannot generate the UICs of public figures to see if they are in the database unless they also have the salt from your FastAPI environment variables.
#### Integration with FastAPI
In your main app.py, you would instantiate this service once:
```from uic_service import UICService

uic_engine = UICService(salt="YOUR_SECURE_ENV_VARIABLE")

@app.post("/webhook")
async def chat(From: str = Form(...), Body: str = Form(...)):
    # ... logic to collect the 5 variables ...
    if finished_collecting:
        code = uic_engine.create_uic(fn, ln, yr, mi, bz)
        return MessagingResponse().message(f"Your UIC is {code}")
```
Focusing on Development
I'm currently developing a WhatsApp bot for UIC generation in the DRC. This is a practical application of my data science skills within global health. Balancing the technical aspects with the demanding workload is key. The goal is to create a functional and useful tool.
Evaluating Project Scope
Okay, I've outlined the project steps. It looks like the core coding, including the FastAPI backend and UIC logic, could indeed be completed within a few hours. The Twilio setup is straightforward. I'm focusing on the state management aspect, realizing a global variable approach should be fine for this POC. Edge case testing will be crucial, so I plan to iterate on that heavily.
Defining Sprint Boundaries
I am now solidifying the project's timeline and breaking down the "half-day sprint" into manageable segments. Specifically, I'm identifying the biggest pitfalls to avoid, aiming to ensure completion within the accelerated timeframe. Skipping the webhook validation for the POC is now a clear priority. Cloud deployment will add time, so I'm considering that.
Yes, 4 hours is a very realistic "sprint" window for a data scientist with your background. Since I've already provided the technical architecture, you aren't starting from scratch—you are essentially just "wiring it up."
Here is how you can divide that half-day to get to a working demo:
#### Hour 1: Infrastructure & Plumbing
- Twilio: Sign up and join the WhatsApp Sandbox. (10 mins)
- Ngrok: Install and run ngrok http 8000 to get your public URL. (5 mins)
- Scaffold: Create a new project folder, virtual environment, and install fastapi, uvicorn, twilio, and python-multipart. (10 mins)
- Connect: Point the Twilio Webhook URL to https://your-ngrok-url.io/whatsapp.
#### Hour 2: The Logic Engine (uic_service.py)
- Copy and refine the normalization logic.
- Edge Case Testing: Run a standalone script to ensure "Gédéon" and "GEDEON" produce the same hash.
- This is the most "applied data science" part of the morning—ensuring the UIC is resilient to messy real-world data entry.
#### Hour 3: The State Machine (main.py)
- Build the simple dictionary-based session tracker (user_sessions = {}).
- Map the incoming WhatsApp messages to the sequence of questions.
- The "Reset" Logic: Add a keyword like "RESTART" to clear the session so you can test the flow multiple times without waiting for a timeout.
#### Hour 4: Integration & Testing
- Fire up the FastAPI server: uvicorn main:app --reload.
- Run through the full flow on your phone.
- The "Demo" Touch: Add a few "Success" messages. Instead of just sending the code, send: "Generating your secure code based on DRC Protocol... [Wait 1 second] ... Your UIC is: XXX-XXX"
#### Three "Pro-Tips" to keep it under 4 hours:
1. Don't use Redis yet: For a demo with < 10 people, a global Python dictionary (session_data = {}) is perfectly fine. Don't waste time setting up a database.
2. Use python-multipart: FastAPI requires this to parse the form data that Twilio sends (Twilio sends content-type: application/x-www-form-urlencoded, not JSON).
3. The "Salt" Security: Even for a POC, keep your salt in a .env file or an environment variable. Since you're dealing with global health data, it's good practice to demonstrate "Security by Design" from the very first demo.
Final Checklist for your Sprint:
- [ ] Twilio Sandbox active
- [ ] Ngrok tunnel running
- [ ] uic_service.py (Logic)
- [ ] main.py (FastAPI Webhook)
- [ ] At least one cold Přésh-style coffee in hand.
If you hit a snag with the Twilio Response XML (TwiML) or the Form parsing, let me know! I can give you the exact FastAPI code block for the response. Good luck with the DRC colleagues—this sounds like a project with real-world impact.
Defining the Architecture
I'm currently structuring the WhatsApp bot project for UIC generation in the DRC. My core idea is to establish a modular design. I am now working to clearly define the responsibilities of a "Question Service" (for survey flow) and a "UIC Service" (for logic and data). This modular architecture should allow scalability and easier maintenance down the road.
Developing the Flow
I've been refining the architecture further. My current focus is on the FlowManager, previously the Question Service, and the modified UICService. I've added a check_exists placeholder method. I'm aiming to provide a clear illustration of how they interact through the Webhook within the FastAPI's main.py file to demonstrate the clean hand-off between conversational flow and code generation.
Analyzing Data Context
I'm now diving into the French language context and health zone names. Normalization is key here, especially handling accents. From a data science perspective, I'm focusing on data integrity and implementing collision checks to ensure robustness.
You are spot on. Moving to a Separation of Concerns (SoC) architecture is the right move—it makes the code much easier to test and more resilient if you later decide to move from WhatsApp to SMS or a Web App.
Here is a sketch of how to structure those two distinct services and how they interact within the FastAPI webhook.
#### 1. The FlowManager (Conversation Service)
This service is responsible for the "State Machine." It doesn't care about hashing; it only cares about "Where is this user in the conversation?"
```# flow_manager.py

class FlowManager:
    def __init__(self):
        # In POC, this is a dict. In Production, this moves to Redis.
        self.user_states = {}

        self.steps = [
            {"key": "first_name", "q": "What is the first name? (Prénom)"},
            {"key": "last_name", "q": "What is the family name? (Nom de famille)"},
            {"key": "birth_year", "q": "What is the year of birth? (e.g., 1985)"},
            {"key": "mother_init", "q": "Initial of mother's first name?"},
            {"key": "health_zone", "q": "Which health zone were you born in?"}
        ]

    def get_next_action(self, phone_number: str, message: str):
        # 1. New user or "RESTART"
        if phone_number not in self.user_states or message.upper() == "RESTART":
            self.user_states[phone_number] = {"step_idx": 0, "collected_data": {}}
            return self.steps[0]["q"]

        state = self.user_states[phone_number]
        current_step_idx = state["step_idx"]

        # 2. Save the answer to the previous question
        current_key = self.steps[current_step_idx]["key"]
        state["collected_data"][current_key] = message

        # 3. Check if we have more questions
        if current_step_idx < len(self.steps) - 1:
            state["step_idx"] += 1
            return self.steps[state["step_idx"]]["q"]
        else:
            # 4. Signal that we are finished
            data = state["collected_data"]
            del self.user_states[phone_number] # Clear state
            return data # Return the full dict of answers
```
#### 2. The UICService (Logic & Data Integrity Service)
This service is the "Scientist." It receives the raw data, cleans it, checks for existing codes, and issues the final UIC.
```# uic_service.py

class UICService:
    def __init__(self, db_connection=None):
        self.db = db_connection # Placeholder for a DB like SQLite or Postgres
        self.salt = "DRC_SECURE_SALT_2024"

    def process_and_generate(self, raw_data: dict):
        # 1. Normalization (Internal method called for each field)
        clean_fn = self._normalize(raw_data['first_name'])
        clean_ln = self._normalize(raw_data['last_name'])
        # ... normalize others ...

        # 2. Check for Duplicates (Logic check)
        # Here you would check your DB to see if this specific combo exists
        potential_uic = self._calculate_hash(clean_fn, clean_ln, ...)

        exists = self._check_db(potential_uic)
        if exists:
            return f"MATCH FOUND: This person is already registered with UIC: {potential_uic}"

        # 3. Return the new UIC
        return f"NEW UIC ISSUED: {potential_uic}"

    def _normalize(self, text):
        # (The logic we discussed: strip accents, uppercase, etc.)
        pass

    def _calculate_hash(self, *args):
        # (The SHA-256 logic)
        pass
```
#### 3. The FastAPI Webhook (The Controller)
The Webhook acts as the "Traffic Cop," coordinating the two services.
```# main.py
from fastapi import FastAPI, Form, Response
from flow_manager import FlowManager
from uic_service import UICService
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()
flow = FlowManager()
uic_engine = UICService()

@app.post("/whatsapp")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    # 1. Talk to the FlowManager to see what happens next
    result = flow.get_next_action(From, Body)

    # 2. Decide if we continue asking questions or generate the code
    if isinstance(result, str):
        # It's a string, so it's just the next question
        response_text = result
    else:
        # It's a dictionary, so the survey is complete!
        # Pass it to the UIC engine.
        response_text = uic_engine.process_and_generate(result)

    # 3. Respond via Twilio XML
    twiml = MessagingResponse()
    twiml.message(response_text)
    return Response(content=str(twiml), media_type="application/xml")
```
#### Why this structure works for your DRC project:
1. Validation Logic: You can add a validate() step in the FlowManager. If the user types "ABC" for a birth year, the FlowManager can catch it immediately and repeat the question: "That doesn't look like a year. Please enter 4 digits (e.g., 1990)."
2. Human-in-the-loop: If the UICService finds a near-match (collision), you can code it to flag a human administrator—essential for clinical integrity in the field.
3. Language Swapping: If you need to support both French and Lingala, you only have to touch the FlowManager, leaving your UICService (the math) untouched.
Does this separation of the "Surveyor" (Flow) and the "Validator" (UIC) align with how you and your DRC colleagues visualized the clinical workflow?
