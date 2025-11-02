from models.a2a import MessagePart, A2AMessage
from typing import List, Tuple, Any, Dict


def purify_text(text: str) -> str:
    return text.strip().replace('<p>', '').replace('</p>', '').replace('<br />', '')

def process_history(prev_messages: List[Dict[str, Any]]) -> List[A2AMessage]:
    history = []

    if prev_messages and len(prev_messages) != 0: 
        for i, prev_message in enumerate(prev_messages):
            prev_ms_in = MessagePart(
                kind=prev_message['kind'], # type: ignore
                text=purify_text(prev_message['text']) # type: ignore
            )
            h_message = A2AMessage(
                role='agent' if i % 2 == 0 else 'user',
                parts=[prev_ms_in]
            )
            history.append(h_message)
    return history

def get_query_n_history(message_part: List[MessagePart]) -> Tuple[MessagePart, List[A2AMessage]] | None:
    if len(message_part) == 0:
        return None
    
    query_str = MessagePart(kind='text', text='the user entered an empty message, prompt the user for his or her mode')
    history = []
    
    if len(message_part) == 1:
        if message_part[0].kind == 'text':
            text_payload = message_part[0]
            if text_payload.text:
                query_str.text = purify_text(text_payload.text)

        elif message_part[0].kind == 'data':
            history_in = message_part[0].data
            history = process_history(history_in) if isinstance(history_in, list) else []

        return query_str, history

    print('here1')
    query_str.text = purify_text(message_part[0].text) if message_part[0].text else ''
    print('heremid')
    history = process_history(message_part[1].data) if message_part[1].data and isinstance(message_part[1].data, list) else []
    
    print('here2')
    newest_convo = A2AMessage(
        role='user',
        parts=[MessagePart(kind=query_str.kind, text=query_str.text)]
    )
    history.append(newest_convo)

    return query_str, history

