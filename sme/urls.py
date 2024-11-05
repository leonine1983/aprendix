from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler400, handler404, handler500, handler403
from django.shortcuts import render


def error_400(request, exception):
    return render(request, 'errors/403.html', status=400)

def error_403(request, exception):
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/404.html', status=500)

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500

urlpatterns = [    
    path('', include('admin_acessos.urls')),
    path('admin/', admin.site.urls),    
    path('rh/', include('rh.urls')),
    path('', include('gestao_escolar.urls')),
    path('nutricao/', include('controle_estoque.urls')),
    path('administrativo/', include('docsGestao_Escolar.urls')),
    #path('central_admin/', include('admin_acessos.urls')),
    # extras
    path('ckeditor/', include("ckeditor_uploader.urls"))
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
