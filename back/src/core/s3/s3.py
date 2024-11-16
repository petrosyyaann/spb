import boto3
import botocore
import mimetypes
import logging
import botocore.exceptions
from io import BytesIO

from settings import settings


class S3:
    def __init__(self):
        self.session = boto3.session.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                             region_name=settings.AWS_REGION)
        self.s3client = self.session.client(service_name='s3', endpoint_url=settings.AWS_HOST)
        self.create_bucket(settings.AWS_BUCKET)

    def has_file(self, fileid: str):
        try:
            self.s3client.head_object(Bucket=settings.AWS_BUCKET, Key=fileid)
            return True
        except botocore.exceptions.ClientError:
            return False

    def upload_file(self, file, fileid: str):
        with BytesIO(file) as f:
            self.s3client.upload_fileobj(f, settings.AWS_BUCKET, fileid)

    def download_file(self, file, fileid: str):
        try:
            self.s3client.head_object(Bucket=settings.AWS_BUCKET, Key=fileid)
            self.s3client.download_fileobj(settings.AWS_BUCKET, fileid, file)
            file.seek(0)
        except botocore.exceptions.ClientError:
            raise FileNotFoundError("File not found")

    def delete_file(self, fileid: str):
        self.s3client.delete_object(Bucket=settings.AWS_BUCKET, Key=fileid)

    def create_bucket(self, name):
        try:
            try:
                self.s3client.head_bucket(Bucket=name)
                return
            except botocore.exceptions.ClientError:
                pass
            self.s3client.create_bucket(Bucket=name)
        except botocore.exceptions.ClientError as e:
            raise e
        except Exception as ex:
            logging.info(ex)

    def generate_link(self, bucket, key):
        return self.s3client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600
        )

    def get_url(self, fileid: str):
        try:
            self.s3client.head_object(Bucket=settings.AWS_BUCKET, Key=fileid)

            (mime, encoding) = mimetypes.guess_type(fileid, strict=True)
            if not mime:
                return self.s3client.generate_presigned_url("get_object", ExpiresIn=600,
                                                            Params={"Bucket": settings.AWS_BUCKET, "Key": fileid})
            else:
                return self.s3client.generate_presigned_url("get_object", ExpiresIn=600,
                                                            Params={"Bucket": settings.AWS_BUCKET, "Key": fileid,
                                                                    "ResponseContentType": mime})
        except botocore.exceptions.ClientError:
            raise FileNotFoundError("File not found")


s3_connection = S3()
