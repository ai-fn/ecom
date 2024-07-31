import os

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from account.models import TimeBasedModel, CustomUser
from shop.models import Setting


def get_default_file_upload_path(instance, filename):
    UPLOAD_PATH_SETTING, _ = Setting.objects.get_or_create(
        custom_key="upload_path", defaults={"value_string": "/var/import_files/"}
    )
    return os.path.join(UPLOAD_PATH_SETTING.value_string, filename)


def get_default_images_upload_path():
    DEFAULT_IMAGES_UPLOAD_PATH, _ = Setting.objects.get_or_create(
        custom_key="DEFAULT_IMAGES_UPLOAD_PATH",
        defaults={"value_string": "/var/import_images/"},
    )
    return DEFAULT_IMAGES_UPLOAD_PATH.value_string


class ImportTask(TimeBasedModel):

    STATUS_CHOICES = [
        ("PENDING", _("Pending")),
        ("IN_PROGRESS", _("In Progress")),
        ("COMPLETED", _("Completed")),
        ("FAILED", _("Failed")),
    ]

    file = models.FileField(_("Файл импорта"), upload_to=get_default_file_upload_path)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )
    status = models.CharField(
        _("Статус"), choices=STATUS_CHOICES, default="PENDING", max_length=20
    )
    end_at = models.DateTimeField(_("Окончен"), blank=True, null=True)
    comment = models.TextField(_("Комментарий"), max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name = _("Импорт")
        verbose_name_plural = _("Импорты")
    
    def update_status(self, status: str) -> "ImportTask":
        self.status = status
        self.save(update_fields=["status"])
        return self

    def update_end_at(self) -> "ImportTask":
        self.end_at = timezone.localtime(timezone.now())
        self.save()
        return self


class ImportSetting(TimeBasedModel):

    INACTICE_ITEMS_ACTION_CHOICES = [
        ("LEAVE", "оставить как есть"),
        ("ACTIVATE", "активировать"),
    ]

    ITEMS_NOT_IN_FILE_ACTION_CHOICES = [
        ("DEACTIVATE", "деактивировать"),
        ("DELETE", "удалить"),
        ("SET_NOT_IN_STOCK", 'установить статус "нет в наличии"'),
        ("IGNORE", "не трогать"),
    ]

    import_task = models.ForeignKey(
        ImportTask, on_delete=models.CASCADE, verbose_name=_("Импорт")
    )
    name = models.CharField(_("Наименование"), max_length=256, unique=True)
    slug = models.SlugField(_("Слаг"), max_length=512, unique=True)
    fields = models.JSONField(_("Соотношение полей"), unique=True)
    path_to_images = models.CharField(
        max_length=255, default=get_default_images_upload_path, blank=True, null=True
    )
    items_not_in_file_action = models.CharField(_("Объекты не в файле"),
        max_length=50, choices=ITEMS_NOT_IN_FILE_ACTION_CHOICES, default="IGNORE"
    )
    inactive_items_action = models.CharField(_("Неактивные объекты"),
        max_length=50, choices=INACTICE_ITEMS_ACTION_CHOICES, default="LEAVE"
    )
    remove_existing_price_if_empty = models.BooleanField(_("Удалить существующую цену, если она в файле указана пустой"), default=False)

    class Meta:
        verbose_name = _("Шаблон импорта")
        verbose_name_plural = _("Шаблоны импорта")
