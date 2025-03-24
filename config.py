import os

# Load the API key from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if GROQ_API_KEY is None:
    raise ValueError("GROQ_API_KEY is not set. Please check your Streamlit Cloud settings.")