import os
import pandas as pd

from import_app.models import ImportTask, ImportSetting

from decimal import Decimal, InvalidOperation

from django.db import models
from django.db import transaction, models
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType

from django.core.management.base import CommandError

from mptt.fields import TreeForeignKey

from loguru import logger


class ImportTaskService:

    def __init__(
        self,
        replace_existing_m2m_elems=True,
    ) -> None:
        self.m2m_fields = dict()
        self.image_fields = dict()
        self.unique_fields = dict()
        self.decimal_fields = dict()
        self.foreign_key_fields = dict()

        self.ids = list()
        self.errors = list()
        self.bool_fields = dict()

        self.inactive_items_action = "LEAVE"
        self.items_not_in_file_action = "IGNORE"

        self.replace_existing_m2m_elems = replace_existing_m2m_elems

        self.invalid_value_error_text_en = "Invalid value for '{field_name}', provided '{provided_value}', but expected one of '{choices}'"
        self.invalid_value_error_text_ru = "Неверно значение для '{field_name}', передано '{provided_value}', но ожидалось одно из '{choices}'"

    @staticmethod
    def get_columns(task: ImportTask):

        if not task.file:
            raise ValueError(f"ImportTask instance with id '{task.id}' has no file.")

        _, format = os.path.splitext(task.file.name)
        if format in (".xlsx", ".xls"):
            read_func = pd.read_excel
        elif format == ".csv":
            read_func = pd.read_csv
        else:
            raise ValueError(
                f"ImportTask instance with id '{task.id}' has file with not allowed format."
            )

        file = read_func(task.file.path)

        return file.columns.to_list()

    def process_dataframe(self, df, import_settings: dict):

        self.path_to_images = import_settings.get(
            "path_to_images", "import_images/"
        )
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
                logger.info(f"Model with name '{model_name}' not found.")
                continue

            model = model_type.model_class()
            self.categorize_fields(model, fields)
            self.process_rows(
                df,
                model,
                fields,
            )
        
        # update category tree
        if "category" in import_settings["fields"]:
            from shop.models import Category
            Category.objects.rebuild()

        # update es indexes
        try:
            call_command('update_index')
            logger.info('Successfully updated Elasticsearch indexes')
        except CommandError as e:
            logger.info(str(e))
        except Exception as e:
            logger.error(str(e.with_traceback(e.__traceback__)))


    def categorize_fields(self, model: models.Model, fields: dict) -> tuple:

        for field_name in list(fields.keys()):
            try:
                field = model._meta.get_field(field_name)
            except Exception as e:
                logger.error(
                    f"FieldError: '{model._meta.model_name.title()}' has no field named '{field_name}'"
                )
                self.errors.append(
                    f"У модели {model._meta.model_name.title()} нет поля под названием '{field_name}'"
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
    ):
        no_unique_fields = len(self.unique_fields) < 1

        for _, row in df.iterrows():
            data = self.prepare_data(
                row,
                fields,
            )
            try:
                with transaction.atomic():
                    m2m_data = self.get_notna_items(self.m2m_fields, row)
                    if no_unique_fields:

                        instance = model.objects.create(**data)
                        self.ids.append(instance.pk)

                        if m2m_data:
                            self._set_m2m_data(instance, m2m_data)
                    else:
                        unique_data = self.get_notna_items(self.unique_fields, row)
                        self.update_instance(model, data, unique_data, m2m_data)

            except Exception as e:
                logger.error(
                    f"Error while create or update '{model._meta.model_name.title()}': {str(e)}"
                )
                self.errors.append(
                    f"Ошибка при создании или обновлении '{model._meta.model_name.title()}': {str(e)}"
                )
                continue

        self.process_items_not_in_file_action(model)
        self.process_inactive_items_action(model)


    def prepare_data(
        self,
        row: dict,
        fields: dict,
    ):
        data = {}

        for field_name, cell in self.get_notna_items(self.image_fields, row).items():

            data[field_name] = os.path.join(
                self.path_to_images,
                str(cell),
            )

        for field_name, cell in self.get_notna_items(
            self.foreign_key_fields, row
        ).items():

            data_field_name = (
                f"{field_name}_id" if not field_name.endswith("_id") else field_name
            )
            data[data_field_name] = cell

        for field_name, cell in self.get_notna_items(self.decimal_fields, row).items():

            try:
                data[field_name] = Decimal(str(cell))
            except (ValueError, InvalidOperation) as e:
                logger.error(f"Error converting {cell} to Decimal: {str(e)}")
                self.errors.append(
                    f"Ошибка преобразования {cell}(для поля {field_name}) в Decimal: {str(e)}"
                )
                data[field_name] = None

        for field_name, cell in self.get_notna_items(self.bool_fields, row).items():
            data[field_name] = str(cell).lower() == "true"

        for field_name, cell in self.get_notna_items(fields, row).items():
            data[field_name] = cell

        try:
            for field_name, value in self.unique_fields.items():
                data[field_name] = row[value]

        except KeyError as key_error:
            logger.error(f"Got the KeyError: {str(key_error)}")
            self.errors.append(f"Ошибка обращения по ключу: {str(key_error)}")

        return data

    def update_instance(
        self, model: models.Model, data: dict, unique_data: dict, m2m_data: dict
    ):
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
                f"Error while updating '{model._meta.model_name}' instance: {str(e)}"
            )
            self.errors.append(
                f"Ошбика обновления объекта '{model._meta.model_name}': {str(e)}"
            )

    def get_notna_items(self, fields: dict, row: dict) -> dict:
        result = {}
        for field_name in fields:
            col_name = fields[field_name]
            cell = row.get(col_name)
            if not pd.notna(cell):
                logger.info(f"Field '{col_name}' is empty in file")
                continue

            result[field_name] = cell

        return result

    def _set_m2m_data(self, instance, m2m_data: dict = None):
        func_name = ("add", "set")[self.replace_existing_m2m_elems]

        for field_name, value in m2m_data.items():
            try:
                m2m_field = getattr(instance, field_name)
                func = getattr(m2m_field, func_name)
                values = [int(x.strip()) for x in str(value).split(",")]
                func(values)
            except Exception as e:
                logger.error(
                    f"Error while {func_name} m2m values for field {field_name}: {str(e)}"
                )
                self.errors.append(
                    f"Ошибка при записи значений связи 'многие-ко-многим' для поля {field_name}: {str(e)}"
                )

        return instance

    def process_inactive_items_action(self, model: models.Model):
        if self.inactive_items_action == "LEAVE":
            pass

        elif self.inactive_items_action == "ACTIVATE":
            model.objects.filter(is_active=False).update(is_active=True)

        else:
            format_kwargs = {
                "field_name": "inactive_items_action",
                "provided_value": self.inactive_items_action,
                "choices": ImportSetting.INACTIVE_ITEMS_ACTION_CHOICES,
            }
            logger.error(self.invalid_value_error_text_en.format(**format_kwargs))
            self.errors.append(self.invalid_value_error_text_ru.format(**format_kwargs))

    def process_items_not_in_file_action(self, model: models.Model):
        queryset = model.objects.exclude(id__in=self.ids)

        if self.items_not_in_file_action == "DEACTIVATE":
            queryset.update(is_active=False)

        elif self.items_not_in_file_action == "DELETE":
            queryset.delete()

        elif self.items_not_in_file_action == "SET_NOT_IN_STOCK":
            if not hasattr(model, "in_stock"):
                logger.info(f"'{model.__name__}' has no attribute 'in_stock', ignore")
            else:
                queryset.update(in_stock=False)

        elif self.items_not_in_file_action == "IGNORE":
            pass

        else:
            format_kwargs = {
                "field_name": "items_not_in_file_action",
                "provided_value": self.items_not_in_file_action,
                "choices": ImportSetting.ITEMS_NOT_IN_FILE_ACTION_CHOICES,
            }
            logger.error(self.invalid_value_error_text_en.format(**format_kwargs))
            self.errors.append(self.invalid_value_error_text_ru.format(**format_kwargs))
