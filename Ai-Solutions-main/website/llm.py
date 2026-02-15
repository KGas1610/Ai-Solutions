import os
from google.genai import Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

current_date = datetime.now().strftime("%A, %B %d, %Y")

client = Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)
