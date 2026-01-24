from fastapi import status


class AppException(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceAlreadyExistsException(AppException):
    """Ресурс уже существует."""
    def __init__(self, resource: str, resource_name: str):
        self.resource = resource

        message = (
            f'{resource} c таким именем "{resource_name}" уже существует.')
        status_code = status.HTTP_409_CONFLICT
        super().__init__(message, status_code)


class ResourceNotFoundException(AppException):
    """Ресурс не найден."""
    def __init__(self, resource: str, resource_id: int):
        self.resource = resource
        self.resource_id = resource_id

        message = f"{resource} с id={resource_id} не найден."
        status_code = status.HTTP_404_NOT_FOUND
        super().__init__(message, status_code)
