from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.dependency.tasks import get_task_service
from src.model.filters import TaskFilterParams
from src.model.tasks import Status #TaskCreate, TaskResponse, TaskUpdate
from src.repository.tasks.dto import TaskCreateDTO, TaskUpdateDTO
from src.service.tasks import TaskNotFoundException, TaskService

router_v1 = APIRouter()


@router_v1.get(
    "/status/{status_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[Status]
)
async def get_all_statuses(
    service: Annotated[TaskService, Depends(get_task_service)]
) -> list[Status]:
    return await service.get_all_statuses()
    


# @router_v1.post(
#     "",
#     status_code=status.HTTP_201_CREATED,
#     response_model=TaskResponse
# )
# async def create_task(
#     data: TaskCreate,
#     service: Annotated[TaskService, Depends(get_task_service)]
# ) -> TaskResponse:
#     """Создает задачу."""
#     task_dto = TaskCreateDTO(**data.model_dump())
#     task_db = await service.create_task(task_dto)
#     return TaskResponse(**task_db.model_dump())


# @router_v1.get(
#         "",
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
#     # нужно делать? task_id: Annotated[int, Path(gt=0)] вдруг введут /-1
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
