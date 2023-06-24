from config import log, open_ai, pinecone


def setup():
    log.setup()
    pinecone.setup()
    open_ai.setup()
