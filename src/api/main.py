from aiohttp import web
from settings import API_PORT, logger
from api.views import routes


def create_application():
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(create_application(), port=API_PORT)
