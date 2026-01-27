from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, Path, status

from src.dependency.dependencies import get_task_service
from src.model.filters import TaskFilterParams
from src.model.tasks import (
    StatusResponse,
    TagCreate, TagResponse,
    TaskCreate, TaskResponse, TaskUpdate
)
from src.repository.tasks.dto import TaskCreateDTO, TaskUpdateDTO
from src.service.tasks import TaskService

router_v1 = APIRouter()


# Статус:
@router_v1.get(
    "/status",
    status_code=status.HTTP_200_OK,
    response_model=list[StatusResponse]
)
async def get_all_statuses(
    service: Annotated[TaskService, Depends(get_task_service)]
) -> list[StatusResponse]:
    return await service.get_all_statuses()


# Тег:
@router_v1.post(
    "/tag",
    status_code=status.HTTP_201_CREATED,
    response_model=TagResponse
)
async def create_tag(
    data: Annotated[TagCreate, Body()],
    service: Annotated[TaskService, Depends(get_task_service)]
) -> TagResponse:
    return await service.create_tag(data)


@router_v1.delete(
    "/tag/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tag(
    tag_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)]
) -> None:
    return await service.delete_tag(tag_id)


# Задача:
@router_v1.post(
    "/task",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse
)
async def create_task(
    data: Annotated[TaskCreate, Body()],
    service: Annotated[TaskService, Depends(get_task_service)]
) -> TaskResponse:
    return await service.create_task(data)

# TODO:

# @router_v1.get(
#         "task",
#         status_code=status.HTTP_200_OK,
#         response_model=list[TaskResponse]
# )
# async def get_tasks(
#     service: Annotated[TaskService, Depends(get_task_service)],
#     filters: Annotated[FilterParams, Query()]
# ) -> list[TaskResponse]:
#     """Возвращает список задач."""
#     tasks_db = await service.get_all_tasks(filters)
#     return [TaskResponse(**task.model_dump()) for task in tasks_db]


# @router_v1.get(
#     "/{task_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=TaskResponse
# )
# async def get_task(
#     # ???
#     task_id: int,
#     service: Annotated[TaskService, Depends(get_task_service)]
# ) -> TaskResponse:
#     """Получает задачу по его id."""
#     try:
#         task_db = await service.get_task_by_id(task_id)
#         return TaskResponse(**task_db.model_dump())
#     except TaskNotFoundException as e:
#         raise HTTPException(status_code=404, detail=f"Ошибка: {e}")


# @router_v1.delete(
#     "/{task_id}",
#     status_code=status.HTTP_204_NO_CONTENT
# )
# async def delete_task(
#     task_id: int,
#     service: Annotated[TaskService, Depends(get_task_service)]
# ) -> None:
#     """Удаляет задачу."""
#     try:
#         await service.delete_task(task_id)
#         return None
#     except TaskNotFoundException as e:
#         raise HTTPException(status_code=404, detail=f"Ошибка: {e}")


# @router_v1.patch(
#     "/{task_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=TaskResponse
# )
# async def patch_task(
#     task_id: int,
#     data: TaskUpdate,
#     service: Annotated[TaskService, Depends(get_task_service)]
# ):
#     """Обновляет поля задачи, которые были переданы."""
#     try:
#         task_dto = TaskUpdateDTO(**data.model_dump(exclude_unset=True))
#         updated_task_db = await service.update_task(task_id, task_dto)
#         return TaskResponse(**updated_task_db.model_dump())
#     except TaskNotFoundException as e:
#         raise HTTPException(status_code=404, detail=f"Ошибка: {e}")
