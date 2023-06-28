from functools import cache
from typing import List
from uuid import uuid4

from enums import BOT, ErrorMessage, Message

from fastapi import APIRouter, UploadFile
from langchain import ConversationChain, OpenAI
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
from starlette import status
from utils.ai.open_ai import get_text_chunk, insert
from utils.chat import resolve_sender
from utils.inputs import pdf
from utils.uuid import is_valid_uuid

router = APIRouter(tags=['chat v3'])


@cache
def get_conversation_chain(chat_id: str) -> ConversationChain | BaseConversationalRetrievalChain:
    # conversation = cache.get(chat_id)
    # if conversation is not None: return conversation

    llm = OpenAI(temperature=0)
    conversation = ConversationChain(llm=llm, verbose=True)
    return conversation


@router.get('/v3/{chat_id}')
async def get_chat(chat_id: str) -> dict[str, list[Message] | int]:
    conversation: ConversationChain = get_conversation_chain(chat_id)
    msgs: List[Message] = []

    for i, msg in enumerate(conversation.memory.chat_memory.messages):
        _msg = Message(resolve_sender(msg), msg.content, chat_id)
        msgs.append(_msg)

    return {'total': len(msgs), 'msgs': msgs}


@router.post('/v3')  # release: using conversation chain
async def create(msg: Message):
    answer = Message(BOT, None, msg.chat_id)
    conversation: ConversationChain = get_conversation_chain(answer.chat_id)
    answer.message = await conversation.apredict(input=msg.message)
    return answer


@router.put('/{chat_id}/upload/v3')  # release:remove support only support v3
async def upload(chat_id: str, file: UploadFile):  # TODO: support multiple
    if not is_valid_uuid(chat_id):
        chat_id = uuid4()

    if file.content_type != 'application/pdf':
        return ErrorMessage('Only pdf files are supported currently', chat_id, status.HTTP_400_BAD_REQUEST)

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
