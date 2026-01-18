import datetime

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Декларативный базовый класс для моделей."""
    pass


class Document(Base):
    """
    Справочник по документам к задаче.
    Связь: Task (one) <-> Document (many).
    """
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    path: Mapped[str] = mapped_column(String(256), unique=True)
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("task.id"), nullable=True)  # ??? Если nullable=True - значит можно создать отдельно документ, и он не будет привязан ни к какой задаче. Это правильный подход?


class Status(Base):
    """
    Справочник по статусу к задаче.
    Связь: Task (many) <-> Status (one).
    """
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)


class TaskTag(Base):
    """
    Связующая таблица между задачами и тегами.
    Связь: Task (many) <-> Tag (many).
    """
    __tablename__ = "tasktag"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"))


class Tag(Base):
    """Справочник по тегам к задачам."""
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)


class Task(Base):
    """Модель задачи для хранения в базе данных."""
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(
        String(264), nullable=True)
    deadline_start: Mapped[datetime.date | None] = mapped_column(
        Date, nullable=True)
    deadline_end: Mapped[datetime.date | None] = mapped_column(
        Date, nullable=True)
    status_id: Mapped[int | None] = mapped_column(
        ForeignKey("status.id"), nullable=True)
