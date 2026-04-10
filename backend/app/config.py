from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Claude model config
GENERATION_MODEL = "claude-haiku-4-5"
EXTRACTION_MODEL = "claude-sonnet-4-6"

# Sanity check on startup
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set in .env")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL not set in .env")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY not set in .env")
