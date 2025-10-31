from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise Exception('No Gemni API key provided')

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model='gemini-2.5-flash', contents='Generate a bible verse for someone who is sad'
)

print(response)
print(response.text)