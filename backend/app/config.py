# from dotenv import load_dotenv
# import os

# load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# # Ollama config - runs locally in Docker
# OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# # Same model for both jobs while testing
# # Switch to claude later when ready to polish
# GENERATION_MODEL = "llama3.2:3b"
# EXTRACTION_MODEL = "llama3.2:3b"

# if not SUPABASE_URL:
#     raise ValueError("SUPABASE_URL not set in .env")
# if not SUPABASE_KEY:
#     raise ValueError("SUPABASE_KEY not set in .env")


from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # dormant, keep for later
GROQ_API_KEY = os.getenv("GROQ_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Model config
GENERATION_MODEL = "llama-3.3-70b-versatile"   # Groq
EXTRACTION_MODEL = "gemini-2.5-flash"            # Gemini

if not GROQ_API_KEY:
    raise ValueError("GROQ_KEY not set in .env")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_KEY not set in .env")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL not set in .env")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY not set in .env")