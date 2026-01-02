from datetime import datetime, timezone

from sqlmodel import select

from src.database.connection import SessionDep
from src.database.models import Task
from src.model.filters import FilterParams
from src.repository.tasks.dto import TaskCreateDTO, TaskDTO, TaskUpdateDTO


# ???
# Нужно ли в TaskRepository методы делать асинхронными? Если engine - будет асинхронным)
class TaskRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def create(self, data: TaskCreateDTO) -> TaskDTO:
        """Создает задачу."""
        task = Task(
            name=data.name,
            description=data.description,
            deadline=data.deadline,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return TaskDTO.model_validate(task)

    def read_all(self, filters: FilterParams) -> list[TaskDTO]:
        """Получает все задачи с учётом фильтров."""
        statement = select(Task).offset(filters.offset).limit(filters.limit)
        tasks = self.session.exec(statement).all()
        return [TaskDTO.model_validate(task) for task in tasks]

    def read_by_id(self, task_id: int) -> TaskDTO | None:
        """Получает задачу по его id."""
        # ???
        # в документации SQLModel select(Hero).where(Hero.name == "Deadpond")
        # а в FastAPI hero = session.get(Hero, hero_id)
        # как лучше?
        task = self.session.get(Task, task_id)
        if not task:
            return None
            # ??? Нужно ли в работе с DTO пробрасывать исключения?
            # raise TaskNotFound(f"Задача с id: {task_id} не найдена")
            # или их нужно только в API при взаимодействии с клиентом?
        return TaskDTO.model_validate(task)

    def update(self, task_id: int, data: TaskUpdateDTO) -> TaskDTO | None:
        """Обновляет задачу."""
        task = self.session.get(Task, task_id)
        if not task:
            return None

        for field, new_value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, new_value)

        self.session.commit()
        self.session.refresh(task)
        return TaskDTO.model_validate(task)


    def delete(self, task_id: int) -> bool:
        """Удаляет задачу. Возвращает True, если задача удалена."""
        task = self.session.get(Task, task_id)
        # ???
        # Есть ли разница в проверке if task или в if not task?
        # if task:
        #     self.session.delete(task)
        #     self.session.commit()
        #     return True
        # return False
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    # ???
    # Нужны ли методы по другим полям: get_by_name? delete_by_name?
    # Или например получение активных задач? get_active?
    # Или CRUD в Repository не должен быть раздутым?


#repository = TaskRepository(session)