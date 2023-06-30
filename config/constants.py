import os

from os import environ
from typing import Final

from dotenv import load_dotenv

load_dotenv()

PRODUCTION: Final[str] = 'production'
DEVELOPMENT: Final[str] = 'development'
TESTING: Final[str] = 'testing'
MODE: Final[str] = os.getenv('mode', PRODUCTION)

PINECONE_API_KEY: Final[str] = environ['PINECONE_API_KEY'].strip()
PINECONE_API_ENV: Final[str] = environ['PINECONE_API_ENV'].strip()
INDEX_NAME: Final[str] = os.getenv('INDEX_NAME', 'aichat').strip()

OPENAI_API_KEY: Final[str] = environ['OPENAI_API_KEY'].strip()
OPENAI_EMBEDDINGS_LLM: Final[str] = os.getenv(
    'OPENAI_EMBEDDINGS_LLM', 'text-embedding-ada-002',
).strip()
OPENAI_CHAT_MODEL: Final[str] = os.getenv(
    'OPENAI_CHAT_MODEL', 'gpt-3.5-turbo',
).strip()
