from django.shortcuts import render
import logging

logger = logging.getLogger('django.request')


def custom_bad_request(request, exception, template_name='error.html'):
    logger.warning('400 Bad Request: %s', request.get_full_path())
    ctx = {'error_code': 400, 'error_description': 'Bad request'}
    return render(request, 'error_handle.html', ctx, status=400)


def custom_permission_denied(request, exception, template_name='error.html'):
    logger.warning('403 Forbidden: %s', request.get_full_path())
    ctx = {'error_code': 403, 'error_description': 'Permission denied'}
    return render(request, 'error_handle.html', ctx, status=403)


def custom_page_not_found(request, exception, template_name='error.html'):
    logger.warning('404 Not Found: %s (referer=%s)', request.get_full_path(), request.META.get('HTTP_REFERER'))
    ctx = {'error_code': 404, 'error_description': 'Page not found'}
    return render(request, 'error_handle.html', ctx, status=404)


def custom_server_error(request, template_name='error.html'):
    # Full exception stack is logged by middleware; this renders the page.
    ctx = {'error_code': 500, 'error_description': 'Internal server error'}
    return render(request, 'error_handle.html', ctx, status=500)
