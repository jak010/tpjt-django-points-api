from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from src.apps.service.exceptions import OptimisticLockingError


def custom_exception_handler(exc, context):
    if isinstance(exc, OptimisticLockingError):
        return Response(
            status=status.HTTP_409_CONFLICT,
            data={
                "desm": "Conflict detected: The resource was modified by another user. Please refresh and try again."
            }
        )

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response
