# test_env.py
import os
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print("API Key loaded successfully!")
    print(f"First 5 chars of key: {api_key[:5]}")
else:
    print("API Key NOT loaded. Check .env file and its location.")