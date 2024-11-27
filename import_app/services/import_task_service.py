import os
import pandas as pd
from typing import Dict, Optional

from import_app.models import ImportTask, ImportSetting

from decimal import Decimal, InvalidOperation
from django.db import models, transaction
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import CommandError
from mptt.fields import TreeForeignKey
from loguru import logger


class ImportTaskService:
    """
    Сервис для обработки задач импорта, разбора данных из файлов и обновления базы данных
    на основе импортированных данных.
    """

    def __init__(self, replace_existing_m2m_elems: bool = True) -> None:
        """
        Инициализация сервиса задач импорта.

        :param replace_existing_m2m_elems: Указывает, заменять ли существующие связи "многие ко многим" 
                                           или добавлять к ним.
        """
        self.m2m_fields = {}
        self.image_fields = {}
        self.unique_fields = {}
        self.decimal_fields = {}
        self.foreign_key_fields = {}
        self.bool_fields = {}

        self.ids = []
        self.errors = []
        self.inactive_items_action = "LEAVE"
        self.items_not_in_file_action = "IGNORE"
        self.replace_existing_m2m_elems = replace_existing_m2m_elems

        self.invalid_value_error_text_en = (
            "Invalid value for '{field_name}', provided '{provided_value}', but expected one of '{choices}'"
        )
        self.invalid_value_error_text_ru = (
            "Неверно значение для '{field_name}', передано '{provided_value}', но ожидалось одно из '{choices}'"
        )

    @staticmethod
    def get_columns(task: ImportTask) -> list:
        """
        Получает названия столбцов из файла задачи импорта.

        :param task: Экземпляр задачи импорта.
        :raises ValueError: Если файл отсутствует или имеет неподдерживаемый формат.
        :return: Список названий столбцов.
        """
        if not task.file:
            raise ValueError(f"Задача импорта с id '{task.id}' не содержит файла.")

        _, format = os.path.splitext(task.file.name)
        if format in (".xlsx", ".xls"):
            read_func = pd.read_excel
        elif format == ".csv":
            read_func = pd.read_csv
        else:
            raise ValueError(
                f"Файл задачи импорта с id '{task.id}' имеет неподдерживаемый формат."
            )

        file = read_func(task.file.path)
        return file.columns.to_list()

    def process_dataframe(self, df: pd.DataFrame, import_settings: dict) -> None:
        """
        Обрабатывает DataFrame на основе настроек импорта.

        :param df: DataFrame с данными для импорта.
        :param import_settings: Настройки импорта.
        """
        self.path_to_images = import_settings.get("path_to_images", "import_images/")
        mapping = import_settings.get("fields", {})

        if (
            ITEMS_NOT_IN_FILE_ACTION := import_settings.get("items_not_in_file_action")
        ) is not None:
            self.items_not_in_file_action = ITEMS_NOT_IN_FILE_ACTION

        if (
            INACTIVE_ITEMS_ACTION := import_settings.get("inactive_items_action")
        ) is not None:
            self.inactive_items_action = INACTIVE_ITEMS_ACTION

        for model_name, fields in mapping.items():
            model_type = ContentType.objects.filter(model=model_name).first()
            if model_type is None:
                logger.info(f"Модель с именем '{model_name}' не найдена.")
                continue

            model = model_type.model_class()
            self.categorize_fields(model, fields)
            self.process_rows(
                df,
                model,
                fields,
            )
        
        # Обновление дерева категорий
        if "category" in import_settings["fields"]:
            from shop.models import Category
            Category.objects.rebuild()

        # Обновление Elasticsearch-индексов
        try:
            call_command('update_index')
            logger.info('Elasticsearch-индексы успешно обновлены.')
        except CommandError as e:
            logger.info(str(e))
        except Exception as e:
            logger.error(str(e.with_traceback(e.__traceback__)))

    def categorize_fields(self, model: models.Model, fields: dict) -> None:
        """
        Классифицирует поля модели (M2M, FK, уникальные и т.д.).

        :param model: Модель Django.
        :param fields: Словарь с именами полей.
        """
        for field_name in list(fields.keys()):
            try:
                field = model._meta.get_field(field_name)
            except Exception as e:
                logger.error(
                    f"Ошибка поля: у модели '{model._meta.model_name}' отсутствует поле '{field_name}'."
                )
                self.errors.append(
                    f"У модели {model._meta.model_name} нет поля '{field_name}'."
                )
                fields.pop(field_name)
                continue

            if getattr(field, "primary_key", None):
                self.unique_fields[field_name] = fields.pop(field_name)

            elif isinstance(field, models.ManyToManyField):
                self.m2m_fields[field_name] = fields.pop(field_name)

            elif isinstance(field, models.ForeignKey) or isinstance(
                field, TreeForeignKey
            ):
                self.foreign_key_fields[field_name] = fields.pop(field_name)

            elif isinstance(field, models.ImageField):
                self.image_fields[field_name] = fields.pop(field_name)

            elif isinstance(field, models.DecimalField):
                self.decimal_fields[field_name] = fields.pop(field_name)

            elif isinstance(field, models.BooleanField):
                self.bool_fields[field_name] = fields.pop(field_name)
    def process_rows(
        self,
        df: pd.DataFrame,
        model: models.Model,
        fields: dict,
    ) -> None:
        """
        Обрабатывает строки DataFrame, создавая или обновляя объекты модели.

        :param df: DataFrame с данными для обработки.
        :param model: Модель Django, в которую выполняется импорт данных.
        :param fields: Словарь полей для обработки.
        """
        no_unique_fields = len(self.unique_fields) < 1

        for _, row in df.iterrows():
            data = self.prepare_data(row, fields)
            try:
                with transaction.atomic():
                    m2m_data = self.get_notna_items(self.m2m_fields, row)
                    if no_unique_fields:
                        # Создание новой записи
                        instance = model.objects.create(**data)
                        self.ids.append(instance.pk)

                        if m2m_data:
                            self._set_m2m_data(instance, m2m_data)
                    else:
                        # Обновление существующей записи
                        unique_data = self.get_notna_items(self.unique_fields, row)
                        self.update_instance(model, data, unique_data, m2m_data)
            except Exception as e:
                logger.error(
                    f"Ошибка при создании или обновлении '{model._meta.model_name}': {str(e)}"
                )
                self.errors.append(
                    f"Ошибка создания или обновления '{model._meta.model_name}': {str(e)}"
                )
                continue

        # Дополнительная обработка для элементов, не включенных в файл
        self.process_items_not_in_file_action(model)
        self.process_inactive_items_action(model)

    def prepare_data(
        self,
        row: pd.Series,
        fields: dict,
    ) -> dict:
        """
        Подготавливает данные для создания или обновления объектов модели.

        :param row: Строка данных из DataFrame.
        :param fields: Словарь полей для обработки.
        :return: Подготовленный словарь данных.
        """
        data = {}

        # Обработка полей изображений
        for field_name, cell in self.get_notna_items(self.image_fields, row).items():
            data[field_name] = os.path.join(self.path_to_images, str(cell))

        # Обработка внешних ключей
        for field_name, cell in self.get_notna_items(self.foreign_key_fields, row).items():
            data_field_name = f"{field_name}_id" if not field_name.endswith("_id") else field_name
            data[data_field_name] = cell

        # Обработка десятичных полей
        for field_name, cell in self.get_notna_items(self.decimal_fields, row).items():
            try:
                data[field_name] = Decimal(str(cell))
            except (ValueError, InvalidOperation) as e:
                logger.error(f"Ошибка преобразования {cell} в Decimal: {str(e)}")
                self.errors.append(
                    f"Ошибка преобразования {cell} (для поля {field_name}) в Decimal: {str(e)}"
                )
                data[field_name] = None

        # Обработка логических полей
        for field_name, cell in self.get_notna_items(self.bool_fields, row).items():
            data[field_name] = str(cell).lower() == "true"

        # Обработка остальных полей
        for field_name, cell in self.get_notna_items(fields, row).items():
            data[field_name] = cell

        # Обработка уникальных полей
        try:
            for field_name, value in self.unique_fields.items():
                data[field_name] = row[value]
        except KeyError as key_error:
            logger.error(f"Ошибка ключа: {str(key_error)}")
            self.errors.append(f"Ошибка обращения по ключу: {str(key_error)}")

        return data

    def update_instance(
        self, model: models.Model, data: dict, unique_data: dict, m2m_data: dict
    ) -> None:
        """
        Обновляет существующий объект модели.

        :param model: Модель Django.
        :param data: Данные для обновления.
        :param unique_data: Уникальные поля объекта для идентификации.
        :param m2m_data: M2M данные для обновления.
        """
        try:
            unique_data = {field: data.pop(field, None) for field in unique_data.keys()}
            m2m_data = {field: data.pop(field, None) for field in m2m_data.keys()}

            instance = model.objects.get(**unique_data)
            self.ids.append(instance.pk)

            for field_name, value in data.items():
                setattr(instance, field_name, value)
            instance.save()

            if m2m_data:
                self._set_m2m_data(instance, m2m_data)
        except Exception as e:
            logger.error(
                f"Ошибка обновления объекта '{model._meta.model_name}': {str(e)}"
            )
            self.errors.append(
                f"Ошибка обновления объекта '{model._meta.model_name}': {str(e)}"
            )

    def get_notna_items(self, fields: dict, row: pd.Series) -> dict:
        """
        Фильтрует ненулевые значения из строки DataFrame для указанных полей.

        :param fields: Словарь полей для проверки.
        :param row: Строка данных из DataFrame.
        :return: Словарь с ненулевыми значениями.
        """
        result = {}
        for field_name in fields:
            col_name = fields[field_name]
            cell = row.get(col_name)
            if not pd.notna(cell):
                logger.info(f"Поле '{col_name}' пустое в файле")
                continue

            result[field_name] = cell

        return result

    def _set_m2m_data(self, instance, m2m_data: dict) -> None:
        """
        Устанавливает данные для полей "многие ко многим".

        :param instance: Экземпляр модели.
        :param m2m_data: Данные M2M для установки.
        """
        func_name = ("add", "set")[self.replace_existing_m2m_elems]

        for field_name, value in m2m_data.items():
            try:
                m2m_field = getattr(instance, field_name)
                func = getattr(m2m_field, func_name)
                values = [int(x.strip()) for x in str(value).split(",")]
                func(values)
            except Exception as e:
                logger.error(
                    f"Ошибка при {func_name} значений для M2M поля {field_name}: {str(e)}"
                )
                self.errors.append(
                    f"Ошибка при записи M2M значений для поля {field_name}: {str(e)}"
                )
    def process_inactive_items_action(self, model: models.Model) -> None:
        """
        Обрабатывает элементы модели, которые помечены как неактивные.

        Действия зависят от настроек: активация, игнорирование или другая обработка.

        :param model: Модель Django, для которой выполняется обработка.
        """
        if self.inactive_items_action == "LEAVE":
            # Оставляем элементы без изменений
            pass

        elif self.inactive_items_action == "ACTIVATE":
            # Активируем все неактивные элементы
            model.objects.filter(is_active=False).update(is_active=True)

        else:
            # Если значение настройки некорректно, записываем ошибку
            format_kwargs = {
                "field_name": "inactive_items_action",
                "provided_value": self.inactive_items_action,
                "choices": ImportSetting.INACTIVE_ITEMS_ACTION_CHOICES,
            }
            logger.error(self.invalid_value_error_text_en.format(**format_kwargs))
            self.errors.append(self.invalid_value_error_text_ru.format(**format_kwargs))

    def process_items_not_in_file_action(self, model: models.Model) -> None:
        """
        Обрабатывает элементы модели, которые отсутствуют в файле.

        Действия зависят от настроек: деактивация, удаление или установка статуса "нет в наличии".

        :param model: Модель Django, для которой выполняется обработка.
        """
        queryset = model.objects.exclude(id__in=self.ids)

        if self.items_not_in_file_action == "DEACTIVATE":
            # Деактивируем элементы, отсутствующие в файле
            queryset.update(is_active=False)

        elif self.items_not_in_file_action == "DELETE":
            # Удаляем элементы, отсутствующие в файле
            queryset.delete()

        elif self.items_not_in_file_action == "SET_NOT_IN_STOCK":
            # Устанавливаем статус "нет в наличии" для элементов, отсутствующих в файле
            if not hasattr(model, "in_stock"):
                logger.info(f"У модели '{model.__name__}' отсутствует атрибут 'in_stock', обработка пропущена.")
            else:
                queryset.update(in_stock=False)

        elif self.items_not_in_file_action == "IGNORE":
            # Игнорируем элементы
            pass

        else:
            # Если значение настройки некорректно, записываем ошибку
            format_kwargs = {
                "field_name": "items_not_in_file_action",
                "provided_value": self.items_not_in_file_action,
                "choices": ImportSetting.ITEMS_NOT_IN_FILE_ACTION_CHOICES,
            }
            logger.error(self.invalid_value_error_text_en.format(**format_kwargs))
            self.errors.append(self.invalid_value_error_text_ru.format(**format_kwargs))
