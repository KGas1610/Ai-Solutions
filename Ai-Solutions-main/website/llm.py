import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(
    api_key=os.getenv("GOOGLE_API_KEY")
