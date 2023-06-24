from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=['chat'])


class Message(BaseModel):
    message: str
    chat_id: int


@router.get('/')
async def get_list():
    return {'chats': []}


@router.get('/{chat_id}')
async def get(chat_id: int):
    return {'message': f'chat id {chat_id}'}


@router.post('/')
async def create(msg: Message):
    new_chat_id: int = 1
    return {'message': f'chat created id-{new_chat_id}'}


@router.put('/{chat_id}')
async def update(chat_id: int, msg: Message):
    return {'message': f'chat {chat_id} updated'}


@router.delete('/{chat_id}')
async def delete(chat_id: int):
    return {'message': f'chat id {chat_id} deleted'}
