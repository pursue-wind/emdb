class CustomException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundException(CustomException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)
