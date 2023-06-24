import logging

import middlewares
from config import log
from config.constants import MODE, PRODUCTION

from fastapi import FastAPI
from icecream import ic
from middlewares import health
from routers import chat

app = FastAPI(debug=False)
app.include_router(chat.router, prefix='/chat')
app.include_router(health.router)

log.setup()

middlewares.setup_middlewares(app)


@app.on_event('startup')
async def startup():
    app.debug = MODE != PRODUCTION


@app.get('/')
async def root():
    return {'message': 'AI Chat is up'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
