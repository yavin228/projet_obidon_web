"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentification (allauth + Django auth)
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    
    # Application core (toutes les URLs principales)
    path('', include('core.urls')),
    
    # URLs spécifiques (déjà dans core/urls.py, donc optionnelles ici)
    # path('update-currency/', views.update_currency_preference, name='update_currency'),
]

# Configuration pour le mode DEBUG (développement uniquement)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Servir également les fichiers des STATICFILES_DIRS
    for directory in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=directory)