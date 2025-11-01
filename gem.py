from models.a2a import MessagePart
from fastapi.responses import JSONResponse
from fastapi import status

from google.genai import types
from google.genai import Client

from typing import List

async def process_message(id: str, gemini_client: Client, message_part:  List[MessagePart]):
    message_payload = message_part[0]
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction='You are a biblical therapist, your provide people with words of encouragement and biblical verse and explanation on it based on their modes, the bible verse should only be one. Any questions that does not relate to christianity and the bible, ignore, any question that will likely not be theraputic, ignore and return a response like sorry, I cannot handle that it is beyond my juridstication',
            ),
            contents=message_payload.text
        )
        response_message = response.text
        return response_message
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'jsonrpc': '2.0',
                'id': id,
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': {'details': str(e)}
                }
            }
        )
        


# load_dotenv()

# API_KEY = os.getenv('GEMINI_API_KEY')
# if not API_KEY:
#     raise Exception('No Gemni API key provided')

# client = genai.Client(api_key=API_KEY)

# response = client.models.generate_content(
#     model='gemini-2.5-flash', contents='Generate a bible verse for someone who is sad'
# )

# print(response)
# print(response.text)