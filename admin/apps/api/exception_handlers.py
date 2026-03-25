from rest_framework.views import exception_handler
from .exceptions import AppBaseException

def custom_exception_handler(exc, context):
    """
    Global exception handler for DRF.
    Intercepts standard DRF and custom AppBaseExceptions to return a unified JSON envelope.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, AppBaseException):
            response.data = {
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        else:
            status_code = response.status_code
            error_code = 'VALIDATION_FAILED' if status_code == 400 else 'API_ERROR'
            
            if status_code == 401:
                error_code = 'AUTHENTICATION_FAILED'
            elif status_code == 403:
                error_code = 'PERMISSION_DENIED'
            elif status_code == 404:
                error_code = 'RESOURCE_NOT_FOUND'

            message = "An error occurred."
            details = None
            
            if isinstance(response.data, dict):
                if 'detail' in response.data:
                    message = str(response.data.pop('detail'))
                    if response.data:
                        details = response.data
                else:
                    if status_code == 400:
                        message = "Invalid input data provided."
                    details = response.data
            elif isinstance(response.data, list):
                if status_code == 400:
                    message = "Invalid input data provided."
                details = response.data
            else:
                message = str(response.data)

            response.data = {
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": details
                }
            }
    
    return response
