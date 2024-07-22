from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import TimeBasedModel


class Lead(TimeBasedModel):
    bitrix_id = models.IntegerField(_("Идентификатор Bitrix24"), unique=True, blank=True, null=True)
    title = models.CharField(_("Название лида"), max_length=255)
    status = models.CharField(_("Статус лида"), max_length=50)
    dynamical_fields = models.JSONField(_("Дополнительная информация"), default=dict, blank=True, null=True)

    def __str__(self) -> str:
        return f"Lead '{self.title}': {self.status}"
    
    class Meta:
        verbose_name = _("Лид")
        verbose_name_plural = _("Лиды")