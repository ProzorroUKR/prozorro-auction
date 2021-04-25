import unittest

from unittest.mock import patch, Mock, call

from prozorro_auction.utils import get_now
from prozorro_auction.settings import TZ


class UtilsCase(unittest.TestCase):

    @patch('prozorro_auction.utils.datetime')
    def test_get_now(self, now_mock):
        now = "hello"
        now_mock.now.return_value = now

        result = get_now()

        now_mock.now.assert_called_once_with(tz=TZ)
        assert result == now

