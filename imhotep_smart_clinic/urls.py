"""
URL configuration for imhotep_smart_clinic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.http import HttpResponse
import os

handler401 = 'tasks.error_handle.handler401'
handler405 = 'tasks.error_handle.handler405'
handler408 = 'tasks.error_handle.handler408'
handler429 = 'tasks.error_handle.handler429'
handler502 = 'tasks.error_handle.handler502'
handler503 = 'tasks.error_handle.handler503'
handler504 = 'tasks.error_handle.handler504'

def serve_sitemap(request):
    sitemap_path = os.path.join(settings.STATIC_ROOT, 'sitemap.xml')
    if not os.path.exists(sitemap_path):
        sitemap_path = os.path.join(settings.BASE_DIR, 'static', 'sitemap.xml')
    
    with open(sitemap_path, 'r') as f:
        content = f.read()
    
    return HttpResponse(content, content_type='application/xml')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('doctor/', include('doctor.urls')),
    path('assistant/', include('assistant.urls')),
    
    # Add these lines to serve service-worker.js from the root
    path('service-worker.js', 
         RedirectView.as_view(url=settings.STATIC_URL + 'service-worker.js', permanent=False),
         name='service-worker'),
         
    # Add this line if you need to serve offline.html from the root
    path('offline.html',
         TemplateView.as_view(template_name='offline.html'),
         name='offline'),
         
    path('sitemap.xml', serve_sitemap, name='sitemap'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
