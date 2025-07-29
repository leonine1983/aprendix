from django.urls import path
from gestao_escolar.views import *


urlpatterns = [
    path('abrir-pdf/', abri_tutorial, name='tutorial_pdf'),
]