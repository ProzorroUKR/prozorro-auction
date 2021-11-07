from aiohttp.test_utils import AioHTTPTestCase
from prozorro_auction.api.main import create_application


class BaseTestCase(AioHTTPTestCase):

    async def setUpAsync(self):
        pass

    async def get_application(self):
        self.app = create_application()
        return self.app

