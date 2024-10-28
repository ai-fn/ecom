import os
import urllib
import urllib.request
import pandas as pd
from loguru import logger
from celery import shared_task

from tempfile import NamedTemporaryFile

from import_app.models import ImportTask
from import_app.services import ImportTaskService


@shared_task
def handle_file_task(import_task_data: dict, replace_existing_m2m_elems: bool = True):

    import_task_id = import_task_data.get("id")
    import_settings = import_task_data.get("import_setting")
    if not import_settings:
        logger.error("Could not start import task without settings")
        return

    import_task = ImportTask.objects.get(id=import_task_id)
    
    task_service = ImportTaskService(replace_existing_m2m_elems=replace_existing_m2m_elems)
    file_url = import_task.file.url

    try:
        with urllib.request.urlopen(file_url) as file_obj:
            
            _, format = os.path.splitext(import_task.file.name)

            if format == '.xlsx':
                suffix = ".xlsx"
                read_function = pd.read_excel
            elif format == '.csv':
                suffix = ".csv"
                read_function = pd.read_csv
            else:
                raise ValueError("Unsupported file format. Only .xlsx and .csv are supported.")

            with NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
                tmp.write(file_obj.read())
                tmp.flush()
                tmp.seek(0)
                df = read_function(tmp.name)
                
                import_task.update_status("IN_PROGRESS")
                import_task.save(update_fields=('status',))
                task_service.process_dataframe(df, import_settings)
                import_task.update_end_at()
                import_task.update_status("COMPLETED")
                if task_service.errors:
                    import_task.errors = "\n".join(task_service.errors)
                
                import_task.save()

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        task_service.errors.append(f"Ошибка обработки файла: {str(e)}")
        import_task.update_status("FAILED")
        import_task.update_errors(task_service.errors)
        import_task.save()
