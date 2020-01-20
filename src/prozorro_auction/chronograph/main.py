from prozorro_auction.chronograph.storage import increase_and_read_expired_timer, update_auction
from prozorro_auction.chronograph.stages import tick_auction
from prozorro_auction.exceptions import RetryException
from prozorro_auction.settings import logger, PROCESSING_LOCK
from time import time
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


async def chronograph_loop():
    logger.info('Starting chronograph service')
    while KEEP_RUNNING:
        auction = await increase_and_read_expired_timer()
        if auction:
            _start_time = time()
            try:
                await tick_auction(auction)
            except RetryException as e:
                logger.warning(e, extra={"MESSAGE_ID": "CHRONOGRAPH_TICK_RETRY"})
            except Exception as ex:
                # auction.timer = None
                logger.exception(ex, extra={"MESSAGE_ID": "CHRONOGRAPH_TICK_EXCEPTION"})
            else:
                await update_auction(auction)

                processing_time = time() - _start_time
                if processing_time >= PROCESSING_LOCK:
                    message = (
                        f"Auction {auction['_id']} processing time equals to {processing_time} seconds"
                        f"and is bigger than processing lock time - {PROCESSING_LOCK} seconds."
                        "This may lead to inconsistency of data!"
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
