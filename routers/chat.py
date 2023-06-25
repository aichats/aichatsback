import dataclasses
import http
import shutil
from http.client import HTTPException
from typing import List, TypeVar

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
    sender: BOT | USER | SENDER
    message: str
    chat_id: int = None


@router.get('/')
async def get_list():  # TODO:
    return {'chats': []}


@router.get('/{chat_id}')  # TODO:
async def get(chat_id: int):
    return {'message': f'chat id {chat_id}'}


@router.post('/')
async def create(msg: Message):
    new_chat_id: int = msg.chat_id or '1'
    answer = Message(BOT, msg.message, new_chat_id)

    return {'message': answer}


@router.post('/{chat_id}/upload')
async def upload(chat_id: int, file: UploadFile):  # TODO: support multiple
    if file is None or chat_id is None:
        res = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': 'No file attached or chat_id is not provided'},
        )
        return res

    if file.content_type != 'application/pdf':
        return {'error': 'Only PDF files are allowed'}

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
        return {'error': str(e)}


@router.put('/{chat_id}')  # TODO:
async def upsert(chat_id: int, msg: Message):
    msg.chat_id |= chat_id
    return create(msg)

# @router.delete('/{chat_id}')  # TODO:
# async def delete(chat_id: int):
#     return {'message': f'chat id {chat_id} deleted'}
