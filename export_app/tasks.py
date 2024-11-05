import os
import pandas as pd

from io import BytesIO
from uuid import uuid4
from loguru import logger
from typing import Literal
from celery import shared_task

from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.conf import settings as django_settings
from django.core.files.storage import default_storage

from export_app.services import ExportService
from export_app.models import ExportTask, ExportTaskStatus


@shared_task
def export(
    task_data: dict, file_type: Literal[".xlsx", ".csv"] = ".xlsx", email_to: str = None
):
    task = ExportTask.objects.get(id=task_data.get("id"))
    settings: dict = task_data.get("settings")
    if not settings:
        task.update_errors("Невозможно выполнить экспорт без настроек")
        task.update_ended_at()
        task.update_status(ExportTaskStatus.FAILED)
        task.save()
        return

    fields: dict = settings.get("fields")

    try:
        task.update_status(ExportTaskStatus.IN_PROGRESS)
        df = ExportService.create_dataframe(fields)
    except Exception as e:
        task.update_status(ExportTaskStatus.FAILED)
        task.update_errors(str(e))
        task.save()
        raise

    try:
        file_path = write_to_file(df, file_type)
    except Exception as e:
        logger.error(f"Error while save export data into file: {str(e)}")
        task.update_errors(str(e))
        task.update_status(ExportTaskStatus.FAILED)
        task.update_ended_at()
        task.save()
        return

    task.update_status(ExportTaskStatus.COMPLETED)
    task.update_result_file(file_path)

    task.update_ended_at()
    task.save()

    if email_to:
        send_email_with_attachment(email_to, file_path)

    logger.info(f"Export task ended, file saved to {file_path}")


def write_to_file(df: pd.DataFrame, file_type: Literal[".xlsx", ".csv"]) -> str:
    buffer = BytesIO()
    directory = "export_files"
    file_name = f"export_{uuid4()}{file_type}"

    file_path = os.path.join(directory, file_name)

    write_func =  df.to_excel if file_type == ".xlsx" else df.to_csv
    write_func(buffer, index=False)
    buffer.seek(0)

    default_storage.save(name=file_path, content=ContentFile(buffer.read()))
    buffer.close()

    return file_path


def send_email_with_attachment(email_to, file_path):
    subject = "Экспорт объектов"
    email = EmailMessage(
        subject=subject,
        from_email=django_settings.EMAIL_HOST_USER,
        to=[email_to],
    )
    email.attach_file(file_path)
    result = email.send(fail_silently=True)
    logger.debug(f"CSV file of products was mailed with status: {result}")
