import config
import middlewares
from config.constants import INDEX_NAME, MODE, PRODUCTION
from fastapi import FastAPI
from icecream import ic
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from middlewares import health
from routers import chat

app = FastAPI(debug=False)
app.include_router(chat.router, prefix='/chat')
app.include_router(health.router)

config.setup()

middlewares.setup_middlewares(app)


@app.on_event('startup')
async def startup():
    app.debug = MODE != PRODUCTION
    embeddings = OpenAIEmbeddings()
    vectorstore = Pinecone.from_existing_index(
        index_name=INDEX_NAME, embedding=embeddings,
    )
    ic(vectorstore)
    ic('startup complete')


@app.get('/')
async def root():
    return {'message': 'AI Chat is up'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
