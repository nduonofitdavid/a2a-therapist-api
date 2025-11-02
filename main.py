from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os


from google import genai
from gem import process_message

from models.a2a import JSONRPCRequest, JSONRPCResponse, TaskResult, TaskStatus, Artifact, MessagePart, A2AMessage
from util import get_query_n_history

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        context_id = str(uuid4())
        request_id = rpc_request.id


        if rpc_request.method == 'message/send':
            message = rpc_request.params.message # type: ignore
            config = rpc_request.params.configuration # type: ignore
            task_id = message.taskId or str(uuid4())
            
            processed_json = get_query_n_history(message.parts)
            if not processed_json:
                return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"message": "json payload was not formatted properly"},
                },
            )
    
            query_, history_ = processed_json

            ai_agent_response = await process_message(request_id, gemini_client, query_) # type: ignore
            
            agent_message = A2AMessage(
                role='agent',
                parts=[MessagePart(kind='text', text=ai_agent_response)], # type: ignore
                messageId=str(uuid4()),
                taskId=task_id,
            )
            
            task_status = TaskStatus(
                state='completed',
                timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                message=agent_message,
            )

            artifacts = [
                Artifact(
                    name='therapistResponse',
                    parts=[MessagePart(kind='text', text=ai_agent_response)], # type: ignore
                )
            ]
        
            # print(message.parts[1])

            task_result = TaskResult(
                id=task_id,
                contextId=context_id,
                status=task_status,
                artifacts=artifacts,
                history=history_
            )

            jsonrpc_response = JSONRPCResponse(
                id=request_id,
                result=task_result,
            )            

            return JSONResponse(
                status_code=200,
                content=jsonrpc_response.model_dump(),
            )
        

        elif rpc_request.method == 'execute':
            return JSONResponse(
                status_code=200,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"message": "Execute method not implemented yet"},
                },
            )

    except Exception as e:
        print(str(e))
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
    return {"status": "healthy", "agent": "biblical therapist"}


@app.get('/.well-known/agent.json')
async def agent_card():
    response = {
        "name": "BiblicalTherapistAgent",
        "description": "An agent that provides therapy sessions along with biblical words of encouragement",
        "url": "https://unapparelled-subcritical-lawana.ngrok-free.dev/",
        "version": "1.0.0",
        "provider": {
            "organization": "Ndu Corp",
            "url": "http://github.com/Forsaken324",
        },
        "documentationUrl": "https://unapparelled-subcritical-lawana.ngrok-free.dev/docs",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": False
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "therapy",
                "description": "provides words of encouragement based on the mode entered for the user"
            }
        ],
        "supportsAuthenticationExtendedCard": False
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run("main:app", host='0.0.0.0', port=port, reload=True)
