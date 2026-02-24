from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin


class AjaxFormMixin:
    """
    Mixin para manejar formularios con respuestas AJAX
    """
    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Guardado exitosamente',
                'redirect_url': self.get_success_url() if hasattr(self, 'get_success_url') else '/'
            })
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
        return super().form_invalid(form)
