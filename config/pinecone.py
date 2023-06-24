import pinecone
from database.pinecone_db import create_index, index_list
from icecream import ic

from config.constants import INDEX_NAME, PINECONE_API_ENV, PINECONE_API_KEY


def setup() -> None:
    ic('Init pinecone database')
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_API_ENV,
    )
    create_index(INDEX_NAME)

    indexes = index_list()

    if INDEX_NAME not in indexes:
        raise BlockingIOError(f'index creation failed:{INDEX_NAME}')

    ic(f'pinecone-setup complete:{INDEX_NAME}')
