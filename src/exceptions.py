

class RetryException(Exception):
    pass


class RequestRetryException(RetryException):

    def __init__(self, timeout=0):
        self.timeout = timeout
        super(RequestRetryException, self).__init__()
