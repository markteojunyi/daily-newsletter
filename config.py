from dotenv import load_dotenv
import os
 
load_dotenv()
 
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
AUDIENCE = os.getenv("AUDIENCE")
 
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048