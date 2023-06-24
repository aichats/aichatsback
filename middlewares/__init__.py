import logging

from fastapi import FastAPI
from icecream import ic


def setup_middlewares(app: FastAPI):
    from .log_requests import exception_handler, log_requests

    app.middleware('http')(log_requests)
    app.exception_handler(Exception)(exception_handler)
    ic('initialized middlewares')
