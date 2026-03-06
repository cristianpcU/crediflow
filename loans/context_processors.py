from .models import Cuota


def cuotas_vencidas_count(request):
    """
    Context processor para mostrar el contador de cuotas vencidas
    en todas las páginas (especialmente en el header)
    """
    if request.user.is_authenticated:
        count = Cuota.objects.vencidas().count()
        return {'cuotas_vencidas_count': count}
    return {'cuotas_vencidas_count': 0}
