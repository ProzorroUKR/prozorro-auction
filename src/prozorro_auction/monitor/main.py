from prozorro_auction.monitor.settings import (
    MONITOR_TIMER_WARNING_LIMIT,
    MONITOR_TIMER_ERROR_LIMIT,
    MONITOR_INTERVAL_SECONDS,
    MONITOR_PENDING_AUCTION,
)
from prozorro_auction.monitor.storage import get_minimum_timer_auction, get_pending_count
from prozorro_auction.settings import logger, SENTRY_DSN, TZ
from prozorro_auction.utils.base import get_now
import asyncio
import signal
import sentry_sdk
import pytz


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
        count = await get_pending_count(get_now())
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

    loop = asyncio.get_event_loop()

    if MONITOR_PENDING_AUCTION:
        loop.create_task(pending_count())

    loop.run_until_complete(timer_monitor())
