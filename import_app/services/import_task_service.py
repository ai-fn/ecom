import os
import pandas as pd

from import_app.models import ImportTask

from decimal import Decimal, InvalidOperation

from django.db import transaction, models
from django.db import models
from django.contrib.contenttypes.models import ContentType
from mptt.fields import TreeForeignKey

from loguru import logger


class ImportTaskService:

    def __init__(self, replace_existing_m2m_elems=True) -> None:
        self.image_fields = {}
        self.decimal_fields = {}
        self.unique_fields = {}
        self.foreign_key_fields = {}
        self.m2m_fields = {}
        self.bool_fields = {}
        self.replace_existing_m2m_elems = replace_existing_m2m_elems

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

    def get_unique_field_names(self, model: models.Model, fields_dict: dict) -> dict:

        fields = fields_dict.copy()
        unique_field_names = {}
        field_names = list(fields.keys())

        for field_name in field_names:
            try:
                model._meta.get_field(field_name)
            except Exception as e:
                logger.error(e)
                fields.pop(field_name)

        return unique_field_names

    def process_dataframe(self, df, import_settings=None):
        if import_settings is None:
            import_settings = {}

        self.path_to_images = import_settings.get("path_to_images", "/tmp/import_images/")
        mapping = import_settings.get("fields", {})

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

    def categorize_fields(self, model: models.Model, fields: dict) -> tuple:

        for field_name in list(fields.keys()):
            try:
                field = model._meta.get_field(field_name)
            except Exception as e:
                logger.error(
                    f"FieldError: '{model._meta.model_name.title()}' has no field named '{field_name}'"
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
                        if m2m_data:
                            self._set_m2m_data(instance, m2m_data)
                    else:
                        unique_data = self.get_notna_items(self.unique_fields, row)
                        self.update_instance(model, data, unique_data, m2m_data)
            except Exception as e:
                logger.error(
                    f"Error while create or update '{model._meta.model_name.title()}': {str(e)}"
                )

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

        for field_name, cell in self.get_notna_items(self.foreign_key_fields, row).items():

            data_field_name = (
                f"{field_name}_id" if not field_name.endswith("_id") else field_name
            )
            data[data_field_name] = cell

        for field_name, cell in self.get_notna_items(self.decimal_fields, row).items():

            try:
                data[field_name] = Decimal(str(cell))
            except (ValueError, InvalidOperation) as e:
                logger.error(f"Error converting {cell} to Decimal: {e}")
                data[field_name] = None

        for field_name, cell in self.get_notna_items(self.bool_fields, row).items():
            data[field_name] = str(cell).lower() == "true"

        try:
            for field_name, value in (*fields.items(), *self.unique_fields.items()):
                data[field_name] = row[value]

        except KeyError as key_error:
            logger.error(f"Got the KeyError: {str(key_error)}")

        return data

    def update_instance(
        self, model: models.Model, data: dict, unique_data: dict, m2m_data: dict
    ):
        try:
            unique_data = {field: data.pop(field, None) for field in unique_data.keys()}
            m2m_data = {field: data.pop(field, None) for field in m2m_data.keys()}

            instance = model.objects.get(**unique_data)
            for field_name, value in data.items():
                setattr(instance, field_name, value)
            instance.save()

            if m2m_data:
                self._set_m2m_data(instance, m2m_data)
        except Exception as e:
            logger.error(
                f"Error while updating '{model._meta.model_name}' instance: {e}"
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
                values = [int(x.strip()) for x in value.split(",")]
                func(values)
            except Exception as e:
                logger.error(
                    f"Error while {func_name} m2m values for field {field_name}: {str(e)}"
                )

        return instance
