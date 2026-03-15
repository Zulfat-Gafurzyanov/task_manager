from typing import Annotated

from fastapi import (
    APIRouter, Depends, Body, Path, UploadFile, File,
    status, Security as FastAPISecurity
)
from src.api.deps import get_task_service
from src.core.security import Security
from src.model.filters import TaskFilterParams
from src.model.tasks import (
    DocumentResponse,
    StatusResponse,
    TagCreate, TagResponse,
    TaskCreate, TaskResponse, TaskUpdate
)
from src.model.users import UserBase
from src.service.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ===== Status =====

@router.get(
    "/status",
    response_model=list[StatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о всех статусах"
)
async def get_all_statuses(
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:read"])
    ]
) -> list[StatusResponse]:
    return await service.get_all_statuses()


# ===== Tag =====

@router.post(
    "/tag",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тег"
)
async def create_tag(
    data: Annotated[TagCreate, Body()],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> TagResponse:
    return await service.create_tag(data, current_user.id)


@router.delete(
    "/tag/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тег"
)
async def delete_tag(
    tag_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> None:
    await service.delete_tag(tag_id, current_user.id)


# ===== Task =====

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу"
)
async def create_task(
    data: Annotated[TaskCreate, Body()],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> TaskResponse:
    return await service.create_task(data, current_user.id)


@router.get(
    "",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о всех задачах"
)
async def get_tasks(
    service: Annotated[TaskService, Depends(get_task_service)],
    filters: Annotated[TaskFilterParams, Depends()],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:read"])
    ]
) -> list[TaskResponse]:
    return await service.get_all_tasks(filters, current_user.id)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,    
    summary="Получить информацию о конкретной задаче"
)
async def get_task(
    task_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:read"])
    ]
) -> TaskResponse:
    return await service.get_task_by_id(task_id, current_user.id)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Частичное обновление задачи"
)
async def patch_task(
    task_id: Annotated[int, Path(gt=0)],
    data: Annotated[TaskUpdate, Body()],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> TaskResponse:
    return await service.update_task(task_id, data, current_user.id)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление задачи"
)
async def delete_task(
    task_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> None:
    await service.delete_task(task_id, current_user.id)


# ===== TaskTag =====


@router.get(
    "/{task_id}/tag/",
    response_model=list[TagResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить все теги задачи"
)
async def get_task_tags(
    task_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
):
    return await service.get_task_tags(task_id, current_user.id)


@router.post(
    "/{task_id}/tag/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Добавить тег к задаче"
)
async def add_tag_to_task(
    task_id: Annotated[int, Path(gt=0)],
    tag_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> None:
    await service.add_tag_to_task(task_id, tag_id, current_user.id)


@router.delete(
    "/{task_id}/tag/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тег задачи"
)
async def remove_tag_from_task(
    task_id: Annotated[int, Path(gt=0)],
    tag_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> None:
    await service.remove_tag_from_task(task_id, tag_id, current_user.id)


# ===== Document =====

@router.post(
    "/{task_id}/document",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить документ к задаче"
)
async def upload_document(
    task_id: Annotated[int, Path(gt=0)],
    file: Annotated[UploadFile, File()],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> DocumentResponse:
    return await service.upload_document(task_id, file, current_user.id)


@router.get(
    "/{task_id}/document",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о всех документах задачи"
)
async def get_task_documents(
    task_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:read"])
    ]
) -> list[DocumentResponse]:
    return await service.get_task_documents(task_id, current_user.id)


@router.delete(
    "/document/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить документ"
)
async def delete_document(
    document_id: Annotated[int, Path(gt=0)],
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[
        UserBase,
        FastAPISecurity(Security.get_current_user, scopes=["tasks:write"])
    ]
) -> None:
    await service.delete_document(document_id, current_user.id)
