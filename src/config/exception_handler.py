from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from src.apps.service.exceptions import OptimisticLockingError
from django.db import transaction, IntegrityError


def custom_exception_handler(exc, context):
    if isinstance(exc, OptimisticLockingError):
        return Response(
            status=status.HTTP_200_OK,
            data={
                "desm": "Conflict detected: The resource was modified by another user. Please refresh and try again."
            }
        )
    if isinstance(exc, IntegrityError):
        return Response(
            status=status.HTTP_200_OK,
            data={
                "desm": "bad request"
            }
        )


    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response
