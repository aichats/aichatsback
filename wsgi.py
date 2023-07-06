def application(environ, start_response):
    from app import app

    from fastapi.middleware.wsgi import WSGIMiddleware

    wsgi_app = WSGIMiddleware(app)
    return wsgi_app(environ, start_response)
