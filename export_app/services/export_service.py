from typing import Dict, List, Tuple
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist

from loguru import logger
import pandas as pd


class ExportService:

    @staticmethod
    def create_dataframe(model_fields: Dict[str, list]) -> pd.DataFrame:
        """
        Создает DataFrame из данных моделей Django.

        :param model_fields: Словарь, где ключи - имена моделей, а значения - списки полей для извлечения.
        :return: DataFrame, содержащий данные моделей.
        :raises ValueError: Если указанные модели не найдены.
        """
        cts = ContentType.objects.filter(
            model__in=model_fields.keys(), app_label__in=settings.IMPORT_EXPORT_APPS
        )

        not_found = set(model_fields.keys()).difference(
            cts.values_list("model", flat=True)
        )

        if len(not_found) > 0:
            raise ValueError(f"Invalid model names ({', '.join(not_found)})")

        data = dict()
        for ct in cts:
            model = ct.model_class()
            fields = set(model_fields.get(ct.model))

            reg_fields, m2m_fields = ExportService.prepare_data(model, fields)

            if len(m2m_fields) > 0:
                instances = model.objects.prefetch_related(*m2m_fields).all()
            else:
                instances = model.objects.all()

            for obj in instances:
                for field_name in reg_fields:
                    key = f"{ct.name}_{field_name}"
                    append_data = getattr(obj, field_name, None)
                    if (idx := getattr(append_data, "pk", None)):
                        append_data = str(idx)

                    data.setdefault(key, []).append(append_data)

                for field_name in m2m_fields:
                    key = f"{ct.name}_{field_name}"
                    append_data = ', '.join([str(x) for x in getattr(obj, field_name).values_list("pk", flat=True)])
                    data.setdefault(key, []).append(append_data)

        df = pd.DataFrame({k: pd.Series(v) for k, v in data.items()})
        return df

    @staticmethod
    def prepare_data(model: models.Model, field_names: List[str]) -> Tuple[List[str], List[str]]:
        """
        Разделяет список полей модели на обычные и m2m поля.

        :param model: Модель Django, для которой нужно разделить поля.
        :param field_names: Список имен полей модели.
        :return: Кортеж, содержащий два списка: обычные поля и m2m поля.
        """
        reg_fields, m2m_fields = [], []
        for field_name in field_names:
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist as e:
                logger.error(str(e))
                continue

            if type(field) in (models.ManyToManyField, models.ManyToOneRel, models.ManyToManyRel):
                m2m_fields.append(field_name)
            else:
                reg_fields.append(field_name)
        
        return reg_fields, m2m_fields
