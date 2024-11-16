import uvicorn
from contextlib import asynccontextmanager
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI
from settings import settings
from routers import router
from core.db import create_tables as create_postgres_tables
from core.clickhouse import create_tables as create_clickhouse_tables
from core.rabbitmq import rabbit_connection
import logging

@asynccontextmanager
async def lifespan(application: FastAPI):
    create_clickhouse_tables()
    create_postgres_tables()
    await rabbit_connection.connect()
    yield
    await rabbit_connection.close()

app = FastAPI(debug=settings.SERVER_TEST,
              lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    GZipMiddleware,
    minimum_size=2000
)


if __name__ == "__main__":
    if not settings.SERVER_TEST:
        uvicorn.run(
            app,
            host=settings.SERVER_ADDR,
            port=settings.SERVER_PORT,
            log_level="info",
        )
    else:
        uvicorn.run(
            app,
            host=settings.SERVER_ADDR,
            workers=settings.SERVER_WORKERS,
            port=settings.SERVER_PORT,
            reload=True,
            log_level="debug",
        )
