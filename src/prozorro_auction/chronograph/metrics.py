from aiohttp.abc import AbstractAccessLogger
from aiohttp import web
import prometheus_client
import asyncio

registry = prometheus_client.CollectorRegistry()  # without default python metrics
chronograph_processing_time_summary = prometheus_client.Summary(
    'chronograph_processing_time_summary',
    'Time taken to process an auction stage',
    registry=registry,
)
chronograph_total_time_summary = prometheus_client.Summary(
    'chronograph_total_time_summary',
    'Time taken to fetch auction and process',
    registry=registry,
)


async def metrics(_):
    response = web.Response(body=prometheus_client.generate_latest(registry=registry))
    response.content_type = prometheus_client.CONTENT_TYPE_LATEST
    return response


class AccessLogger(AbstractAccessLogger):
    def log(self, request, response, time):
        pass


async def main():
    app = web.Application()
    app.router.add_get('/metrics', metrics)
    runner = web.AppRunner(app, access_log_class=AccessLogger)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 9091)
    await site.start()
    while True:
        await asyncio.sleep(3600)
