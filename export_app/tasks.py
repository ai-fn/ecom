import os
import pandas as pd

from email.message import EmailMessage
from loguru import logger

from uuid import uuid4
from django.conf import settings as django_settings
from typing import Literal
from celery import shared_task

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
        return

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
    task.update_result_file(file_path.removeprefix(str(django_settings.MEDIA_ROOT) + "/"))
    task.update_ended_at()
    task.save()

    if email_to:
        send_email_with_attachment(email_to, file_path)

    logger.info(f"Export task ended, file saved to {file_path}")


def write_to_file(
    df: pd.DataFrame, file_type: Literal[".xlsx", ".csv"], export_type: str = None
) -> str:
    file_name = "export"
    directory = os.path.join(django_settings.MEDIA_ROOT, "export_files")

    if export_type is not None:
        file_name += f"_{export_type}"

    if os.path.isfile(os.path.join(directory, f"{file_name}{file_type}")):
        file_name += f"_{uuid4()}"

    file_name += file_type

    file_path = os.path.join(directory, file_name)

    if file_type == ".xlsx":
        write_func = df.to_excel
    else:
        write_func = df.to_csv

    if not os.path.exists(directory):
        os.makedirs(directory)

    write_func(file_path, index=False)

    return file_path


def send_email_with_attachment(email_to, file_path):
    subject = "Экспортированные продукты CSV"
    body = "Пожалуйста, найдите приложенный CSV-файл с экспортированными продуктами."
    email = EmailMessage(subject, body, django_settings.EMAIL_HOST_USER, [email_to])
    email.attach_file(file_path)
    result = email.send(fail_silently=True)
    logger.debug(f"CSV file of products was mailed with status: {result}")
