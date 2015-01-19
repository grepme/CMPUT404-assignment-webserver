#
# Welcome to all the valid HTTPErrors for this assignment!
#


class HTTPError(Exception):

    def __init__(self):
        pass

    def finish(self):
        """Every HTTPError must handle the exception and clean up after itself.
        This should be inherited but provided it is not, a pass is given."""
        pass


class HTTPForbiddenError(HTTPError):
    """A 403 error with a message"""
    def __init__(self, request, message):
        self.request = request
        self.message = message

    def finish(self):
        self.request.sendall("HTTP/1.1 403 Forbidden\r\n\r\n")
        self.request.sendall(self.message)


class HTTPNotFound(HTTPError):
    """A 404 Error with a message"""
    def __init__(self, request, message):
        self.request = request
        self.message = message

    def finish(self):
        self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n")
        self.request.sendall(self.message)
