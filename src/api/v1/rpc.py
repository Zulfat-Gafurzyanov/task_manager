from fastapi import APIRouter

from src.broker.rpc_publisher import rpc_publisher

router = APIRouter(prefix="/rpc", tags=["rpc"])

EXAMPLE_QUEUE = "example_rpc_queue"


@router.post("/echo")
async def rpc_echo(payload: dict) -> dict:
    """Отправляет RPC-запрос в очередь и ждёт ответ от consumer'а."""
    import json

    response = await rpc_publisher.call(
        message=json.dumps(payload),
        request_queue_name=EXAMPLE_QUEUE,
    )
    return {"response": json.loads(response)}
