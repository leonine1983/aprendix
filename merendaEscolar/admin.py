from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Produto)
admin.site.register(EstoqueCentral)
admin.site.register(Transferencia)