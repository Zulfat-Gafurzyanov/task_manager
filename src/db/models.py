import datetime

from sqlalchemy import Column, Date, ForeignKey, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Декларативный базовый класс для моделей."""
    pass


# Вспомогательная таблица для связи many to many:
TaskTag = Table(
    "tasks_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)


class Document(Base):
    """Справочник по документам к задаче."""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    path: Mapped[str] = mapped_column(String(256), unique=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"))

    # Связь 1 to many:
    task: Mapped["Task | None"] = relationship(
        "Task", back_populates="documents")


class Status(Base):
    """Справочник по статусу к задаче."""
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    # Связь 1 to many:
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="status")


class Tag(Base):
    """Справочник по тегам к задачам."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    # Связь many to many (через вспомогательную таблицу):
    tasks: Mapped[list["Task"]] = relationship(
        "Task", secondary=TaskTag, back_populates="tags")


class Task(Base):
    """Модель задачи для хранения в базе данных."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(String(264))
    status_id: Mapped[int | None] = mapped_column(ForeignKey("statuses.id"))
    deadline_start: Mapped[datetime.date | None] = mapped_column(Date)
    deadline_end: Mapped[datetime.date | None] = mapped_column(Date)

    # Связь 1 to many:
    status: Mapped["Status | None"] = relationship(
        "Status", back_populates="tasks")
    # Связь many to many (через вспомогательную таблицу):
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=TaskTag, back_populates="tasks")
    # Связь 1 to many:
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="task")
