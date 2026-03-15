from fastapi import APIRouter

from src.api.v1.assignments import router as assigments_router
from src.api.v1.rpc import router as rpc_router
from src.api.v1.tasks import router as tasks_router
from src.api.v1.users import router as users_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(tasks_router)
v1_router.include_router(users_router)
v1_router.include_router(rpc_router)
v1_router.include_router(assigments_router)
