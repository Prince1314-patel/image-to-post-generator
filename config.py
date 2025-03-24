import os
from dotenv import load_dotenv
import toml

# Load secrets from the secrets.toml file
secrets = toml.load('.secrets/secrets.toml')
GROQ_API_KEY = secrets['GROQ']['API_KEY']