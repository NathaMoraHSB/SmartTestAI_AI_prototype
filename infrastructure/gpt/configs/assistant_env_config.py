import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global environment settings for libraries (must be set before importing them)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disables oneDNN optimizations (for compatibility issues)
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'  # Suppresses symlink warnings from HuggingFace Hub

# OpenAI API configuration
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/responses"