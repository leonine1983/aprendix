from django.urls import path
from .views import home_professor
app_name = 'modulo_professor'

urlpatterns = [
    path('', home_professor, name='homeProfessor')
]
