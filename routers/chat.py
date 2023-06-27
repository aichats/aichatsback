import asyncio
import dataclasses
import http
import logging
import sys
from functools import cache
from typing import List, TypeVar
from uuid import uuid4

import langchain

from config.constants import OPENAI_CHAT_MODEL
from database.pinecone_db import get_vectorstore
from fastapi import APIRouter, status, UploadFile
from fastapi.responses import JSONResponse
from icecream import ic
from langchain import ConversationChain, OpenAI
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
    ConversationalRetrievalChain,
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


def resolve_sender(msg) -> str:
    match msg.__class__:
        case langchain.schema.AIMessage:
            sender = BOT
        case langchain.schema.HumanMessage:
            sender = USER
        case _:
            alog.error(msg)
            raise Exception('Unknown message type', msg.__class__)
    return sender


@dataclasses.dataclass
class Message:
    sender: SENDER | langchain.schema.AIMessage | langchain.schema.HumanMessage
    message: str
    chat_id: str = None

    def __post_init__(self):
        if self.chat_id is None or self.chat_id == 'null':
            self.chat_id = uuid4().hex


@dataclasses.dataclass
class ErrorMessage:
    error: str | Exception
    chat_id: str
    status_code: http.HTTPStatus = status.HTTP_400_BAD_REQUEST

    def __post_init__(self):
        self.error = str(self.error)
        alog.error(
            self.__dict__,
        )

    def __repr__(self):
        return self.__call__()

    def __call__(self):
        return JSONResponse(
            status_code=self.status_code,
            content=self.__dict__,
        )

    def __json__(self):
        return self.__dict__


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
    # TODO:prompt
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
        memory_key='chat_history', return_messages=True,
    )
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        # combine_docs_chain_kwargs={"prompt": prompt}
    )
    return conversation_chain


@router.get('/v1/{chat_id}')
async def get_chat_v1(chat_id: str) -> dict[str, list[Message] | int]:
    conversation: ConversationChain = get_conversation(chat_id)
    msgs: List[Message] = []

    for i, msg in enumerate(conversation.memory.chat_memory.messages):
        _msg = Message(resolve_sender(msg), msg.content, chat_id)
        msgs.append(_msg)

    return {'total': len(msgs), 'msgs': msgs}


@router.get('/v2/{chat_id}')
async def get_chat_v2(chat_id: str) -> dict[str, list[Message] | int]:
    conversation: BaseConversationalRetrievalChain = get_chat(chat_id)
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
    conversation = get_chat(msg.chat_id)
    ic(conversation)
    response = conversation({'question': msg.message})
    answer.message = response['answer']
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


@router.put('/{chat_id}/upload/v2')
async def upload_v2(chat_id: str, file: UploadFile):
    if chat_id == '0':  # For beginning of new conversation
        chat_id = uuid4()

    if file.content_type != 'application/pdf':
        return ErrorMessage(
            'Only pdf files are supported currently', chat_id, status.HTTP_400_BAD_REQUEST,
        )()
    try:
        data = pdf.extract(file.file)
        # Use loader and data splitter to make a document list
        doc = get_text_chunk(data)
        # Upsert data to the VectorStore
        insert(doc, chat_id)
        conversation = get_conversation(chat_id)
        # res = conversation.run(
        #     {'question': f'uploaded a pdf file-{file.filename} which will serve as context for our conversation '},
        # )
        prompt_tmpl = Message(
            USER,
            f"""uploaded a pdf file-{file.filename} which will serve as context for our conversation""",
            chat_id,
        )

        task = asyncio.create_task(create_v2(prompt_tmpl))
        # https://docs.python.org/3/library/asyncio-task.html#waiting-primitives
        done, pending = await asyncio.wait([task], timeout=0.0000001)

        return Message(BOT, f'uploaded-{file.filename}', chat_id)
    except Exception as e:
        return ErrorMessage(
            e, chat_id, status.HTTP_422_UNPROCESSABLE_ENTITY,
        )()


router.post('/')(create_v1)
router.get('/{chat_id}')(get_chat_v1)
router.put('/{chat_id}/upload')(upload_v1)
