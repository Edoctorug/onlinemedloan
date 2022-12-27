from rest_framework import status


class BaseExceptionManager(Exception):
    message = ""
    action_id = 0
    action_name = None
    status = status.HTTP_400_BAD_REQUEST
    code = -1

    def __init__(self, message="", code=-1, **kwargs):
        if message == "":
            message = self.message
        else:
            self.message = message

        self.kwargs = kwargs

        if code == -1:
            code = self.code
        else:
            self.code = code

        super().__init__(message, code)
