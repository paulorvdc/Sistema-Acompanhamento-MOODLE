from django.urls import path
from . import views

urlpatterns = [
    path('', views.canvas, name='canvas'),
    path('model', views.report, name='model'),
    path('rotulados', views.rotulados, name='rotulados'),
    path('motivos', views.motivos, name='motivos'),
    path('selecionar', views.selecionar, name='selecionar'),
    path('acompanhar', views.acompanhar, name='acompanhar'),
    path('ajax/load_categories', views.load_categories, name='ajax_load_categories'),
    path('ajax/load_courses', views.load_courses, name='ajax_load_courses')
]