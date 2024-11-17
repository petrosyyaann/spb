from settings import settings
import polars as pl
from datetime import datetime


storage_options = {
    "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
    "aws_secret_access_key":settings.AWS_SECRET_ACCESS_KEY,
    "endpoint_url": settings.AWS_HOST
}

def get_lf(s3_path: str):
    return pl.scan_csv(f"s3://{settings.AWS_BUCKET}/{s3_path}", separator=";", storage_options=storage_options)