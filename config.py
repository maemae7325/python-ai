import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

AVAILABLE_MODELS = {
    "Gemini 2.5 Flash（推奨・高速）": "gemini-2.5-flash",
    "Gemini 2.0 Flash（安定）": "gemini-2.0-flash",
    "Gemini 2.5 Pro（高品質）": "gemini-2.5-pro",
}

DEFAULT_MODEL = "gemini-2.5-flash"
