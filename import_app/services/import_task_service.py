import os
import pandas as pd

from import_app.models import ImportTask

from decimal import Decimal, InvalidOperation

from django.db import transaction, models
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from loguru import logger


class ImportTaskService:

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
                field = model._meta.get_field(field_name)
            except Exception as e:
                logger.error(e)
                fields.pop(field_name)
                continue

        return unique_field_names

    def process_dataframe(self, df, import_settings=None):
        if import_settings is None:
            import_settings = {}

        path_to_images = import_settings.get("path_to_images", "/tmp/import_images/")
        mapping = import_settings.get("fields", {})

        for model_name, fields in mapping.items():
            model_type = ContentType.objects.filter(model=model_name).first()
            if model_type is None:
                logger.info(f"Model with name '{model_name}' not found.")
                continue

            model = model_type.model_class()
            foreign_key_fields, image_fields, decimal_fields, unique_fields = (
                self.categorize_fields(model, fields)
            )
            self.process_rows(
                df,
                model,
                fields,
                foreign_key_fields,
                image_fields,
                decimal_fields,
                unique_fields,
                path_to_images,
            )

    def categorize_fields(self, model: models.Model, fields: dict) -> tuple:
        foreign_key_fields = {}
        image_fields = {}
        decimal_fields = {}
        unique_fields = {}

        for field_name in list(fields.keys()):
            try:
                field = model._meta.get_field(field_name)
            except Exception as e:
                logger.error(
                    f"FieldError: '{model._meta.model_name.title()}' has no field named '{field_name}'"
                )
                fields.pop(field_name)
                continue

            if field.primary_key:
                unique_fields[field_name] = fields.pop(field_name)

            elif isinstance(field, models.AutoField) or getattr(
                field, "primary_key", None
            ):
                unique_fields[field.name] = fields.pop(field_name)
            elif getattr(field, "unique", None):
                unique_fields[field.name] = fields.pop(field_name)

            elif isinstance(field, models.ForeignKey):
                foreign_key_fields[field_name] = fields.pop(field_name)
            elif isinstance(field, models.ImageField):
                image_fields[field_name] = fields.pop(field_name)
            elif isinstance(field, models.DecimalField):
                decimal_fields[field_name] = fields.pop(field_name)

        return foreign_key_fields, image_fields, decimal_fields, unique_fields

    def process_rows(
        self,
        df: pd.DataFrame,
        model: models.Model,
        fields: dict,
        foreign_key_fields: dict,
        image_fields: dict,
        decimal_fields: dict,
        unique_fields: dict,
        path_to_images: str,
    ):
        no_unique_fields = len(unique_fields) < 1

        for _, row in df.iterrows():
            data = self.prepare_data(
                row,
                fields,
                image_fields,
                decimal_fields,
                foreign_key_fields,
                path_to_images,
            )
            try:
                with transaction.atomic():
                    if no_unique_fields:
                        model.objects.create(**data)
                    else:
                        self.update_or_create_instance(model, data, unique_fields)
            except Exception as e:
                logger.error(
                    f"Error while create or update '{model._meta.model_name.title()}': {str(e)}"
                )

    def prepare_data(
        self,
        row: dict,
        fields: dict,
        image_fields: dict,
        decimal_fields: dict,
        foreign_key_fields: dict,
        path_to_images: str,
    ):
        data = {}

        try:
            for field_name in image_fields:
                cell_name = image_fields[field_name]
                cell = row.get(cell_name)
                if not pd.notna(cell):
                    logger.info(f"Field '{cell_name}' is empty in file")
                    continue
                
                data[field_name] = os.path.join(
                    settings.BASE_DIR,
                    path_to_images,
                    str(cell),
                )

            for field_name in foreign_key_fields:
                cell_name = foreign_key_fields[field_name]
                cell = row.get(cell_name)
                if not pd.notna(cell):
                    logger.info(f"Field '{cell_name}' is empty in file")
                    continue

                data_field_name = (
                    f"{field_name}_id" if not field_name.endswith("_id") else field_name
                )
                data[data_field_name] = cell

            for field_name in decimal_fields:
                cell_name = decimal_fields.get(field_name)
                cell = row.get(cell_name)
                if not pd.notna(cell):
                    logger.info(f"Field '{cell_name}' is empty in file")
                    continue

                try:
                    data[field_name] = Decimal(str(cell))
                except (ValueError, InvalidOperation) as e:
                    logger.error(f"Error converting {cell} to Decimal: {e}")
                    data[field_name] = None

        except KeyError as key_error:
            logger.error(f"Got the KeyError: {str(key_error)}")

        for field_name in fields:
            data[field_name] = row[fields[field_name]]

        return data

    def update_or_create_instance(
        self, model: models.Model, data: dict, unique_fields: list
    ):
        try:
            unique_data = {column: data.pop(field, None) for field, column in unique_fields.items()}
            model.objects.update_or_create(**unique_data, defaults=data)
        except Exception as e:
            logger.error(
                f"Error while updating '{model._meta.model_name}' instance: {e}"
            )
