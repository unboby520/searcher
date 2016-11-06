# coding:utf8
"""

Author: ilcwd
"""

from . import errorcode

class BaseServiceException(Exception):

    def __init__(self, error_code, error=None, retry_interval=0, extra=None):
        self.error_code = int(error_code)
        self.error = error
        self.retry_interval = abs(int(retry_interval))
        self.extra = extra.copy() if extra else None

    def dictify(self):
        obj = {'error_code': self.error_code}
        if self.error:
            obj['error'] = self.error
        if self.retry_interval:
            obj['retryable'] = 1
            obj['retry_interval'] = self.retry_interval
        if self.extra:
            obj.update(self.extra)

        return obj



class APIException(BaseServiceException):
    pass


SERVER_ERROR_EXCEPTION = APIException(errorcode.SERVER_ERROR, "server error")