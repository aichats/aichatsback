from icecream import ic

from config import log, open_ai, pinecone


def setup():
    log.setup()
    pinecone.setup()
    open_ai.setup()
    ic('setup of log, openai, pinecone complete')
