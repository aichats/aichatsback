import logging

from config import alog

from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from starlette.responses import JSONResponse


async def log_requests(request: Request, call_next):
    alog.debug(f'Request received: {request.method} {request.url}')
    response = await call_next(request)
    alog.debug(f'Response returned: {response.status_code}')
    return response


async def exception_handler(request: Request, exc: Exception):
    alog.exception({
        'request': request.url.path,
        'exception': exc,
    })
