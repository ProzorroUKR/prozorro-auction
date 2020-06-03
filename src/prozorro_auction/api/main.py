import sentry_sdk
from prozorro_auction.settings import API_PORT, logger, SENTRY_DSN, SENTRY_ENVIRONMENT
from prozorro_auction.api.views import routes
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from aiohttp import web


if SENTRY_DSN:
    sentry_sdk.init(
            dsn=SENTRY_DSN, environment=SENTRY_ENVIRONMENT,
            integrations=[AioHttpIntegration()]
        )


def create_application():
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(create_application(), port=API_PORT)
