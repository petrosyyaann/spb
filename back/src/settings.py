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

    AWS_HOST: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET: str
    AWS_REGION: str = "us-east-1"

    JWT_SECRET: str
    JWT_ACCESS_EXPIRE: int
    JWT_REFRESH_EXPIRE: int
    JWT_REFRESH_LONG_EXPIRE: int

    MINIMAL_PASSWORD_LENGTH: int = 4

    RABBITMQ_HOST: str = 'localhost'
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_PORT: int = 5672

settings = Settings()
