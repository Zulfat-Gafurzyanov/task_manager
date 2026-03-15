import asyncio
import logging

from src.broker.rpc_consumer import rpc_consumer
from src.db.connection import init_db_pool, close_db_pool
from src.service.assigments import handle

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db_pool()
    try:
        await rpc_consumer.start_consuming(
            queue_name="task_assignment_queue",
            callback=handle,
        )
    finally:
        await close_db_pool()


if __name__ == "__main__":
    asyncio.run(main())
