class CustomException(Exception):
    """Base class for custom exception classes."""

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(f"Error {self.status_code}: {self.message}")


class InvalidTableNameError(CustomException):
    def __init__(self, table_name):
        super().__init__(message=f'The table name "{table_name}" is invalid.', status_code=400)


class AddError(CustomException):
    def __init__(self):
        super().__init__(message="Error in database Add operation.", status_code=400)


class ReadError(CustomException):
    def __init__(self):
        super().__init__(message="Error in database read operation. Please verify the query params and try again.", status_code=400)


class ReadGetError(CustomException):
    def __init__(self, param):
        super().__init__(message=f'Unable to retrieve movies for requested params: {param}', status_code=400)


class UpdateNoResultFoundError(CustomException):
    def __init__(self, id_no):
        super().__init__(message=f'Cannot find item for the requested id: {id_no}', status_code=400)


class UpdateError(CustomException):
    def __init__(self):
        super().__init__(message="Error in database update operation. Please verify the fields.", status_code=400)


class DeleteError(CustomException):
    def __init__(self):
        super().__init__(message="Error in database delete operation.", status_code=400)


class DeleteNoResultFoundError(CustomException):
    def __init__(self, id_no):
        super().__init__(message=f'Cannot find item for the requested id: {id_no}', status_code=400)


class InvalidParameterError(CustomException):
    def __init__(self, field):
        super().__init__(message=f"{field} field missing. Operation Failed", status_code=400)


def create_error_status(exception: CustomException):
    """
    Creates an error status response based on the given exception
    :param exception: CustomException containing the status_code and message
    :return: The created error status response
    """
    return {
        'status_code': exception.status_code,
        'error': exception.message}
