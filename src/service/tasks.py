from sqlalchemy.exc import IntegrityError

from src.model.filters import TaskFilterParams
from src.model.tasks import (
    StatusResponse,
    TagCreate, TagResponse,
    TaskCreate, TaskResponse
)
from src.repository.tasks.dto import (
    TagCreateDTO,
    TaskCreateDTO, TaskResponseDTO, TaskUpdateDTO
)
from src.repository.cache import CacheRepository
from src.repository.tasks.tasks import TaskRepository
from src.exseption.tasks import (
    ResourceAlreadyExistsException,
    ResourceNotFoundException
)


class TaskService:
    """
    Сервисный слой для работы с задачами.

    Описывает бизнес-логику управления задачами,
    включая обработку исключений и взаимодействие с репозиторием.
    """

    def __init__(self, task_repo: TaskRepository, cache_repo: CacheRepository):
        self.task_repo = task_repo
        self.cache_repo = cache_repo

    # ===== Статус =====
    async def get_all_statuses(self) -> list[StatusResponse]:
        """Получает все статусы из БД."""
        # Проверяем кеш:
        cache_key = "statuses:all"
        cached = await self.cache_repo.get(cache_key)
        if cached:
            return [StatusResponse(**item) for item in cached]
        # Если нет кеша:
        statuses = await self.task_repo.get_all_statuses()
        result = [StatusResponse.model_validate(status) for status in statuses]
        # Кешируем:
        await self.cache_repo.set(
            cache_key,
            [status.model_dump() for status in result],
            ttl=3600
        )
        return result

    # ===== Тег =====
    async def create_tag(self, data: TagCreate) -> TagResponse:
        """Cоздает тег."""
        try:
            tag_dto = TagCreateDTO(name=data.name)
            created_tag = await self.task_repo.create_tag(tag_dto)
            return TagResponse(**created_tag.model_dump())
        except IntegrityError:
            raise ResourceAlreadyExistsException("Тег", data.name)

    async def delete_tag(self, tag_id: int) -> None:
        """Удаляет тег."""
        try:
            return await self.task_repo.delete_tag(tag_id)
        except ValueError:
            raise ResourceNotFoundException("Тег", tag_id)

    async def create_task(self, data: TaskCreate) -> TaskResponse:
        """Создает задачу."""
        try:
            task_dto = TaskCreateDTO(
                name=data.name,
                description=data.description,
                deadline_start=data.deadline_start,
                deadline_end=data.deadline_end,
                status_id=data.status_id
            )
            created_task = await self.task_repo.create_task(task_dto)
            return TaskResponse(**created_task.model_dump())
        except Exception:  # ??? Какой exception обрабатывать?
            raise

# TODO:
    # def _get_task_or_raise(
    #         self, task: TaskDTO | None, task_id: int) -> TaskDTO:
    #     """Проверяет наличие задачи по id,
    #     если ее нет то выбрасывает исключение."""
    #     if not task:
    #         raise TaskNotFoundException(f"Задача с id: {task_id} не найдена.")
    #     return task

    # async def get_all_tasks(self, filters: FilterParams) -> list[TaskDTO]:
    #     """Получает все задачи с учётом фильтров."""
    #     return await self.repository.read_all(filters)

    # async def get_task_by_id(self, id: int) -> TaskDTO:
    #     """Получает задачу по его id."""
    #     task = await self.repository.read_by_id(id)
    #     return self._get_task_or_raise(task, id)

    # async def update_task(self, id: int, data: TaskUpdateDTO) -> TaskDTO:
    #     """Обновляет поля задачи."""
    #     updated_task = await self.repository.update(id, data)
    #     return self._get_task_or_raise(updated_task, id)

    # async def delete_task(self, id: int) -> bool:
    #     """Удаляет задачу."""
    #     deleted_task = await self.repository.delete(id)
    #     if not deleted_task:
    #         raise TaskNotFoundException(f"Задача с id: {id} не найдена.")
    #     return True
    #     # ???
    #     # Здесь не смог придумать как использовать _get_task_or_raise
    #     # потому что self.repository.delete(id) возвращает bool
    #     # а _get_task_or_raise ждет TaskDTO | None. Как лучше сделать?

    #     # !!! из мыслей исправить в repository возврат сделать не bool,
    #     # a TaskDTO | None, но не понимаю стоит ли после удаления task из бд,
    #     # возвращать в функции delete его копию в виде TaskDTO

    #     # Что имею ввиду: в repository:
    #     # async def delete(self, id: int) -> TaskDTO | None:
    #     #     task = await self.session.get(Task, id)
    #     #     if not task:
    #     #         return None  ---->  (вернуть None вместо False)
    #     #     task_dto = TaskDTO.model_validate(task)
    #     #     await self.session.delete(task)
    #     #     await self.session.commit()
    #     #     return task_dto  ---->  (вернуть dto вместо True)
