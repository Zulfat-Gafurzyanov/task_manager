from datetime import datetime, timezone

from sqlmodel import select

from src.db.connection import SessionDep
from src.db.models import Task
from src.model.filters import FilterParams
from src.repository.tasks.dto import TaskCreateDTO, TaskDTO, TaskUpdateDTO


class TaskRepository:
    """
    Репозиторий для работы с задачами в базе данных.

    Предоставляет CRUD-операции для Task, работая с DTO-объектами.
    Изолирует бизнес-логику от реализации базы данных.
    """
    def __init__(self, session: SessionDep):
        self.session = session

    async def create(self, data: TaskCreateDTO) -> TaskDTO:
        """Создает задачу."""
        task = Task(
            name=data.name,
            description=data.description,
            deadline=data.deadline,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return TaskDTO.model_validate(task)

    async def read_all(self, filters: FilterParams) -> list[TaskDTO]:
        """Получает все задачи с учётом фильтров."""
        statement = select(Task).offset(filters.offset).limit(filters.limit)
        result = await self.session.execute(statement)
        tasks = result.all()
        return [TaskDTO.model_validate(task[0]) for task in tasks]

    async def read_by_id(self, id: int) -> TaskDTO | None:
        """Получает задачу по его id."""
        # ???
        # в документации SQLModel написано:     select(Hero).where(Hero.name == "Deadpond")
        # а в FastAPI:                          hero = session.get(Hero, hero_id)
        # как лучше get или where?
        task = await self.session.get(Task, id)
        if not task:
            return None
        return TaskDTO.model_validate(task)

    async def update(self, id: int, data: TaskUpdateDTO) -> TaskDTO | None:
        """Обновляет поля задачи."""
        task = await self.session.get(Task, id)
        if not task:
            return None
        for field, new_value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, new_value)
        await self.session.commit()
        await self.session.refresh(task)
        return TaskDTO.model_validate(task)

    async def delete(self, id: int) -> bool:
        """Удаляет задачу. Возвращает True, если задача удалена."""
        task = await self.session.get(Task, id)
        if not task:
            return False
        await self.session.delete(task)
        await self.session.commit()
        return True


    # ???
    # Нужны ли методы по другим полям: get_by_name? delete_by_name?
    # Или например получение активных задач? get_active?
    # Или CRUD в Repository не должен быть раздутым?
