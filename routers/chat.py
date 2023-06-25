import dataclasses
import http
import shutil
from functools import cache
from http.client import HTTPException
from typing import List, TypeVar
from uuid import uuid4

import delta as delta
import openai

from config.constants import OPENAI_CHAT_MODEL
from fastapi import APIRouter, status, UploadFile
from fastapi.responses import JSONResponse
from h11 import Response
from icecream import ic
from langchain import ConversationChain, OpenAI
from pydantic import BaseModel
from utils.ai.open_ai import get_text_chunk, insert
from utils.cache import Cache
from utils.inputs import pdf
from utils.inputs.html import extract

from utils.Time import deltaTime

router = APIRouter(tags=['chat'])

SENDER = TypeVar('SENDER', str, str)
BOT: SENDER = 'bot'
USER: SENDER = 'user'


# cache = Cache(
#     maxsize=10000, ttl=deltaTime(min=20).total_seconds(),
# )


@dataclasses.dataclass
class Message:
    sender: SENDER
    message: str
    chat_id: str = None


@dataclasses.dataclass
class ErrorMessage():
    error: str | Exception
    chat_id: str


@router.get('/')
async def get_list():  # TODO:
    return {'chats': []}


# @router.get('/{chat_id}')  # TODO:
# async def get(chat_id: str):
#     return {'message': f'chat id {chat_id}'}

@cache
def get_conversation(chat_id: str) -> ConversationChain:
    # conversation = cache.get(chat_id)
    # if conversation is not None: return conversation

    llm = OpenAI(temperature=0)
    conversation = ConversationChain(llm=llm, verbose=True)
    return conversation


@router.post('/')
async def create(msg: Message):
    answer = Message(BOT, None, msg.chat_id or uuid4())

    conversation = get_conversation(answer.chat_id)
    answer.message = conversation.predict(input=msg.message)

    return answer


@router.post('/{chat_id}/upload')
async def upload(chat_id: str, file: UploadFile):  # TODO: support multiple
    if file is None or chat_id is None:
        res = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorMessage(
                'No file attached or chat_id is not provided', chat_id,
            ),
        )
        return res

    chat_id = chat_id or uuid4()

    if file.content_type != 'application/pdf':
        return ErrorMessage('Only pdf files are supported', chat_id)

    try:
        data = pdf.extract(file.file)
        ic('pdfs have been reading into data')

        # Use loader and data splitter to make a document list
        doc = get_text_chunk(data)
        ic(f'text_chunks are generated and the total chucks are {len(doc)}')

        # Upsert data to the VectorStore
        insert(doc)

        return Message(BOT, 'uploaded successfully', chat_id)
    except Exception as e:
        return ErrorMessage(e)  # TODO:Define error format dataclass


@router.put('/{chat_id}')  # TODO:
async def upsert(chat_id: str, msg: Message):
    msg.chat_id |= chat_id
    return create(msg)

# @router.delete('/{chat_id}')  # TODO:
# async def delete(chat_id: int):
#     return {'message': f'chat id {chat_id} deleted'}
