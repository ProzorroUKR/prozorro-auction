from prozorro_auction.chronograph.storage import increase_and_read_expired_timer, update_auction
from prozorro_auction.chronograph.stages import tick_auction, POSTPONE_ANNOUNCEMENT_TD
from prozorro_auction.exceptions import RetryException
from prozorro_auction.settings import logger, TZ
from prozorro_auction.utils import get_now
from datetime import timedelta
from time import time
import pytz
import asyncio
import signal


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
        logger.warning(f"Delaying auction processing {auction['_id']} for {errors_count} seconds")
    else:
        data.update(timer=None)
        logger.critical(f"Discard auction processing {auction['_id']}")
    await update_auction(data, update_date=False)


async def chronograph_loop():
    logger.info('Starting chronograph service')
    while KEEP_RUNNING:
        auction = await increase_and_read_expired_timer()
        if auction:
            timer = auction["timer"]
            _start_time = time()
            try:
                await tick_auction(auction)
            except RetryException as e:
                logger.warning(e, extra={"MESSAGE_ID": "CHRONOGRAPH_TICK_RETRY"})
                await postpone_timer_on_error(auction)
            except Exception as ex:
                logger.exception(ex, extra={"MESSAGE_ID": "CHRONOGRAPH_TICK_EXCEPTION"})
                await postpone_timer_on_error(auction)
            else:
                await update_auction(auction)

                processing_time = time() - _start_time
                current_ts = get_now()
                timer_time = pytz.utc.localize(timer).astimezone(TZ)
                if (
                    current_ts >= timer_time and not (
                        auction["timer"] is None and processing_time < POSTPONE_ANNOUNCEMENT_TD.total_seconds()
                        # it's been announcement stage
                        # that takes longer due to its communicates with API CDB
                    )
                ):
                    message = (
                        f"Auction {auction['_id']} processing finished at {current_ts}, time - {processing_time}. "
                        f"While it's locked only by {auction['timer']} ({timer_time}). "
                        f"This may lead to inconsistency of data!"
                    )
                    logger.critical(message)
                else:
                    logger.info(f"Processed auction {auction['_id']}, time - {processing_time}")
        else:
            logger.debug('No auctions needs to be updated. nooping')
            await asyncio.sleep(1)


if __name__ == '__main__':
    configure_signals()
    asyncio.run(chronograph_loop())
