"""SistemaHibrido URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.conf.urls import url
from django.views.generic.base import TemplateView
from core import views as cviews
from users import views as uviews
from . import views_root

urlpatterns = [
    path('', views_root.start, name='start'),
    path('admin/', admin.site.urls),
    path('login/', uviews.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', cviews.home, name='home'),
    url('register/', include('users.urls'), name='users-register'),
    #path('edit/', include('users.urls'), name='users-edit'),         
    #path('canvas/', TemplateView.as_view(template_name='core/canvas.html'), name='canvas'), 
    path('canvas/', include('core.urls'), name='core-canvas')
]
