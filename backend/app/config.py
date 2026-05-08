from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Ollama config - runs locally in Docker
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# Same model for both jobs while testing
# Switch to claude later when ready to polish
GENERATION_MODEL = "llama3.2:3b"
EXTRACTION_MODEL = "llama3.2:3b"

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL not set in .env")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY not set in .env")
