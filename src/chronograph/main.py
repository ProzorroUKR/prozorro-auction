from storage import read_expired_timer_and_update
from chronograph.model import tick_auction
from settings import logger
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
        async with read_expired_timer_and_update() as auction:
            if not auction:
                logger.debug('No auctions needs to be updated. nooping')
                await asyncio.sleep(1)
                continue
            try:
                await tick_auction(auction)
            except Exception as ex:
                # auction.timer = None
                logger.exception(f'Unexpected error during timer processing {str(ex)}')


if __name__ == '__main__':
    configure_signals()
    asyncio.run(chronograph_loop())
