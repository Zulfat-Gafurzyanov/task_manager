from fastapi import FastAPI

from src.api.v1 import tasks


app = FastAPI()
app.include_router(tasks.router, prefix="/v1", tags=["tasks"])

task_db: dict = {}
