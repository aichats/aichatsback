from typing import List
from uuid import uuid4

from enums import BOT, ErrorMessage, Message

from fastapi import APIRouter, UploadFile
from langchain import ConversationChain
from starlette import status
from starlette.responses import JSONResponse
from utils.ai.open_ai import get_text_chunk, insert
from utils.chat import get_conversation_chain, resolve_sender
from utils.inputs import pdf
from utils.uuid import is_valid_uuid

router = APIRouter(tags=['chat v1'])


@router.get('/v1/{chat_id}')
async def get_chat_v1(chat_id: str) -> dict[str, list[Message] | int]:
    conversation: ConversationChain = get_conversation_chain(chat_id)
    msgs: List[Message] = []

    for i, msg in enumerate(conversation.memory.chat_memory.messages):
        _msg = Message(resolve_sender(msg), msg.content, chat_id)
        msgs.append(_msg)

    return {'total': len(msgs), 'msgs': msgs}


@router.post('/v1')  # release: using conversation chain
async def create_v1(msg: Message):
    answer = Message(BOT, None, msg.chat_id)
    conversation: ConversationChain = get_conversation_chain(answer.chat_id)
    answer.message = conversation.predict(input=msg.message)
    return answer


@router.put('/{chat_id}/upload/v1')  # release:remove support only support v1
async def upload_v1(chat_id: str, file: UploadFile):  # TODO: support multiple
    if not is_valid_uuid(chat_id):
        chat_id = uuid4()

    if file.content_type != 'application/pdf':
        res = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorMessage(
                'Only pdf files are supported currently', chat_id,
            ).__dict__,
        )
        return res

    # conversation = get_conversation(chat_id)

    try:
        data = pdf.extract(file.file)
        # Use loader and data splitter to make a document list
        doc = get_text_chunk(data)
        # Upsert data to the VectorStore
        insert(doc)

        return Message(BOT, 'uploaded successfully', chat_id)
    except Exception as e:
        return ErrorMessage(e, chat_id)
