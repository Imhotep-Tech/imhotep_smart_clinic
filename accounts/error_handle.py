from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest

def handler404(request, exception):
    context = {
        'error_code': '404',
        'error_description': "We can't find that page.",
        'error_details': "The page you were looking for doesn't exist or may have been moved."
    }
    return render(request, 'error_handle.html', context, status=404)

def handler500(request):
    context = {
        'error_code': '500',
        'error_description': "Something went wrong.",
        'error_details': "Our servers encountered an internal error. Please try again later or contact support."
    }
    return render(request, 'error_handle.html', context, status=500)

def handler403(request, exception):
    context = {
        'error_code': '403',
        'error_description': "Access Denied.",
        'error_details': "You don't have permission to access this resource. Please check your credentials or contact an administrator."
    }
    return render(request, 'error_handle.html', context, status=403)

def handler400(request, exception):
    context = {
        'error_code': '400',
        'error_description': "Bad Request.",
        'error_details': "The server could not understand the request due to invalid syntax or missing parameters."
    }
    return render(request, 'error_handle.html', context, status=400)

def handler401(request, exception=None):
    context = {
        'error_code': '401',
        'error_description': "Unauthorized.",
        'error_details': "Authentication is required and has failed or has not been provided."
    }
    return render(request, 'error_handle.html', context, status=401)

def handler405(request, exception=None):
    context = {
        'error_code': '405',
        'error_description': "Method Not Allowed.",
        'error_details': "The request method is not supported for the requested resource."
    }
    return render(request, 'error_handle.html', context, status=405)

def handler408(request, exception=None):
    context = {
        'error_code': '408',
        'error_description': "Request Timeout.",
        'error_details': "The server timed out waiting for the request. Please try again later."
    }
    return render(request, 'error_handle.html', context, status=408)

def handler429(request, exception=None):
    context = {
        'error_code': '429',
        'error_description': "Too Many Requests.",
        'error_details': "You've sent too many requests in a given amount of time. Please try again later."
    }
    return render(request, 'error_handle.html', context, status=429)

def handler502(request, exception=None):
    context = {
        'error_code': '502',
        'error_description': "Bad Gateway.",
        'error_details': "The server received an invalid response while acting as a gateway or proxy."
    }
    return render(request, 'error_handle.html', context, status=502)

def handler503(request, exception=None):
    context = {
        'error_code': '503',
        'error_description': "Service Unavailable.",
        'error_details': "The server is temporarily unable to handle the request. Please try again later."
    }
    return render(request, 'error_handle.html', context, status=503)

def handler504(request, exception=None):
    context = {
        'error_code': '504',
        'error_description': "Gateway Timeout.",
        'error_details': "The server acting as a gateway or proxy did not receive a timely response."
    }
    return render(request, 'error_handle.html', context, status=504)