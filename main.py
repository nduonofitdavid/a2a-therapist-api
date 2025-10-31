from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from google import genai

from models.a2a import JSONRPCRequest, JSONRPCResponse, TaskResult, TaskStatus, Artifact, MessagePart, A2AMessage

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise Exception('GEMINI API key was not found, add it to your .env file')


@asynccontextmanager
async def lifeSpan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global gemini_client

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    yield

    if gemini_client:
        await gemini_client.aio.aclose()


app = FastAPI(
    title="Ndu's Telex Integration",
    lifespan=lifeSpan
)

welcome_response = """
<!DOCTYPE html>
<html lang=en>
    <head>
        <title>Ndu's Telex Integration</title>
    </head>
    <body>
        <h1>Welcome to the bible therapist integration</h1>
        <p>This is a safe space, visit /docs for more information on how to use this integration</p>
    </body>
</html>
"""

@app.get('/', response_class=HTMLResponse)
async def index():
    return welcome_response

@app.post('/a2a/therapist')
async def a2a_endpoint(request: Request):
    """Main Bible therapist endpoint"""
    try:
        body = await request.json()

        if body.get('jsonrpc') != '2.0' or 'id' not in body:
            return JSONResponse(
                status_code=400,
                content={
                    'jsonrpc': '2.0',
                    'id': body.get('id'),
                    'error': {
                        'code': -32600,
                        'message': "Invalid Request: jsonrpc must be '2.0' and id is required "
                    }
                }
            )

        rpc_request = JSONRPCRequest(**body)

        messages = []
        context_id = None
        task_id = None
        config = None

        if rpc_request.method == 'message/send':
            messages = [rpc_request.params.message] # type: ignore
            config = rpc_request.params.configuration # type: ignore
        elif rpc_request.method == 'execute':
            messages = rpc_request.params.messages # type: ignore
            context_id = rpc_request.params.contextId # type: ignore
            task_id = rpc_request.params.taskId # type: ignore


        return rpc_request.model_dump()

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'jsonrpc': '2.0',
                'id': body.get('id') if 'body' in locals() else None, # type: ignore
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': {'details': str(e)}
                }
            }
        )

@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "chess"}


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
