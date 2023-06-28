import asyncio
from typing import List
from uuid import uuid4

import langchain

from config import alog
from enums import BOT, ErrorMessage, Message, USER
from fastapi import APIRouter, UploadFile
from icecream import ic
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
from starlette import status
from utils.ai.open_ai import get_text_chunk, insert
from utils.chat import get_conversation_v2, resolve_sender
from utils.inputs import pdf
from utils.uuid import is_valid_uuid

router = APIRouter(tags=['chat v2'])


@router.post('/v2/{chat_id}')
async def get_chat_v2(chat_id: str) -> dict[str, list[Message] | int]:
    conversation: BaseConversationalRetrievalChain = get_conversation_v2(
        chat_id,
    )
    msgs: List[Message] = []

    chat_history: List[
        langchain.schema.AIMessage |
        langchain.schema.HumanMessage
    ] = conversation.memory.chat_memory

    for i, msg in enumerate(chat_history.messages):
        # ic(i, msg)
        _msg = Message(resolve_sender(msg), msg.content, chat_id)
        msgs.append(_msg)

    return {'total': len(msgs), 'msgs': msgs}


@router.post('/v2')
async def create_v2(msg: Message):
    answer = Message(BOT, None, msg.chat_id)
    conversation = get_conversation_v2(msg.chat_id)
    ic(conversation)
    response = conversation({'question': msg.message})
    answer.message = response['answer']
    return answer


@router.put('/{chat_id}/upload/v2')
async def upload_v2(chat_id: str, file: UploadFile):  # FIX backport v1
    if not is_valid_uuid(chat_id):  # For beginning of new conversation
        alog.error(__name__, 'invalid chat_id', chat_id)
        chat_id = uuid4().hex

    if file.content_type != 'application/pdf':
        return ErrorMessage(
            'Only pdf files are supported currently', chat_id, status.HTTP_400_BAD_REQUEST,
        )()

    try:
        data = pdf.extract(file.file)
        # Use loader and data splitter to make a document list
        doc = get_text_chunk(data)
        # Upsert data to the VectorStore
        insert(doc, namespace=chat_id)

        prompt_tmpl = Message(
            USER,
            f"""uploaded a pdf file-{file.filename} which will serve as context for our conversation""",
            chat_id,
        )

        task = asyncio.create_task(create_v2(prompt_tmpl))
        # https://docs.python.org/3/library/asyncio-task.html#waiting-primitives
        # doesn't block or raise in case of timeouts
        await asyncio.wait([task], timeout=pow(10, -7))

        return Message(BOT, f'uploaded-{file.filename}', chat_id)
    except Exception as e:
        return ErrorMessage(
            e, chat_id, status.HTTP_422_UNPROCESSABLE_ENTITY,
        )()
