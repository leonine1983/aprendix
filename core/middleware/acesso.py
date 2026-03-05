from core.models.acesso import HistoricoAcesso

class LogAcessoMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if request.user.is_authenticated:
            ip = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            HistoricoAcesso.objects.create(
                user=request.user,
                ip=ip,
                user_agent=user_agent,
                dispositivo=user_agent[:180],
            )

        return response