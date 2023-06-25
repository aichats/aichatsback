import dataclasses
import http
import shutil
from http.client import HTTPException
from typing import List, TypeVar

import openai

from config.constants import OPENAI_CHAT_MODEL
from fastapi import APIRouter, status, UploadFile
from fastapi.responses import JSONResponse
from h11 import Response
from icecream import ic
from pydantic import BaseModel
from utils.ai.open_ai import get_text_chunk, insert
from utils.inputs import pdf
from utils.inputs.html import extract

router = APIRouter(tags=['chat'])

SENDER = TypeVar('SENDER', str, str)
BOT: SENDER = 'bot'
USER: SENDER = 'user'


@dataclasses.dataclass
class Message:
    sender: SENDER
    message: str
    chat_id: int = None


@dataclasses.dataclass
class ErrorMessage():
    error: str | Exception
    chat_id: int


@router.get('/')
async def get_list():  # TODO:
    return {'chats': []}


# @router.get('/{chat_id}')  # TODO:
# async def get(chat_id: int):
#     return {'message': f'chat id {chat_id}'}


@router.post('/')
async def create(msg: Message):
    new_chat_id: int = msg.chat_id or 1

    response = openai.Completion.create(
        engine='text-davinci-003',  # TODO:configurable
        prompt='',
        max_tokens=100,  # Set the maximum number of tokens in the response
        n=1,  # Set the number of completions to generate
        stop=None,  # Specify an optional stopping criterion
    )

    answer = Message(BOT, response.choices[0].text.strip(), new_chat_id)

    return answer


@router.post('/{chat_id}/upload')
async def upload(chat_id: int, file: UploadFile):  # TODO: support multiple
    if file is None or chat_id is None:
        res = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorMessage(
                'No file attached or chat_id is not provided', chat_id,
            ),
        )
        return res

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

        return {'message': 'Uploaded successfully', 'chat_id': chat_id}
    except Exception as e:
        return ErrorMessage(e)  # TODO:Define error format dataclass


@router.put('/{chat_id}')  # TODO:
async def upsert(chat_id: int, msg: Message):
    msg.chat_id |= chat_id
    return create(msg)

# @router.delete('/{chat_id}')  # TODO:
# async def delete(chat_id: int):
#     return {'message': f'chat id {chat_id} deleted'}
