from app import app

from fastapi.middleware.wsgi import WSGIMiddleware

wsgi_app = WSGIMiddleware(app)


def application(environ, start_response):
    return wsgi_app(environ, start_response)
