from pydantic import BaseModel, ConfigDict
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    assignee_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    # При обновлении все поля опциональны
    title: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)