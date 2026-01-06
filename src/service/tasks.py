from src.model.filters import FilterParams
from src.repository.tasks.dto import TaskCreateDTO, TaskDTO, TaskUpdateDTO
from src.repository.tasks.tasks import TaskRepository


class TaskNotFoundException(Exception):
    """Исключение, возникающее когда задача не найдена по id."""
    pass


# ???
# Что помимо вызова функций из репозитория и проброса исключений,
# может входить в бизнес-логику сервис-слоя?
class TaskService:
    """Класс для описания бизнес-логики."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def _get_task_or_raise(
            self, task: TaskDTO | None, task_id: int) -> TaskDTO:
        """Проверяет наличие задачи по id,
        если ее нет то выбрасывает исключение."""
        if not task:
            raise TaskNotFoundException(f"Задача с id: {task_id} не найдена.")
        return task

    async def create_task(self, data: TaskCreateDTO) -> TaskDTO:
        """Создает задачу."""
        return await self.repository.create(data)

    async def get_all_tasks(self, filters: FilterParams) -> list[TaskDTO]:
        """Получает все задачи с учётом фильтров (limit, offset)."""
        return await self.repository.read_all(filters)

    async def get_task_by_id(self, id: int) -> TaskDTO:
        """Получает задачу по его id."""
        task = await self.repository.read_by_id(id)
        return self._get_task_or_raise(task, id)

    async def update_task(self, id: int, data: TaskUpdateDTO) -> TaskDTO:
        """Обновляет поля задачи."""
        updated_task = await self.repository.update(id, data)
        return self._get_task_or_raise(updated_task, id)

    async def delete_task(self, id: int) -> bool:
        """Удаляет задачу."""
        deleted_task = await self.repository.delete(id)
        if not deleted_task:
            raise TaskNotFoundException(f"Задача с id: {id} не найдена.")
        return True
        # ???
        # Здесь не смог придумать как использовать _check_task
        # потому что self.repository.delete(id) возвращает bool
        # а _check_task ждет TaskDTO | None. Как лучше сделать?

        # !!! из мыслей исправить в repository возврат сделать не bool,
        # a TaskDTO | None, но не понимаю стоит ли после удаления task из бд,
        # возвращать в функции delete его копию в виде TaskDTO

        # Что имею ввиду repository.delete(id):
        # async def delete(self, id: int) -> TaskDTO | None:
        #     task = await self.session.get(Task, id)
        #     if not task:
        #         return None  ---->  (вместо False)
        #     task_dto = TaskDTO.model_validate(task)
        #     await self.session.delete(task)
        #     await self.session.commit()
        #     return task_dto  ---->  (вместо True)
