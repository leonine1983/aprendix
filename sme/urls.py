from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', include('admin_acessos.urls')),
    path('admin/', admin.site.urls),    
    path('rh/', include('rh.urls')),
    path('', include('gestao_escolar.urls')),
    path('nutricao/', include('controle_estoque.urls')),
    path('central_admin/', include('admin_acessos.urls')),
    # extras
    path('ckeditor/', include("ckeditor_uploader.urls"))
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
