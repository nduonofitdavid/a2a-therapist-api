from models.a2a import MessagePart, A2AMessage, MessageConfiguration, TaskResult, TaskStatus, Artifact
from fastapi import  HTTPException

from datetime import datetime, timezone

from google.genai import types, Client
from typing import List, Optional
from uuid import uuid4
from util import get_query_n_history


class TherapyAgent:
    def __init__(self, api_key) -> None:
        self.gemini_client = Client(api_key=api_key)

    async def call_gemini_agent(self, query_: MessagePart):
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),
                    system_instruction="""
                    You are a biblical therapist, your provide people with words of encouragement and biblical verse and explanation on it based on their modes, 
                    the bible verse should only be one. Any questions that does not relate to christianity and the bible, ignore, any question that will likely not be theraputic, 
                    ignore and return a polite response saying why you ignored it.
                    """,
                ),
                contents=query_.text
            )
            response_message = response.text
            return response_message
        except Exception as e:
            print(f"Gemini exception: {e}")
            return "Sorry, I could not process your request"

    

    async def process_messages(
        self,
        messaages: List[A2AMessage],
        context_id: Optional[str] = None,
        task_id: Optional[str] = None,
        config: Optional[MessageConfiguration] = None
    ) -> TaskResult:
        
        context_id = context_id or str(uuid4())
        task_id = task_id or str(uuid4())

        user_message = messaages[-1] if messaages else None
        if not user_message:
            raise ValueError("No message provided")
        
        sectioned_messages = get_query_n_history(user_message.parts)

        query_ = {}
        history_ = []
        ai_agent_response = ''

        if not sectioned_messages:
            raise HTTPException(
                status_code=400,
                detail='The data you provided was not correctly formatted'
            )
        
        query_, history_ = sectioned_messages
        ai_agent_response = await self.call_gemini_agent(query_)

        agent_message = A2AMessage(
            role='agent',
            parts=[MessagePart(kind='text', text=ai_agent_response)],
            taskId=task_id
        )

        history= history_ + [agent_message]

        task_status = TaskStatus(
            state='completed',
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            message=agent_message
        )

        artifacts = [
            Artifact(
                name='therapistresponse',
                parts=[MessagePart(kind='text', text=ai_agent_response)]
            )
        ]

        if config:
            print('inside config')
            if isinstance(config.historyLength, int):
                history_length: int = config.historyLength
                print(history_length)
                if history_length > len(history):
                    history = []
                elif history_length == 0:
                    history = []
                else:
                    history_new = [A2AMessage] * history_length
                    count = 0
                    current_element = len(history) - 1
                    while count < history_length:
                        print(history[current_element].model_dump())
                        history_new[count] = history[current_element] # type: ignore
                        current_element-=1
                        count+=1
                    history = history_new[::-1]

        task_result = TaskResult(
            id=task_id,
            contextId=context_id,
            status=task_status,
            artifacts=artifacts,
            history=history # type: ignore
        )

        return task_result
    
    async def clean_up(self):
        """clean up, close connection"""
        await self.gemini_client.aio.aclose()

