from clickhouse_connect import get_client
from settings import settings


def clickhouse_session():
    return get_client(host=settings.CLICKHOUSE_ADDR,
                      port=settings.CLICKHOUSE_PORT,
                      username=settings.CLICKHOUSE_USERNAME,
                      password=settings.CLICKHOUSE_PASSWORD)


def db_session():
    return get_client(host=settings.CLICKHOUSE_ADDR,
                      database=settings.CLICKHOUSE_DB_NAME,
                      port=settings.CLICKHOUSE_PORT,
                      username=settings.CLICKHOUSE_USERNAME,
                      password=settings.CLICKHOUSE_PASSWORD)
