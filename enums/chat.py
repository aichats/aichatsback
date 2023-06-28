import dataclasses
import http
import logging
from typing import TypeVar
from uuid import uuid4

import langchain

from config import alog
from starlette import status
from starlette.responses import JSONResponse
from utils.uuid import is_valid_uuid

SENDER = TypeVar('SENDER', str, str)
BOT: SENDER = 'bot'
USER: SENDER = 'user'


@dataclasses.dataclass
class Message:
    sender: SENDER | langchain.schema.AIMessage | langchain.schema.HumanMessage
    message: str
    chat_id: str = None

    def __post_init__(self):
        if not is_valid_uuid(self.chat_id):
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
