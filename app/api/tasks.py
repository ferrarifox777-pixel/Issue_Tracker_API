from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.db.database import get_async_session
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.api.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_in: TaskCreate,
        # Защищаем эндпоинт и получаем текущего юзера из токена:
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    # Создаем задачу, принудительно назначая автором того, кто сделал запрос
    new_task = Task(
        **task_in.model_dump(),
        author_id=current_user.id
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return new_task


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
        status: Optional[str] = None,  # Фильтр по статусу
        assignee_id: Optional[int] = None,  # Фильтр по исполнителю
        skip: int = 0,    # Сколько записей пропустить
        limit: int = 100, # Максимальное количество записей за раз
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    """Получить список задач с возможностью фильтрации."""
    query = select(Task)

    # Динамически собираем SQL-запрос
    if status:
        query = query.where(Task.status == status)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)

    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_update: TaskUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    """Обновить задачу (сменить статус, название или исполнителя)."""
    # Ищем задачу
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    # Превращаем входящие данные в словарь, исключая пустые поля (те, что не передали)
    update_data = task_update.model_dump(exclude_unset=True)

    # Обновляем атрибуты модели ORM
    for key, value in update_data.items():
        setattr(task, key, value)

    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        session: AsyncSession = Depends(get_async_session),
        # Сюда может зайти ТОЛЬКО пользователь с role="admin"
        current_user: User = Depends(get_current_admin_user)
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    await session.delete(task)
    await session.commit()