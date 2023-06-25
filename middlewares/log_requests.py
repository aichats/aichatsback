import logging

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

alog = logging.getLogger('app')


async def log_requests(request: Request, call_next):
    alog.debug(f'Request received: {request.method} {request.url}')
    response = await call_next(request)
    alog.debug(f'Response returned: {response.status_code}')
    return response


async def exception_handler(request: Request, exc: Exception):
    alog.error(f'Exception occurred: {exc}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'message': 'Internal Server Error'},
    )
