from fastapi import APIRouter, Depends, UploadFile
from models.user import User
from core.db import get_database, Session
from core.auth import get_user
from uuid import uuid4
from core.s3 import s3_connection
from typing import List
import core.errors as errors


router = APIRouter()


@router.post("",
             status_code=201,
             responses=errors.with_errors(errors.not_enough_data_for_processing()))
async def upload_workflow_data(files: List[UploadFile]):
    """Загрузка данных о результах выполнения спринтов"""
    if len(files) != 3:
        raise errors.not_enough_data_for_processing()

    s3_paths = []
    for file in files:
        s3_connection.upload_file(file.file.read(), "attachments/" + file.filename)
        s3_paths.append(f"import/{uuid4()}_{file.filename}")

    # TODO send s3_paths to preprocessing
