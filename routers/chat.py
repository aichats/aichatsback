import dataclasses
import http
from http.client import HTTPException
from typing import List

from fastapi import APIRouter, status, UploadFile
from fastapi.responses import JSONResponse
from h11 import Response
from pydantic import BaseModel

router = APIRouter(tags=['chat'])


class Message(BaseModel):
    message: str = None
    chat_id: int = None
    attachments: UploadFile = None


@router.get('/')
async def get_list():  # TODO:
    return {'chats': []}


@router.get('/{chat_id}')  # TODO:
async def get(chat_id: int):
    return {'message': f'chat id {chat_id}'}


@router.post('/')  # TODO:
async def create(msg: Message):
    new_chat_id: int = msg.chat_id or '1'
    answer = Message(msg.message, new_chat_id)

    return {'message': answer}


@router.post('/upload')
async def upload(msg: Message):

    if msg.attachments is None or msg.chat_id is None:
        res = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': 'no file attached or chat_id is not provided'},
        )
        return res

    file = msg.attachments

    if file.content_type != 'application/pdf':
        return {'error': 'Only PDF files are allowed'}

    return {'message': 'uploaded successfully', 'chat_id': msg.chat_id}

# @router.put('/{chat_id}') #TODO:
# async def upsert(chat_id: int, msg: Message):
#     return {'message': f'chat {chat_id} updated'}
#
#
# @router.delete('/{chat_id}')  # TODO:
# async def delete(chat_id: int):
#     return {'message': f'chat id {chat_id} deleted'}
