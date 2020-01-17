

class SkipException(Exception):
    pass


class RetryException(Exception):
    pass


class RequestRetryException(RetryException):

    def __init__(self, timeout=0, response=None):
        self.timeout = timeout
        self.response = response
        super(RequestRetryException, self).__init__()
