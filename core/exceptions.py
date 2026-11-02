from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize API error responses across all endpoints.
    Provides consistent status_code, message, detail, and errors dictionary.
    """
    response = exception_handler(exc, context)

    if response is not None:
        raw_data = response.data
        detail_msg = "An error occurred."

        if isinstance(raw_data, dict):
            if "detail" in raw_data:
                detail_msg = str(raw_data["detail"])
            else:
                detail_msg = "Validation failed. Please verify your input."

            response.data = {
                "status_code": response.status_code,
                "message": detail_msg,
                "detail": detail_msg,
                "errors": raw_data,
            }
        elif isinstance(raw_data, list):
            first_err = str(raw_data[0]) if raw_data else "Error"
            response.data = {
                "status_code": response.status_code,
                "message": first_err,
                "detail": first_err,
                "errors": raw_data,
            }

    return response
