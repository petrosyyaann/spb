from fastapi import APIRouter, Depends, UploadFile
from aio_pika import DeliveryMode, Message
from models.user import User
from core.db import get_database, Session
from core.auth import get_user
from uuid import uuid4
from core.s3 import s3_connection
from typing import List
import core.errors as errors
from core.rabbitmq import rabbit_connection
from schemas.rabbit import CSVs


router = APIRouter()


@router.post("",
             status_code=201,
             responses=errors.with_errors(errors.not_enough_data_for_processing()))
async def upload_workflow_data(files: List[UploadFile]):
    """Загрузка данных о результах выполнения спринтов"""
    if len(files) != 3:
        raise errors.not_enough_data_for_processing()
    upload_id = str(uuid4())
    s3_paths = []
    for file in files:
        s3_paths.append(f"import/{upload_id}/{file.filename}")
        s3_connection.upload_file(file.file.read(), s3_paths[-1])

    await rabbit_connection.exchange_new_csv.publish(
        Message(
            body=CSVs(id=upload_id, s3_paths=s3_paths).model_dump_json().encode(),
            content_type="application/json",
            content_encoding="utf-8",
            delivery_mode=DeliveryMode.PERSISTENT,
        ),
        "",
    )
