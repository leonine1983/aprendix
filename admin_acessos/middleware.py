from django.contrib import messages
from django.shortcuts import redirect

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.session.get_expiry_date():
                messages.warning(request, "Sua sessão expirou. Faça login novamente.")
                return redirect('admin_acessos:login_create')
        response = self.get_response(request)
        return response