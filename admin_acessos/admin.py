from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm


admin.site.register(NomeclaturaJanelas)
admin.site.register(MessageUser)
admin.site.register(PaletaCores)