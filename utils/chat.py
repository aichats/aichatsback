import logging
from functools import cache

import langchain

from config import alog
from config.constants import OPENAI_CHAT_MODEL
from database.pinecone_db import get_vectorstore

from enums.chat import BOT, USER
from langchain import ConversationChain, OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


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


@cache
def get_conversation_chain(chat_id: str) -> ConversationChain:
    # conversation = cache.get(chat_id)
    # if conversation is not None: return conversation

    llm = OpenAI(temperature=0)
    conversation = ConversationChain(llm=llm, verbose=True)
    return conversation


@cache
def get_conversation_v2(chat_id: str) -> BaseConversationalRetrievalChain:
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
        retriever=vectorstore.as_retriever(namespace=chat_id),
        memory=memory,
        verbose=True,
        # combine_docs_chain_kwargs={"prompt": prompt}
    )
    return conversation_chain
