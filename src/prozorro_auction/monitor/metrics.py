from prozorro_auction.monitor.storage import (
    get_minimum_timer_auction,
    get_auction_count_by_timer,
)
from prozorro_auction.monitor.settings import MONITOR_EXPECTING_OFFSET_SECONDS
from prozorro_auction.utils.base import get_now
from prozorro_auction.settings import TZ
from aiohttp.abc import AbstractAccessLogger
from aiohttp import web
from datetime import timedelta
import prometheus_client
import asyncio
import pytz

registry = prometheus_client.CollectorRegistry()  # without default python metrics

chronograph_pending_gauge = prometheus_client.Gauge(
    'chronograph_pending_gauge',
    'Number of auctions ready to be processed by chronograph',
    registry=registry,
)
chronograph_expecting_gauge = prometheus_client.Gauge(
    'chronograph_expecting_gauge',
    'Number of auctions about to be processed in the near future (1m by default)'
    '(can be used to auto-scale chronograph)',
    registry=registry,
)
chronograph_max_offset_gauge = prometheus_client.Gauge(
    'chronograph_max_offset_gauge',
    'The biggest offset timer auction, shows how many seconds ago the auction must`ve been processed',
    registry=registry,
)


async def metrics(_):
    now = get_now()
    auction, pending_count, expecting_count = await asyncio.gather(
        get_minimum_timer_auction(now),
        get_auction_count_by_timer(now),
        get_auction_count_by_timer(now + timedelta(seconds=MONITOR_EXPECTING_OFFSET_SECONDS)),
    )

    # 1
    if auction is None:
        chronograph_max_offset_gauge.set(0)
    else:
        timer = pytz.utc.localize(auction["timer"]).astimezone(TZ)
        offset = (now - timer).total_seconds()
        chronograph_max_offset_gauge.set(offset)

    chronograph_pending_gauge.set(pending_count)
    chronograph_expecting_gauge.set(expecting_count)

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
