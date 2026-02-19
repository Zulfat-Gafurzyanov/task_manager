import datetime

from sqlalchemy import BigInteger, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    path: Mapped[str] = mapped_column(String(256), unique=True)
    task_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("task.id", ondelete="CASCADE"),
        index=True
    )


class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)


class TaskTag(Base):
    """Связующая таблица: Task (many) <-> Tag (many)."""
    __tablename__ = "tasktag"
    __table_args__ = (UniqueConstraint("task_id", "tag_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("task.id"),
        index=True
    )
    tag_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tag.id"),
        index=True
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True
    )


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(
        String(2048), nullable=True)
    deadline_start: Mapped[datetime.date | None] = mapped_column(
        Date, nullable=True)
    deadline_end: Mapped[datetime.date | None] = mapped_column(
        Date, nullable=True)
    status_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("status.id"),
        nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True
    )


# ===== User =====

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(512))
    email: Mapped[str] = mapped_column(String(512))
    phone: Mapped[str | None] = mapped_column(String(512), nullable=True)
    role: Mapped[str] = mapped_column(String(32), default="user")
