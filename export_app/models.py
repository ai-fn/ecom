import os
from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.conf import settings
from loguru import logger

from account.models import CustomUser, TimeBasedModel


def get_default_upload_to(instance: "ExportTask", filename):
    return settings.MEDIA_ROOT / "export_files" / filename


class ExportTaskStatus(models.TextChoices):
    PENDING = "PENDING", _("В ожидании"),
    IN_PROGRESS = "IN_PROGRESS", _("В процессе"),
    COMPLETED = "COMPLETED", _("Успешно завершён"),
    FAILED = "FAILED", _("Завершился с ошибкой"),


class ExportSettings(TimeBasedModel):
    name = models.CharField(_("Наименование"), max_length=256, unique=True, validators=[MinLengthValidator(3)])
    slug = models.SlugField(_("Слаг"), max_length=256, unique=True)
    fields = models.JSONField(_("Поля для экспорта"))

    class Meta:
        verbose_name = _("Настройки экспорта")
        verbose_name_plural = _("Настройки экспорта")


class ExportTask(TimeBasedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    export_status = models.CharField(_("Статус"), choices=ExportTaskStatus.choices, default=ExportTaskStatus.PENDING)
    ended_at = models.DateTimeField(_('Окончен'), blank=True, null=True)
    errors = models.TextField(_("Ошбики"), blank=True, null=True)
    result_file = models.FileField(_("Результат экспорта"), upload_to=get_default_upload_to, blank=True, null=True)
    settings = models.ForeignKey(ExportSettings, verbose_name=_("Настройки"), on_delete=models.SET_NULL, blank=True, null=True)

    def update_ended_at(self):
        now = timezone.localtime(timezone.now())
        self.ended_at = now
        self.save()

    def update_status(self, status: str):
        self.export_status = status
    
    def update_errors(self, errors: str):
        self.errors = errors
    
    def update_result_file(self, path: str):
        self.result_file = path

    class Meta:
        verbose_name = _("Задача экспорта")
        verbose_name_plural = _("Задачи экспорта")
    
    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        if self.result_file:
            file_path = self.result_file.path[1:] if self.result_file.path.startswith("/") else self.result_file.path
            path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    logger.info(f"File for ExportTask with id {self.id} removed by path: {path}")
                except Exception as e:
                    logger.error(f"Error while removing ExportTask file by path {self.result_file.path}")

        return super().delete(*args, **kwargs)
