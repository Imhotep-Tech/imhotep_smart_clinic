from django.conf import settings
from django.shortcuts import render
import logging

class CustomErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.request')

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception:
            # Log full stack trace to the terminal/console
            self.logger.exception('Unhandled exception at %s', request.get_full_path())
            # In DEBUG, re-raise so you still get the Django debug page
            if getattr(settings, 'DEBUG', False):
                raise
            # In production, show a friendly unified error page
            response = render(
                request,
                'error_handle.html',
                {'error_code': 500, 'error_description': 'Internal server error'},
                status=500,
            )
            # Ensure the response is an instance of HttpResponse
            return response
