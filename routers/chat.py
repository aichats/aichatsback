import dataclasses
import logging
from functools import cache
from typing import Dict, List, TypeVar
from uuid import uuid4

import langchain

from config.constants import OPENAI_CHAT_MODEL
from database.pinecone_db import get_vectorstore
from fastapi import APIRouter, status, UploadFile
from fastapi.responses import JSONResponse
from icecream import ic
from langchain import ConversationChain, OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from utils.ai.open_ai import get_text_chunk, insert
from utils.inputs import pdf

router = APIRouter(tags=['chat'])

SENDER = TypeVar('SENDER', str, str)
BOT: SENDER = 'bot'
USER: SENDER = 'user'

alog = logging.getLogger('app')


# cache = Cache(
#     maxsize=10000, ttl=deltaTime(min=20).total_seconds(),
# )


@dataclasses.dataclass
class Message:
    sender: SENDER
    message: str
    chat_id: str = None

    def __post_init__(self):
        if self.chat_id is None:
            self.chat_id = uuid4().hex


@dataclasses.dataclass
class ErrorMessage:
    error: str | Exception
    chat_id: str


# @router.get('/') #Need DB
# async def get_list():  # TODO:
#     return {'chats': []}
@cache
def get_conversation(chat_id: str) -> ConversationChain:
    # conversation = cache.get(chat_id)
    # if conversation is not None: return conversation

    llm = OpenAI(temperature=0)
    conversation = ConversationChain(llm=llm, verbose=True)
    return conversation


@cache
def get_chat(chat_id: str) -> BaseConversationalRetrievalChain:
    # from langchain import PromptTemplate
    #
    # # Define a custom prompt template
    # template = """Given the following conversation, respond to the best of your ability:
    # Chat History:
    # {chat_history}
    # Follow Up Input: {question}
    # Standalone question:"""
    #
    # prompt = PromptTemplate(
    #     input_variables=["chat_history", "question"],
    #     template=template
    # )
    vectorstore = get_vectorstore(namespace=chat_id)
    llm = ChatOpenAI(model=OPENAI_CHAT_MODEL)
    memory = ConversationBufferMemory(
        memory_key=chat_id, return_messages=True,
    )
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        # combine_docs_chain_kwargs={"prompt": prompt}
    )
    ic(chat_id)
    return conversation_chain


@router.get('/v1/{chat_id}')
async def get_chat_v1(chat_id: str) -> dict[str, list[Message] | int]:
    conversation: ConversationChain = get_conversation(chat_id)
    msgs: List[Message] = []

    for i, msg in enumerate(conversation.memory.chat_memory.messages):

        match msg.__class__:
            case langchain.schema.AIMessage:
                sender = BOT
            case langchain.schema.UserMessage:
                sender = USER
            case _:
                alog.error(msg)
                raise Exception('Unknown message type', msg.__class__)

        _msg = Message(sender, msg.content, chat_id)
        msgs.append(_msg)

    return {'total': len(msgs), 'msgs': msgs}


@router.get('/v2/{chat_id}')
async def get_chat_v2(chat_id: str) -> dict[str, list[Message] | int]:
    conversation: BaseConversationalRetrievalChain = get_chat(chat_id)
    msgs: List[Message] = []

    chat_history = conversation['chat_history']

    for i, message in enumerate(chat_history):
        # message.content
        # TODO:
        ic(i, message)
        pass

    return {'total': len(msgs), 'msgs': msgs}


@router.post('/v1')  # release: using conversation chain
async def create_v1(msg: Message):
    answer = Message(BOT, None, msg.chat_id)
    conversation: ConversationChain = get_conversation(answer.chat_id)
    answer.message = conversation.predict(input=msg.message)
    return answer


# release: using conversation retrieval chain for pdf support
@router.post('/v2')
async def create_v2(msg: Message):
    answer = Message(BOT, None, msg.chat_id)
    conversation: BaseConversationalRetrievalChain = get_chat(answer.chat_id)
    response = conversation({'question': msg.message})
    msg = response['chat_history'][-1]
    answer.message = msg.content  # TODO: performance fix
    return answer


@router.put('/{chat_id}/upload/v1')  # release:remove support only support v1
async def upload_v1(chat_id: str, file: UploadFile):  # TODO: support multiple
    if chat_id == '0':
        chat_id = uuid4()

    if file.content_type != 'application/pdf':
        res = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorMessage(
                'Only pdf files are supported currently', chat_id,
            ),
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


router.post('/')(create_v1)
router.get('/{chat_id}')(get_chat_v1)
router.put('/{chat_id}/upload')(upload_v1)
