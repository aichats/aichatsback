import openai

from config.constants import OPENAI_API_KEY


def setup():
    openai.api_key = OPENAI_API_KEY
