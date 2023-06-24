import os

from fastapi import FastAPI

from routers import chat

debug = os.getenv('debug', True)

app = FastAPI(debug=debug)

app.include_router(chat.router, prefix='/chat')


@app.get('/')
async def root():
    return {'message': 'AI Chat is up'}


@app.get('/health')
async def health():
    return {'status': 'ok'}
