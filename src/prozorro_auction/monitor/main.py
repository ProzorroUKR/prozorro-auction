from prozorro_auction.monitor.settings import (
    MONITOR_TIMER_WARNING_LIMIT,
    MONITOR_TIMER_ERROR_LIMIT,
    MONITOR_INTERVAL_SECONDS,
    MONITOR_PENDING_AUCTION,
    MONITOR_TIMER,
)
from prozorro_auction.monitor.storage import get_minimum_timer_auction, get_auction_count_by_timer
from prozorro_auction.monitor.metrics import main as metrics_main
from prozorro_auction.settings import SENTRY_DSN, TZ
from prozorro_auction.utils.base import get_now
from prozorro_auction.logging import setup_logging, update_log_context
import asyncio
import signal
import sentry_sdk
import pytz
import logging


logger = logging.getLogger(__name__)


KEEP_RUNNING = True


def stop_callback(signum, frame):
    logger.info('Received shutdown signal. Stopping main loop...')
    global KEEP_RUNNING
    KEEP_RUNNING = False


def configure_signals():
    signal.signal(signal.SIGTERM, stop_callback)
    signal.signal(signal.SIGINT, stop_callback)


async def timer_monitor():
    logger.info('Starting monitoring service')
    while KEEP_RUNNING:
        now = get_now()
        auction = await get_minimum_timer_auction(now)
        if auction is None:
            logger.info(
                "No pending auctions at the moment",
                extra={
                    "MESSAGE_ID": "MONITORING_TICK_EMPTY",
                }
            )
        else:
            timer = pytz.utc.localize(auction["timer"]).astimezone(TZ)
            offset = (now - timer).total_seconds()
            if offset > MONITOR_TIMER_WARNING_LIMIT:
                if offset > MONITOR_TIMER_ERROR_LIMIT:
                    log = logger.error
                else:
                    log = logger.warning
            else:
                log = logger.info
            log(
                f"Min timer is {timer} that's off by {offset}",
                extra={
                    "MESSAGE_ID": "MONITORING_TICK_TIME",
                    "TIMER": timer,
                    "OFFSET": offset,
                    "AUCTION_ID": auction['_id'],
                }
            )
        await asyncio.sleep(MONITOR_INTERVAL_SECONDS)


async def pending_count():
    logger.info('Starting pending auctions monitoring')
    while KEEP_RUNNING:
        count = await get_auction_count_by_timer(get_now())
        logger.info(
            f"{count} auctions ready for chronograph",
            extra={
                "MESSAGE_ID": "MONITORING_PENDING_COUNT",
                "COUNT": count,
            }
        )

        await asyncio.sleep(MONITOR_INTERVAL_SECONDS)


if __name__ == '__main__':
    configure_signals()
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN)

    setup_logging()
    update_log_context(SYSLOG_IDENTIFIER="AUCTION_MONITORING")

    loop = asyncio.get_event_loop()

    if MONITOR_PENDING_AUCTION:
        loop.create_task(pending_count())

    if MONITOR_TIMER:
        loop.create_task(timer_monitor())

    loop.run_until_complete(metrics_main())
