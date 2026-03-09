from django.http import Http404
from django.shortcuts import render


class Friendly404Middleware:
    """Captura Http404 y muestra la página amigable incluso en DEBUG."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Http404:
            context = {
                'title': 'Recurso no encontrado',
                'requested_path': request.path,
            }
            return render(request, 'errors/404.html', context, status=404)
        return response
