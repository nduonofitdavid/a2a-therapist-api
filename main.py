from uuid import uuid4
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
import json
import sys

from agent.therapist import TherapyAgent

from models.a2a import A2AMessage, JSONRPCRequest, JSONRPCResponse, MessagePart

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise Exception('GEMINI API key was not found, add it to your .env file')


logger = logging.getLogger('fastapi_app')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('fastapi.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)


@asynccontextmanager
async def lifeSpan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global therapy_agent

    therapy_agent = TherapyAgent(
        api_key=GEMINI_API_KEY
    )

    yield

    if therapy_agent:
        await therapy_agent.clean_up()


app = FastAPI(
    title="Ndu's Telex Integration",
    description="An AI agent that provides therapy and comfort through the word of God",
    version="1.0",
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
    logger.info('Root endpoint accessed')
    return welcome_response

@app.post('/a2a/therapist')
async def a2a_endpoint(request: Request):
    """Main Bible therapist endpoint"""
    
    
    try:
        body = await request.json()

        if body is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32600,
                        'message': 'Invalid Request: No JSON body'
                    }
                }
            )

        logger.info(f"Raw telex body: {json.dumps(body, indent=2)}")

        print(body)

        if 'jsonrpc' in body:
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

            context_id = None
            task_id = None
            messages = []
            config = None

            if rpc_request.method == 'message/send':
                messages =[rpc_request.params.message] # type: ignore
                config = rpc_request.params.configuration # type: ignore

            elif rpc_request.method == 'execute':
                messages = rpc_request.params.messages # type: ignore
                context_id = rpc_request.params.contextId # type: ignore
                task_id = rpc_request.params.taskId # type: ignore
            
            else:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        'jsonrpc': '2.0',
                        'id': rpc_request.id,
                        'error': {'code': -32601, 'message': 'Method not found'}
                    }
                )
        else:
            message = body.get('message')
            if not message:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        'jsonrpc': '2.0',
                        'id': body.get('id') or str(uuid4()),
                        'error': {
                            'code': -32600,
                            'message': "Invalid Request: jsonrpc must be '2.0' and id is required "
                        }
                    }
                )
            context_id= body.get('contextId') or str(uuid4())
            task_id = body.get('id') or str(uuid4())
            config = body.get('config', None)

            messages = [A2AMessage(kind='message', role='user', parts=[MessagePart(kind='text', text=message), MessagePart(kind='data', data=[{'kind': 'text', 'text': message}])])]

        # call the AI agent
        result = await therapy_agent.process_messages(
            messaages=messages,
            context_id=context_id,
            task_id=task_id,
            config=config
        )

        # build response
        if 'jsonrpc' in body:
            response = JSONRPCResponse(
                id=rpc_request.id, # type: ignore
                result=result
            )

            return response.model_dump()
    
        else:
            result.id = task_id # type: ignore
            result.status.state = 'completed'
            return result.model_dump()
        

    except Exception as e:
        logging.error(
            f"A2A endpoint error - Request ID: {body.get('id') if 'body' in locals() else 'N/A'}" # type: ignore
            f"Request Method: {body.get('method') if 'body' in locals() else 'N/A'}" # type: ignore
            f"Exception Raised: {str(e)}",
            exc_info=True
        )
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
    return {"status": "healthy", "agent": "biblicaltherapist"}


@app.get('/.well-known/agent.json')
async def agent_card():
    response = {
        "name": "biblicaltherapist",
        "description": "An agent that provides therapy sessions along with biblical words of encouragement",
        "url": "https://unapparelled-subcritical-lawana.ngrok-free.dev/",
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": False
        },
        "skills": [
            {
                "name": "therapy",
                "description": "provides words of encouragement based on the mode entered for the user"
            }
        ],
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run("main:app", host='0.0.0.0', port=port, reload=True)
