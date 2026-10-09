import os
from dotenv import load_dotenv

# Read the .env file and put its values into environment variables
load_dotenv()

# Required: the app can't work without these, so crash early if missing
DATABASE_URL = os.environ["DATABASE_URL"]
QDRANT_URL = os.environ["QDRANT_URL"]

# Optional for now: an empty string if not set
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")   # needed from Week 2