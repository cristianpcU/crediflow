from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente-list'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente-detail'),
    path('clientes/crear/', views.ClienteCreateView.as_view(), name='cliente-create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente-update'),
    
    # Préstamos
    path('prestamos/', views.PrestamoListView.as_view(), name='prestamo-list'),
    path('prestamos/<int:pk>/', views.PrestamoDetailView.as_view(), name='prestamo-detail'),
    path('prestamos/crear/', views.PrestamoCreateView.as_view(), name='prestamo-create'),
    path('prestamos/<int:pk>/editar/', views.PrestamoUpdateView.as_view(), name='prestamo-update'),
    path('prestamos/<int:pk>/eliminar/', views.PrestamoDeleteView.as_view(), name='prestamo-delete'),
    
    # Cuotas
    path('cuotas/proximas/', views.CuotasProximasView.as_view(), name='cuotas-proximas'),
    path('cuotas/vencidas/', views.CuotasVencidasView.as_view(), name='cuotas-vencidas'),
    path('cuotas/<int:pk>/pagar/', views.CuotaPagoView.as_view(), name='cuota-pago'),
    
    # Gastos Adicionales
    path('gastos/crear/', views.GastoAdicionalCreateView.as_view(), name='gasto-create'),
    path('prestamos/<int:pk>/gastos/', views.PrestamoGastosUpdateView.as_view(), name='prestamo-gastos'),
]
