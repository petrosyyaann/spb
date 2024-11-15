from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVER_ADDR: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_TEST: bool = True
    SERVER_WORKERS: int = 1

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_ADDR: str = "db"
    DB_PORT: int = 5432

    CLICKHOUSE_ADDR: str = "clickhouse"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USERNAME: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DB_NAME: str

    JWT_SECRET: str
    JWT_ACCESS_EXPIRE: int
    JWT_REFRESH_EXPIRE: int
    JWT_REFRESH_LONG_EXPIRE: int

    MINIMAL_PASSWORD_LENGTH: int = 4


settings = Settings()
