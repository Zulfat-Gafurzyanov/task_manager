import json
from typing import Annotated

from fastapi import (
    APIRouter, Depends, Path, Security as FastAPISecurity,
    status, HTTPException
)

from src.api.deps import get_task_service
from src.broker.rpc_publisher import rpc_publisher
from src.core.security import Security
from src.model.users import UserBase
from src.service.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["assignments"])

ASSIGNMENT_QUEUE = "task_assignment_queue"


@router.post(
    "/{task_id}/assignee/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Назначить пользователя на задачу"
)
async def add_assignee(
    task_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> None:
    await service.get_task_by_id(task_id, current_user.id)
    result = await rpc_publisher.call(
        json.dumps({"action": "add", "task_id": task_id, "user_id": user_id}),
        ASSIGNMENT_QUEUE
    )
    response = json.loads(result)
    if response.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=response["detail"])


@router.delete(
    "/{task_id}/assignee/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Снять пользователя с задачи"
)
async def remove_assignee(
    task_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> None:
    await service.get_task_by_id(task_id, current_user.id)
    await rpc_publisher.call(
        json.dumps(
            {"action": "remove", "task_id": task_id, "user_id": user_id}),
        ASSIGNMENT_QUEUE
    )


@router.get(
    "/{task_id}/assignees",
    status_code=status.HTTP_200_OK,
    summary="Получить список назначенных пользователей"
)
async def get_assignees(
    task_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:read"])
    ]
) -> list[int]:
    await service.get_task_by_id(task_id, current_user.id)
    result = await rpc_publisher.call(
        json.dumps({"action": "list", "task_id": task_id}),
        ASSIGNMENT_QUEUE
    )
    response = json.loads(result)
    return response.get("data", [])
