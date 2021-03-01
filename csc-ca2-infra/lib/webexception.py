from http import HTTPStatus

from lib.constants import ISE_ERROR_MESSAGE

class WebException(Exception):
    def __init__(self, status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message = ISE_ERROR_MESSAGE):
        super().__init__()
        self.status_code = status_code
        self.message = message
