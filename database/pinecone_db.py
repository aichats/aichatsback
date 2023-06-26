import logging
from functools import cache
from typing import List

import pinecone

from config.constants import INDEX_NAME, OPENAI_EMBEDDINGS_LLM
from icecream import ic
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Pinecone


def index_list() -> List[str]:
    return pinecone.list_indexes()


def create_index(index_name: str = INDEX_NAME, dimension: int = 1536, metric: str = 'euclidean'):
    # check before creating
    if index_name not in index_list():
        # index not existed. Create a new index
        pinecone.create_index(
            name=index_name, dimension=dimension, metric=metric,
        )
        ic(f'created a new index {index_name}')
    else:
        logging.warning(f'{index_name} index existed. skip creating.')


def insert(data: List[Document], embeddings: OpenAIEmbeddings, index=INDEX_NAME, namespace='') -> Pinecone:
    return Pinecone.from_documents(
        data, embedding=embeddings,
        index_name=index,
    )  # TODO: support namespaces based on user


@cache
def get_vectorstore(
        index_name=INDEX_NAME, namespace: str = None, text_key: str = 'text',
        embeddings=OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_LLM),
) -> Pinecone:
    vectorstore = Pinecone.from_existing_index(
        index_name=index_name, embedding=embeddings, namespace=namespace, text_key=text_key,
    )
    return vectorstore
