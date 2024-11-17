from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_ADDR: str = "db"
    DB_PORT: int = 5432

    RABBITMQ_HOST: str = 'localhost'
    RABBITMQ_USER: str = 'quest'
    RABBITMQ_PASS: str = 'quest'
    RABBITMQ_PORT: int = 5672

    AWS_HOST: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET: str
    AWS_REGION: str = 'us-east-1'


settings = Settings()
