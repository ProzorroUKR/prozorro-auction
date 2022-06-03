from prozorro_auction.chronograph.storage import increase_and_read_expired_timer, update_auction
from prozorro_auction.chronograph.stages import tick_auction, POSTPONE_ANNOUNCEMENT_TD
from prozorro_auction.chronograph.model import get_verbose_current_stage
from prozorro_auction.chronograph.metrics import (
    main as metrics_main,
    chronograph_processing_time_summary,
    chronograph_total_time_summary,
)
from prozorro_auction.exceptions import RetryException
from prozorro_auction.settings import TZ, SENTRY_DSN
from prozorro_auction.utils.base import get_now
from prozorro_auction.logging import setup_logging, update_log_context, log_context
from datetime import timedelta
from time import time
import pytz
import asyncio
import signal
import sentry_sdk
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


async def postpone_timer_on_error(auction):
    """
    if an auction stage raises an exception,
    we run retries with increased intervals
    and finally we discard these tasks completely
    :return:
    """
    data = {"_id": auction["_id"]}
    errors_count = auction.get("chronograph_errors_count", 0)
    errors_count += 1
    if errors_count < 1000:
        data.update(
            timer=auction["timer"] + timedelta(seconds=errors_count),
            chronograph_errors_count=errors_count,
        )
        logger.warning(f"Delaying auction processing for {errors_count} seconds")
    else:
        data.update(timer=None)
        logger.critical(f"Discarding processing auction")
    await update_auction(data, update_date=False)


async def chronograph_loop():
    logger.info('Starting chronograph service')
    while KEEP_RUNNING:
        before_fetch_time = time()
        auction = await increase_and_read_expired_timer()
        if auction:
            with log_context(AUCTION_ID=auction['_id']):
                timer = auction["timer"]
                before_run_time = time()
                try:
                    await tick_auction(auction)
                except RetryException as e:
                    logger.warning(e, extra={"MESSAGE_ID": "CHRONOGRAPH_TICK_RETRY"})
                    await postpone_timer_on_error(auction)
                except Exception as ex:
                    logger.exception(ex, extra={"MESSAGE_ID": "CHRONOGRAPH_TICK_EXCEPTION"})
                    await postpone_timer_on_error(auction)
                else:
                    before_save_time = time()
                    await update_auction(auction)
                    after_save_time = time()

                    processing_time = before_save_time - before_run_time
                    total_time = after_save_time - before_fetch_time
                    current_ts = get_now()
                    timer_time = pytz.utc.localize(timer).astimezone(TZ)
                    extra_log = {
                        "MESSAGE_ID": "CHRONOGRAPH_TICK_TIME",
                        "PROCESSING_TIME": processing_time,
                        "TOTAL_TIME": total_time,
                        "FETCH_TIME":  before_run_time - before_fetch_time,
                        "SAVE_TIME": after_save_time - before_save_time,
                        "AUCTION_STAGE": get_verbose_current_stage(auction),
                    }
                    if (
                        current_ts >= timer_time and not (
                            auction["timer"] is None and processing_time < POSTPONE_ANNOUNCEMENT_TD.total_seconds()
                            # it's been announcement stage
                            # that takes longer due to its communicates with API CDB
                        )
                    ):
                        logger.critical(
                            "Auction processing takes more than its lock. This may lead to inconsistency of data!",
                            extra=extra_log)
                    else:
                        logger.info(
                            f"Processed auction, time - {processing_time}",
                            extra=extra_log
                        )
                    # metrics update
                    chronograph_total_time_summary.observe(total_time)
                    chronograph_processing_time_summary.observe(processing_time)
        else:
            await asyncio.sleep(1)


if __name__ == '__main__':
    configure_signals()
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN)

    setup_logging()
    update_log_context(SYSLOG_IDENTIFIER="AUCTION_CHRONOGRAPH")

    loop = asyncio.get_event_loop()
    loop.create_task(metrics_main())
    loop.run_until_complete(chronograph_loop())
