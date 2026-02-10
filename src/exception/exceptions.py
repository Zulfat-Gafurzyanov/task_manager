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


class ResourceByIdNotFoundException(AppException):
    """Ресурс не найден (поиск по id)."""
    def __init__(self, resource: str, resource_id: int):
        self.resource = resource
        self.resource_id = resource_id

        message = f"{resource} с id={resource_id} не найден(а)."
        status_code = status.HTTP_404_NOT_FOUND
        super().__init__(message, status_code)


class ResourceByNameNotFoundException(AppException):
    """Ресурс не найден (поиск по имени)."""
    def __init__(self, resource: str, resource_name: str):
        self.resource = resource
        self.resource_name = resource_name

        message = f"{resource} с именем: {resource_name} не найден(а)."
        status_code = status.HTTP_404_NOT_FOUND
        super().__init__(message, status_code)


class ResourceNotCreatedException(AppException):
    """Ресурс не создан."""
    def __init__(self, resource: str):
        self.resource = resource

        message = f"{resource} не удалось создать."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(message, status_code)
