from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente-list'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente-detail'),
    path('clientes/crear/', views.ClienteCreateView.as_view(), name='cliente-create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente-update'),
    
    # Préstamos
    path('prestamos/', views.PrestamoListView.as_view(), name='prestamo-list'),
    path('prestamos/historial/', views.PrestamoHistorialView.as_view(), name='prestamo-historial'),
    path('prestamos/<int:pk>/', views.PrestamoDetailView.as_view(), name='prestamo-detail'),
    path('prestamos/crear/', views.PrestamoCreateView.as_view(), name='prestamo-create'),
    path('prestamos/<int:pk>/editar/', views.PrestamoUpdateView.as_view(), name='prestamo-update'),
    path('prestamos/<int:pk>/eliminar/', views.PrestamoDeleteView.as_view(), name='prestamo-delete'),
    
    # Cuotas
    path('cuotas/proximas/', views.CuotasProximasView.as_view(), name='cuotas-proximas'),
    path('cuotas/vencidas/', views.CuotasVencidasView.as_view(), name='cuotas-vencidas'),
    
    # Gestión de Usuarios (solo Admin, CEO, Gerente)
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario-list'),
    path('usuarios/<int:pk>/', views.UsuarioDetailView.as_view(), name='usuario-detail'),
    path('usuarios/crear/', views.UsuarioCreateView.as_view(), name='usuario-create'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario-update'),
    path('usuarios/<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='usuario-delete'),
    path('cuotas/<int:pk>/pagar/', views.CuotaPagoView.as_view(), name='cuota-pago'),
    path('cuotas/<int:pk>/comprobante/', views.ComprobantePagoView.as_view(), name='cuota-comprobante'),
    path('prestamos/<int:pk>/liquidar/', views.PrestamoLiquidarView.as_view(), name='prestamo-liquidar'),
    
    # Gastos Adicionales
    path('gastos/crear/', views.GastoAdicionalCreateView.as_view(), name='gasto-create'),
    path('prestamos/<int:pk>/gastos/', views.PrestamoGastosUpdateView.as_view(), name='prestamo-gastos'),
    
    # Revisión de Cobros
    path('cobros/revision/', views.RevisionCobrosView.as_view(), name='revision-cobros'),
    
    # Perfil de Usuario
    path('perfil/editar/', views.UserProfileEditView.as_view(), name='user-profile-edit'),
]
