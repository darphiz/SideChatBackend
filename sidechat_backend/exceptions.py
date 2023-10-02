import logging
from contextlib import suppress
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger("application")

def error_handler(exc, context):
    exception_message = "Something went wrong."
    exception_code = 500
    with suppress(AttributeError):
        exception_message = exc.message
        exception_code = exc.code
    response = exception_handler(exc, context)
    if response is not None:
        return response
    logger.error(exception_message)
    return Response({
        "data": None,
        "error": exception_message
        }, status=exception_code)
