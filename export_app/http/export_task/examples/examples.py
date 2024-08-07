from export_app.http.export_task_settings.examples import (
    example_export_settings_successful_response,
)

id = 1
user = 1
result_file = "/files/export1.xlsx"
export_status_completed = "COMPLETED"
export_status_pending = "PENGING"

ended_at = "2024-08-06T12:00:00Z"
errors = None
error = "Invalid file type: expected (.xlsx, .csv), got (.pdf)"

example_model_fields = [
    "id",
    "title",
    "created_at",
    "updated_at",
]

example_model_names_response = {
    "result": [
        "product",
        "category",
        "brand",
        "characteristic",
        "characteristicvalue",
    ]
}

examle_model_fields_response = {
    "result": example_model_fields,
}

example_get_all_response = {
    "result": {
        "product": example_model_fields,
    }
}

example_create_request = {
    "settings": example_export_settings_successful_response,
    "user": user,
}

example_partial_update_request = {
    "settings": example_export_settings_successful_response,
}

example_successful_response_completed = {
    "id": id,
    "settings": example_export_settings_successful_response,
    "result_file": result_file,
    "user": user,
    "export_status": export_status_completed,
    "ended_at": ended_at,
    "errors": errors,
}

example_successful_response_pending = {
    **example_successful_response_completed,
    "export_status": export_status_pending,
    "result_file": None,
    "ended_at": None,
}

example_invalid_file_type_response = {"error": error}

example_start_task_export_response = {
    "detail": f"Export task started with settings {example_export_settings_successful_response}"
}
