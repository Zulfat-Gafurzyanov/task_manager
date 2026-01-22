from fastapi import status


class ResourceAlreadyExistsException(Exception):
    """Ресурс уже существует."""
    def __init__(self, resource: str, resource_name: str):
        self.resource = resource
        self.message = (
            f'{resource} c таким именем "{resource_name}" уже существует')
        self.status_code = status.HTTP_404_NOT_FOUND


class ResourceNotFoundException(Exception):
    """Ресурс не найден."""
    def __init__(self, resource: str, resource_id: int):
        self.resource = resource
        self.resource_id = resource_id
        self.message = f"{resource} с id={resource_id} не найден"
        self.status_code = status.HTTP_409_CONFLICT
