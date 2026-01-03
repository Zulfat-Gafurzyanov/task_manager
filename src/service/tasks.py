from src.model.filters import FilterParams
from src.repository.tasks.dto import TaskCreateDTO, TaskDTO, TaskUpdateDTO
from src.repository.tasks.tasks import TaskRepository


# ???
# Что помимо вызова функций из репозитория, должно входить в бизнес-логику сервис-слоя?
# Не понимаю где должна быть:
# - валидация: если есть валидация данных от пользователя в src.model нужно ли делать ее в DTO или в сервис-слое?
# - обработка исключений: в API? в сервис-слое? в репозитории? Где мы их пробрасываем, а где обрабатываем?
class TaskService:
    """Класс для описания бизнес-логики."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, data: TaskCreateDTO) -> TaskDTO:
        """Создает задачу."""
        return self.repository.create(data)

    def get_all_tasks(self, filters: FilterParams) -> list[TaskDTO]:
        """Получает все задачи с учётом фильтров (limit, offset)."""
        return self.repository.read_all(filters)

    def get_task_by_id(self, id: int) -> TaskDTO | None:
        """Получает задачу по его id."""
        return self.repository.read_by_id(id)

    def update_task(self, id: int, data: TaskUpdateDTO) -> TaskDTO | None:
        """Обновляет поля задачи."""
        return self.repository.update(id, data)

    def delete_task(self, id: int) -> bool:
        """Удаляет задачу."""
        return self.repository.delete(id)
