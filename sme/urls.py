from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler400, handler404, handler500, handler403
from django.shortcuts import render
from django.http import FileResponse
import os
from django.conf import settings


def error_400(request, exception):

    return render(request, 'Escola/inicio.html', {'conteudo_page' :"400"  }, status=400)

def error_403(request, exception):
    return render(request, 'Admin_Acessos/erros/403.html', {'conteudo_page' :"403"  }, status=403)

def error_404(request, exception):
    return render(request, 'Escola/inicio.html', {'conteudo_page' :"404"  }, status=404)

def error_500(request):
    return render(request, 'Escola/inicio.html',{'conteudo_page' :"500"  }, status=500)

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500

from django.http import FileResponse, Http404
import os


def serve_sw(request):

    sw_path = os.path.join(
        settings.BASE_DIR,
        'base_static',
        'sw.js'
    )

    if not os.path.exists(sw_path):
        raise Http404()

    response = FileResponse(
        open(sw_path, 'rb'),
        content_type='application/javascript'
    )

    response["Service-Worker-Allowed"] = "/"

    return response

urlpatterns = [    
    path('sw.js', serve_sw, name='sw'),
    path('', include('admin_acessos.urls')),
    path('admin/', admin.site.urls),   
    path('core/', include('core.urls')), 
    path('rh/', include('rh.urls')),
    path('sga/Sist.Gest.Aprendizagem/', include('gestao_escolar.urls')),
    path('sga/atividadesPedagogicas/', include('modulo_atividadesPedagogicas.urls')),
    path('administrativo/', include('docsGestao_Escolar.urls')),
    path('acesso_aluno/', include('modulo_aluno.urls')),
    path('acesso_professor/', include('modulo_professor.urls')),
    #path('central_admin/', include('admin_acessos.urls')),
    path('nutricao_merenda/', include('merendaEscolar.urls')),
    path('escola_merenda/', include('modulo_Merendeiras.urls')),
    
    # extras
    path('ckeditor/', include("ckeditor_uploader.urls")),

    path("arquitetura/", include("arquitetura.urls")),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
