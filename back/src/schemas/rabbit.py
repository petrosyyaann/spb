from pydantic import BaseModel


class CSVs(BaseModel):
    id: str
    s3_paths: list[str]
