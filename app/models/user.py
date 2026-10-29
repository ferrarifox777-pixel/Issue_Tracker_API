from sqlalchemy.orm import Mapped, mapped_column, relationship # <-- добавили relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default="developer") # admin, developer, qa
    created_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys="[Task.author_id]")
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys="[Task.assignee_id]")