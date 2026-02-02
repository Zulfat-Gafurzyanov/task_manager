import datetime
import uuid

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Декларативный базовый класс для моделей."""
    pass


# class Document(Base):
#     """
#     Справочник по документам к задаче.
#     Связь: Task (one) <-> Document (many).
#     """
#     __tablename__ = "document"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(128))
#     path: Mapped[str] = mapped_column(String(256), unique=True)
#     task_id: Mapped[int | None] = mapped_column(
#         ForeignKey("task.id"), nullable=True)


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


# ===== Пользователи и роли =====


class User(Base):
    """Модель пользователя."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(256))
    phone: Mapped[str | None] = mapped_column(String(256), nullable=True)


class Rule(Base):
    """Справочник ролей/прав доступа."""
    __tablename__ = "rule"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)


class UserRule(Base):
    """
    Связующая таблица между пользователями и ролями.
    Связь: User (many) <-> Rule (many).
    """
    __tablename__ = "userrule"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    rule_id: Mapped[int] = mapped_column(ForeignKey("rule.id"))
