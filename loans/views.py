from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
from decimal import Decimal
import json

from django.contrib.auth.models import User, Group

from .models import Cliente, Prestamo, Cuota, GastoAdicional
from .forms import ClienteForm, PrestamoForm, CuotaPagoForm, GastoAdicionalForm, PrestamoGastosForm, UserProfileForm
from .mixins import AjaxFormMixin


# Vistas de Autenticación
def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('loans:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
            
            # Redirigir a la página solicitada o al dashboard
            next_url = request.GET.get('next', 'loans:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'loans/login.html')


def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('loans:login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'loans/dashboard_zen.html'
    login_url = 'loans:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        prestamos_activos = Prestamo.objects.filter(estado='ACTIVO')
        context['total_prestamos'] = prestamos_activos.count()
        context['total_clientes'] = Cliente.objects.filter(activo=True).count()
        context['cuotas_vencidas'] = Cuota.objects.vencidas().count()
        context['cuotas_proximas'] = Cuota.objects.proximas_a_vencer(dias=7).count()
        
        # Métricas financieras - solo préstamos activos
        # Total recaudado: suma de todo lo pagado (PAGADO + PARCIAL)
        cuotas_con_pago = Cuota.objects.filter(
            estado__in=['PAGADO', 'PARCIAL'],
            prestamo__estado='ACTIVO'
        )
        context['total_recaudado'] = cuotas_con_pago.aggregate(
            total=Sum('monto_pagado')
        )['total'] or 0
        
        # Ganancia total: suma de intereses realmente cobrados
        # El interés se cobra PRIMERO, lo faltante es del capital
        ganancia = Decimal('0')
        for cuota in cuotas_con_pago:
            ganancia += cuota.interes_pagado
        context['ganancia_total'] = ganancia
        
        # Capital total en préstamos activos
        context['capital_activo'] = prestamos_activos.aggregate(
            total=Sum('monto_principal')
        )['total'] or 0
        
        # Listas para el dashboard
        context['cuotas_vencidas_list'] = Cuota.objects.vencidas()[:5]
        context['cuotas_proximas_list'] = Cuota.objects.proximas_a_vencer(dias=7)[:5]
        context['prestamos_recientes'] = prestamos_activos[:5]
        
        # Datos para gráficos
        # Préstamos por estado (solo activos, sin liquidados)
        prestamos_por_estado = Prestamo.objects.filter(estado='ACTIVO').values('estado').annotate(total=Count('id'))
        estados_labels = [p['estado'] for p in prestamos_por_estado]
        estados_data = [p['total'] for p in prestamos_por_estado]
        context['prestamos_estados_labels'] = json.dumps(estados_labels)
        context['prestamos_estados_data'] = json.dumps(estados_data)
        
        # Ganancias mensuales (últimos 6 meses) - solo préstamos activos
        from datetime import datetime
        
        # Calcular fecha de inicio (6 meses atrás aproximadamente)
        fecha_inicio = timezone.now().date() - timedelta(days=180)
        cuotas_con_fecha = Cuota.objects.filter(
            estado__in=['PAGADO', 'PARCIAL'],
            fecha_pago__gte=fecha_inicio,
            prestamo__estado='ACTIVO'
        )
        
        # Agrupar por mes y calcular interés realmente cobrado
        from collections import defaultdict
        ganancias_por_mes = defaultdict(Decimal)
        for cuota in cuotas_con_fecha:
            if cuota.fecha_pago:
                mes_key = cuota.fecha_pago.replace(day=1)
                ganancias_por_mes[mes_key] += cuota.interes_pagado
        
        meses_ordenados = sorted(ganancias_por_mes.keys())
        meses_labels = [m.strftime('%b %Y') for m in meses_ordenados]
        ganancias_data = [float(ganancias_por_mes[m]) for m in meses_ordenados]
        context['ganancias_meses_labels'] = json.dumps(meses_labels)
        context['ganancias_meses_data'] = json.dumps(ganancias_data)
        
        return context


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'loans/cliente_list_zen.html'
    context_object_name = 'clientes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Cliente.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(cedula__icontains=search)
            )
        return queryset


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'loans/cliente_detail_zen.html'
    context_object_name = 'cliente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mostrar solo préstamos activos (sin liquidados)
        context['prestamos'] = self.object.prestamo_set.filter(estado='ACTIVO')
        return context


class ClienteCreateView(LoginRequiredMixin, AjaxFormMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'loans/modals/cliente_form_zen.html'
    success_url = reverse_lazy('loans:cliente-list')


class ClienteUpdateView(LoginRequiredMixin, AjaxFormMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'loans/modals/cliente_form_zen.html'
    success_url = reverse_lazy('loans:cliente-list')


class PrestamoListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'loans/prestamo_list_zen.html'
    context_object_name = 'prestamos'
    paginate_by = 10
    
    def get_queryset(self):
        # Por defecto, mostrar solo préstamos ACTIVOS (borrado lógico de LIQUIDADOS)
        queryset = Prestamo.objects.filter(estado='ACTIVO')
        
        # Permitir filtrar por estado específico si se solicita
        estado = self.request.GET.get('estado')
        if estado:
            queryset = Prestamo.objects.filter(estado=estado)
        
        return queryset


class PrestamoHistorialView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para mostrar el historial de préstamos liquidados - Solo Admin"""
    model = Prestamo
    template_name = 'loans/prestamo_historial_zen.html'
    context_object_name = 'prestamos'
    paginate_by = 20
    
    def test_func(self):
        # Solo superusuarios o usuarios del grupo Administrador
        user = self.request.user
        return user.is_superuser or user.groups.filter(name='Administrador').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo el administrador puede acceder al historial de préstamos.')
        return redirect('loans:prestamo-list')
    
    def get_queryset(self):
        # Mostrar solo préstamos LIQUIDADOS
        return Prestamo.objects.filter(estado='LIQUIDADO').order_by('-fecha_inicio')


class PrestamoDetailView(LoginRequiredMixin, DetailView):
    model = Prestamo
    template_name = 'loans/prestamo_detail_zen.html'
    context_object_name = 'prestamo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cuotas'] = self.object.cuotas.all()
        user = self.request.user
        context['puede_gestionar_pagos'] = (
            user.is_superuser or 
            user.groups.filter(name__in=['Administrador', 'Gerente', 'Cajero']).exists()
        )
        return context


class PrestamoCreateView(LoginRequiredMixin, AjaxFormMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'loans/modals/prestamo_form_zen.html'
    success_url = reverse_lazy('loans:prestamo-list')
    
    def get_initial(self):
        initial = super().get_initial()
        # Si viene el parámetro cliente en la URL, precargarlo
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            initial['cliente'] = cliente_id
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar información de si viene desde un cliente específico
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            kwargs['cliente_preseleccionado'] = cliente_id
        return kwargs


class PrestamoUpdateView(LoginRequiredMixin, AjaxFormMixin, UpdateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'loans/modals/prestamo_form_zen.html'
    
    def form_valid(self, form):
        # Eliminar cuotas existentes
        self.object.cuotas.all().delete()
        
        # Guardar el préstamo actualizado
        response = super().form_valid(form)
        
        # Regenerar cuotas con los nuevos valores
        self.object.generar_cuotas()
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('loans:prestamo-detail', kwargs={'pk': self.object.pk})


class PrestamoDeleteView(View):
    """Vista para borrado lógico de préstamo"""
    
    def post(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)
        prestamo.activo = False
        prestamo.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Préstamo eliminado correctamente'})
        
        return redirect('loans:prestamo-list')


class CuotasProximasView(LoginRequiredMixin, ListView):
    model = Cuota
    template_name = 'loans/cuotas_vencimientos_zen.html'
    context_object_name = 'cuotas'
    
    def get_queryset(self):
        dias = int(self.request.GET.get('dias', 7))
        return Cuota.objects.proximas_a_vencer(dias=dias)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = 'proximas'
        context['dias'] = int(self.request.GET.get('dias', 7))
        context['tiene_prestamos'] = Prestamo.objects.exists()
        return context


class CuotasVencidasView(LoginRequiredMixin, ListView):
    model = Cuota
    template_name = 'loans/cuotas_vencimientos_zen.html'
    context_object_name = 'cuotas'
    
    def get_queryset(self):
        return Cuota.objects.vencidas()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = 'vencidas'
        context['tiene_prestamos'] = Prestamo.objects.exists()
        return context


class AdminOrGerenteRequiredMixin(UserPassesTestMixin):
    """Solo permite acceso a superusuarios/admin o usuarios del grupo Gerente"""
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'Gerente']).exists()
    
    def handle_no_permission(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Solo el administrador puede realizar esta acción.'}, status=403)
        messages.error(self.request, 'Solo el administrador puede realizar esta acción.')
        return redirect('loans:dashboard')


class PagoCuotaPermissionMixin(UserPassesTestMixin):
    """Permite cobrar cuotas a Admin, Gerente o Cajero"""

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=['Administrador', 'Gerente', 'Cajero']).exists()

    def handle_no_permission(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para registrar pagos.'}, status=403)
        messages.error(self.request, 'Solo administradores, gerentes o cajeros pueden registrar pagos de cuotas.')
        return redirect('loans:dashboard')


class CuotaPagoView(LoginRequiredMixin, PagoCuotaPermissionMixin, AjaxFormMixin, UpdateView):
    model = Cuota
    form_class = CuotaPagoForm
    template_name = 'loans/modals/cuota_pago_form_zen.html'
    success_url = reverse_lazy('loans:dashboard')
    
    def get_initial(self):
        initial = super().get_initial()
        # Si tiene pago parcial, precargar el saldo pendiente
        if self.object.estado == 'PARCIAL':
            initial['monto_pagado'] = self.object.saldo_pendiente
        else:
            initial['monto_pagado'] = self.object.monto_total
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cuota'] = self.object
        return context
    
    def form_valid(self, form):
        cuota = self.object
        monto_pago = form.cleaned_data['monto_pagado']
        fecha_pago = form.cleaned_data.get('fecha_pago') or timezone.now().date()
        notas = form.cleaned_data.get('notas', '')
        
        # Obtener el monto pagado ORIGINAL de la BD (antes de que el form lo sobreescriba)
        monto_pagado_anterior = Cuota.objects.filter(pk=cuota.pk).values_list('monto_pagado', flat=True).first() or Decimal('0')
        
        # Acumular el pago sobre el valor original
        cuota.monto_pagado = monto_pagado_anterior + monto_pago
        cuota.fecha_pago = fecha_pago
        cuota.cobrador = self.request.user  # Registrar quién realizó el cobro
        
        if notas:
            if cuota.notas:
                cuota.notas += f'\n{notas}'
            else:
                cuota.notas = notas
        
        # Determinar estado según el monto pagado
        if cuota.monto_pagado >= cuota.monto_total:
            cuota.monto_pagado = cuota.monto_total
            cuota.estado = 'PAGADO'
        else:
            cuota.estado = 'PARCIAL'
        
        cuota.save()
        
        # Verificar si todas las cuotas del préstamo están pagadas
        prestamo = cuota.prestamo
        total_cuotas = prestamo.cuotas.count()
        cuotas_pagadas = prestamo.cuotas.filter(estado='PAGADO').count()
        
        # Si todas las cuotas están pagadas, cambiar estado a LIQUIDADO
        if total_cuotas > 0 and cuotas_pagadas == total_cuotas:
            prestamo.estado = 'LIQUIDADO'
            prestamo.save()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return super().form_valid(form)


class PrestamoLiquidarView(AdminOrGerenteRequiredMixin, View):
    """Vista para liquidar un préstamo: paga todas las cuotas pendientes/parciales"""
    
    def post(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)
        fecha_pago = timezone.now().date()
        
        # Pagar todas las cuotas no pagadas (pendientes, parciales, vencidas)
        cuotas_pendientes = prestamo.cuotas.exclude(estado='PAGADO')
        cuotas_liquidadas = 0
        total_liquidado = Decimal('0')
        
        for cuota in cuotas_pendientes:
            saldo = cuota.saldo_pendiente  # Lo que falta por pagar
            total_liquidado += saldo
            cuota.monto_pagado = cuota.monto_total  # Completar al total
            cuota.estado = 'PAGADO'
            cuota.fecha_pago = fecha_pago
            cuota.cobrador = request.user  # Registrar quién realizó la liquidación
            if cuota.notas:
                cuota.notas += f'\nLiquidación total del préstamo (saldo: ${saldo})'
            else:
                cuota.notas = f'Liquidación total del préstamo'
            cuota.save()
            cuotas_liquidadas += 1
        
        # Cambiar estado del préstamo a LIQUIDADO
        prestamo.estado = 'LIQUIDADO'
        prestamo.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Préstamo liquidado. {cuotas_liquidadas} cuotas pagadas por ${total_liquidado:.2f}',
                'cuotas_liquidadas': cuotas_liquidadas,
                'total_liquidado': float(total_liquidado)
            })
        
        messages.success(request, f'Préstamo liquidado correctamente. {cuotas_liquidadas} cuotas pagadas.')
        return redirect('loans:prestamo-detail', pk=prestamo.pk)


class GastoAdicionalCreateView(LoginRequiredMixin, AjaxFormMixin, CreateView):
    model = GastoAdicional
    form_class = GastoAdicionalForm
    template_name = 'loans/modals/gasto_form_zen.html'
    success_url = reverse_lazy('loans:prestamo-list')


class PrestamoGastosUpdateView(LoginRequiredMixin, AjaxFormMixin, UpdateView):
    model = Prestamo
    template_name = 'loans/modals/prestamo_gastos_form_zen.html'
    fields = []  # No usamos campos del formulario, procesamos manualmente
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prestamo'] = self.object
        return context
    
    def form_valid(self, form):
        prestamo = self.object
        
        # Procesar gastos a eliminar
        gastos_a_eliminar = self.request.POST.getlist('eliminar_gasto')
        if gastos_a_eliminar:
            GastoAdicional.objects.filter(id__in=gastos_a_eliminar, prestamos=prestamo).delete()
        
        # Procesar nuevos gastos
        gastos_creados = 0
        index = 1
        while True:
            nombre_key = f'gasto_nombre_{index}'
            monto_key = f'gasto_monto_{index}'
            
            if nombre_key not in self.request.POST:
                break
            
            nombre = self.request.POST.get(nombre_key, '').strip()
            monto_str = self.request.POST.get(monto_key, '').strip()
            
            if nombre and monto_str:
                try:
                    from decimal import Decimal
                    monto = Decimal(monto_str)
                    if monto > 0:
                        # Crear el gasto
                        gasto = GastoAdicional.objects.create(
                            nombre=nombre,
                            monto=monto,
                            descripcion=f'Gasto agregado al préstamo #{prestamo.id}'
                        )
                        # Asociar al préstamo
                        prestamo.gastos_adicionales.add(gasto)
                        gastos_creados += 1
                except (ValueError, Exception) as e:
                    pass
            
            index += 1
        
        return super().form_valid(form)
    def get_success_url(self):
        return reverse('loans:prestamo-detail', kwargs={'pk': self.object.pk})


class RevisionCobrosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para revisión de cobros con filtros por semana y mes - Solo Admin, CEO y Gerente"""
    model = Cuota
    template_name = 'loans/revision_cobros_zen.html'
    context_object_name = 'cobros'
    paginate_by = 50
    
    def test_func(self):
        # Solo superusuarios/admin, CEO o Gerente pueden acceder
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'CEO', 'Gerente']).exists()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo el administrador, CEO o gerente pueden acceder a la revisión de cobros.')
        return redirect('loans:dashboard')
    
    def get_queryset(self):
        # Obtener cuotas pagadas (PAGADO o PARCIAL) de préstamos activos
        queryset = Cuota.objects.filter(
            estado__in=['PAGADO', 'PARCIAL'],
            prestamo__estado='ACTIVO',
            fecha_pago__isnull=False
        ).select_related('prestamo__cliente', 'cobrador').order_by('-fecha_pago')
        
        # Aplicar filtros
        filtro_periodo = self.request.GET.get('periodo', 'mes')
        hoy = timezone.now().date()
        
        if filtro_periodo == 'semana':
            # Última semana (7 días)
            fecha_inicio = hoy - timedelta(days=7)
            queryset = queryset.filter(fecha_pago__gte=fecha_inicio)
        elif filtro_periodo == 'mes':
            # Último mes (30 días)
            fecha_inicio = hoy - timedelta(days=30)
            queryset = queryset.filter(fecha_pago__gte=fecha_inicio)
        elif filtro_periodo == 'hoy':
            # Solo hoy
            queryset = queryset.filter(fecha_pago=hoy)
        
        # Filtro por cobrador
        cobrador_id = self.request.GET.get('cobrador')
        if cobrador_id:
            queryset = queryset.filter(cobrador_id=cobrador_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas de cobros
        cobros = self.get_queryset()
        
        # Total recaudado en el período
        context['total_recaudado'] = cobros.aggregate(
            total=Sum('monto_pagado')
        )['total'] or 0
        
        # Total de cobros realizados
        context['total_cobros'] = cobros.count()
        
        # Lista de cobradores para el filtro
        context['cobradores'] = User.objects.filter(
            cobros_realizados__isnull=False
        ).distinct().order_by('username')
        
        # Filtros activos
        context['periodo_actual'] = self.request.GET.get('periodo', 'mes')
        context['cobrador_actual'] = self.request.GET.get('cobrador', '')
        
        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """Vista para editar perfil de usuario"""
    model = User
    form_class = UserProfileForm
    template_name = 'loans/modals/user_profile_form_zen.html'
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        user = form.save()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Perfil actualizado correctamente',
                'username': user.username,
                'full_name': user.get_full_name() or user.username
            })
        
        messages.success(self.request, 'Perfil actualizado correctamente')
        return redirect('loans:dashboard')
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        
        return super().form_invalid(form)


# ==================== GESTIÓN DE USUARIOS ====================


class UsuarioGroupRestrictionMixin:
    """Restricciones de asignación y visibilidad según el rol del usuario autenticado"""

    cajero_group_name = 'Cajero'
    gerente_group_name = 'Gerente'

    def _user_is_limited_to_cajero(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name__in=['Administrador', 'CEO']).exists():
            return False
        return user.groups.filter(name=self.gerente_group_name).exists()

    def _get_cajero_group(self):
        return Group.objects.get(name=self.cajero_group_name)

    def _get_allowed_groups(self):
        if self._user_is_limited_to_cajero():
            return Group.objects.filter(name=self.cajero_group_name)
        return Group.objects.all()

    def _limit_queryset_to_cajeros(self, queryset):
        if self._user_is_limited_to_cajero():
            return queryset.filter(groups__name=self.cajero_group_name).distinct()
        return queryset

    def _should_strip_admin_flags(self, groups):
        for group in groups:
            if getattr(group, 'name', None) == self.gerente_group_name:
                return True
        return False


class UsuarioListView(LoginRequiredMixin, UserPassesTestMixin, UsuarioGroupRestrictionMixin, ListView):
    """Lista de usuarios - Solo Admin, CEO, Gerente"""
    model = User
    template_name = 'loans/usuario_list_zen.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'CEO', 'Gerente']).exists()

    def handle_no_permission(self):
        messages.error(self.request, 'Solo el administrador, CEO o gerente pueden acceder a la gestión de usuarios.')
        return redirect('loans:dashboard')

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        return self._limit_queryset_to_cajeros(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_queryset = User.objects.all()
        context['total_usuarios'] = base_queryset.count()
        context['usuarios_activos'] = base_queryset.filter(is_active=True).count()
        context['solo_cajero'] = self._user_is_limited_to_cajero()
        return context


class UsuarioDetailView(LoginRequiredMixin, UserPassesTestMixin, UsuarioGroupRestrictionMixin, DetailView):
    """Detalle de usuario - Solo Admin, CEO, Gerente"""
    model = User
    template_name = 'loans/usuario_detail_zen.html'
    context_object_name = 'usuario'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'CEO', 'Gerente']).exists()

    def handle_no_permission(self):
        messages.error(self.request, 'Solo el administrador, CEO o gerente pueden acceder a la gestión de usuarios.')
        return redirect('loans:dashboard')

    def get_queryset(self):
        return self._limit_queryset_to_cajeros(User.objects.all())


class UsuarioCreateView(LoginRequiredMixin, UserPassesTestMixin, UsuarioGroupRestrictionMixin, CreateView):
    """Crear usuario - Solo Admin, CEO, Gerente"""
    model = User
    template_name = 'loans/modals/usuario_form_zen.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']
    
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'CEO', 'Gerente']).exists()
    
    def handle_no_permission(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'No tienes permisos para realizar esta acción.'})
        messages.error(self.request, 'Solo el administrador, CEO o gerente pueden acceder a la gestión de usuarios.')
        return redirect('loans:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Usuario'
        context['action'] = 'Crear'
        context['grupos'] = self._get_allowed_groups()
        context['solo_cajero'] = self._user_is_limited_to_cajero()
        context.setdefault('grupos_actuales', [])
        return context
    
    def form_valid(self, form):
        user = form.save(commit=False)

        grupos_asignar = []
        target_is_cajero = False
        if self._user_is_limited_to_cajero():
            cajero_group = self._get_cajero_group()
            grupos_asignar = [cajero_group]
            target_is_cajero = True
        else:
            grupos_ids = self.request.POST.getlist('grupos')
            grupos_asignar = list(Group.objects.filter(id__in=grupos_ids))
            target_is_cajero = any(group.name == self.cajero_group_name for group in grupos_asignar)
            if self._should_strip_admin_flags(grupos_asignar):
                user.is_staff = False
                user.is_superuser = False

        temp_password = '1234' if target_is_cajero else User.objects.make_random_password()
        user.set_password(temp_password)

        user.save()

        if grupos_asignar:
            user.groups.set(grupos_asignar)
        else:
            user.groups.clear()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Usuario {user.username} creado correctamente. Contraseña temporal: {temp_password}',
                'redirect_url': reverse_lazy('loans:usuario-list')
            })
        
        messages.success(self.request, f'Usuario {user.username} creado correctamente. Contraseña temporal: {temp_password}')
        return redirect('loans:usuario-list')


class UsuarioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UsuarioGroupRestrictionMixin, UpdateView):
    """Editar usuario - Solo Admin, CEO, Gerente"""
    model = User
    template_name = 'loans/modals/usuario_form_zen.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']
    
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'CEO', 'Gerente']).exists()
    
    def handle_no_permission(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'No tienes permisos para realizar esta acción.'})
        messages.error(self.request, 'Solo el administrador, CEO o gerente pueden acceder a la gestión de usuarios.')
        return redirect('loans:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Usuario'
        context['action'] = 'Editar'
        context['grupos'] = self._get_allowed_groups()
        context['solo_cajero'] = self._user_is_limited_to_cajero()
        # Agregar grupos actuales del usuario
        context['grupos_actuales'] = self.object.groups.values_list('id', flat=True)
        return context
    
    def form_valid(self, form):
        user = form.save(commit=False)

        grupos_asignar = []
        if self._user_is_limited_to_cajero():
            cajero_group = self._get_cajero_group()
            grupos_asignar = [cajero_group]
        else:
            grupos_ids = self.request.POST.getlist('grupos')
            grupos_asignar = list(Group.objects.filter(id__in=grupos_ids))
            if self._should_strip_admin_flags(grupos_asignar):
                user.is_staff = False
                user.is_superuser = False

        user.save()

        if grupos_asignar:
            user.groups.set(grupos_asignar)
        else:
            user.groups.clear()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Usuario {user.username} actualizado correctamente.',
                'redirect_url': reverse_lazy('loans:usuario-list')
            })
        
        messages.success(self.request, f'Usuario {user.username} actualizado correctamente.')
        return redirect('loans:usuario-list')


class UsuarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, UsuarioGroupRestrictionMixin, View):
    """Eliminar usuario - Solo Admin, CEO, Gerente"""
    
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'CEO', 'Gerente']).exists()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo el administrador, CEO o gerente pueden acceder a la gestión de usuarios.')
        return redirect('loans:dashboard')
    
    def _get_usuario(self, pk):
        queryset = self._limit_queryset_to_cajeros(User.objects.all())
        return get_object_or_404(queryset, pk=pk)

    def get(self, request, pk):
        usuario = self._get_usuario(pk)
        
        # No permitir eliminar al propio usuario
        if usuario == request.user:
            messages.error(request, 'No puedes eliminar tu propio usuario.')
            return redirect('loans:usuario-list')
        
        # No permitir eliminar superusuarios si no es superuser
        if usuario.is_superuser and not request.user.is_superuser:
            messages.error(request, 'Solo los superusuarios pueden eliminar otros superusuarios.')
            return redirect('loans:usuario-list')
        
        return render(request, 'loans/usuario_confirm_delete_zen.html', {'usuario': usuario})
    
    def post(self, request, pk):
        usuario = self._get_usuario(pk)
        
        # No permitir eliminar al propio usuario
        if usuario == request.user:
            messages.error(request, 'No puedes eliminar tu propio usuario.')
            return redirect('loans:usuario-list')
        
        # No permitir eliminar superusuarios si no es superuser
        if usuario.is_superuser and not request.user.is_superuser:
            messages.error(request, 'Solo los superusuarios pueden eliminar otros superusuarios.')
            return redirect('loans:usuario-list')
        
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado correctamente.')
        return redirect('loans:usuario-list')


def custom_404_view(request, exception):
    """Vista personalizada para manejar recursos no encontrados"""
    context = {
        'title': 'Recurso no encontrado',
        'requested_path': request.path,
    }
    return render(request, 'errors/404.html', context, status=404)


# ==================== COMPROBANTE DE PAGO ====================

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime


class ComprobantePagoView(LoginRequiredMixin, View):
    """Generar comprobante de pago en PDF para cuotas pagadas"""
    
    def numero_a_palabras(self, numero):
        """Convertir número a palabras (español)"""
        unidades = ['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
        decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
        centenas = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS']
        
        numero = int(numero)
        
        if numero == 0:
            return 'CERO'
        
        if numero == 100:
            return 'CIEN'
        
        if numero < 10:
            return unidades[numero]
        
        if numero < 20:
            if numero == 11:
                return 'ONCE'
            elif numero == 12:
                return 'DOCE'
            elif numero == 13:
                return 'TRECE'
            elif numero == 14:
                return 'CATORCE'
            elif numero == 15:
                return 'QUINCE'
            elif numero == 16:
                return 'DIECISEIS'
            elif numero == 17:
                return 'DIECISIETE'
            elif numero == 18:
                return 'DIECIOCHO'
            elif numero == 19:
                return 'DIECINUEVE'
            else:
                return 'DIEZ' + (' Y ' + self.numero_a_palabras(numero - 10) if numero > 10 else '')
        
        if numero < 100:
            if numero % 10 == 0:
                return decenas[numero // 10]
            else:
                return decenas[numero // 10] + ' Y ' + unidades[numero % 10]
        
        if numero < 1000:
            if numero % 100 == 0:
                return centenas[numero // 100]
            else:
                return centenas[numero // 100] + ' ' + self.numero_a_palabras(numero % 100)
        
        # Para números mayores (simplificado)
        if numero < 10000:
            if numero == 1000:
                return 'MIL'
            else:
                return 'MIL ' + self.numero_a_palabras(numero % 1000)
        
        return str(numero)  # Fallback para números muy grandes
    
    def moneda_singular(self):
        """Retorna el singular de la moneda"""
        return "DÓLAR"
    
    def moneda_plural(self):
        """Retorna el plural de la moneda"""
        return "DÓLARES"
    
    def get(self, request, pk):
        cuota = get_object_or_404(Cuota, pk=pk)
        
        # Verificar que la cuota tenga pagos
        if cuota.monto_pagado <= 0:
            messages.error(request, 'Esta cuota no tiene pagos registrados.')
            return redirect('loans:prestamo-detail', cuota.prestamo.pk)
        
        # Generar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.HexColor('#2c3e50')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#5b9bd5')
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 12
        normal_style.leading = 16
        
        # Título principal con estilo de letra de cambio
        title_table = Table([["COMPROBANTE DE PAGO"]], colWidths=[6*inch])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 28),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 30))
        
        # Encabezado con solo la fecha de pago
        fecha_texto = f"FECHA DE PAGO: {cuota.fecha_pago.strftime('%d/%m/%Y')}" if cuota.fecha_pago else "FECHA DE PAGO: No registrada"
        fecha_style = ParagraphStyle(
            'FechaStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=20,
            leftIndent=30,
            backColor=colors.HexColor('#f8f9fa'),
            leftPadding=17,  # 15 + 2
            rightPadding=17,  # 15 + 2
            topPadding=12,   # 10 + 2
            bottomPadding=12  # 10 + 2
        )
        story.append(Paragraph(fecha_texto, fecha_style))
        story.append(Spacer(1, 30))
        
        # Información del cliente y préstamo
        story.append(Paragraph("DATOS DEL PRESTAMO", subtitle_style))
        
        loan_data = [
            ['CLIENTE:', cuota.prestamo.cliente.nombre_completo.upper()],
            ['PRÉSTAMO No:', f'#{cuota.prestamo.pk}'],
            ['CUOTA:', f'Cuota {cuota.numero_cuota} de {cuota.prestamo.duracion_meses}'],
            ['FECHA VENCIMIENTO:', cuota.fecha_vencimiento.strftime('%d/%m/%Y')],
            ['MONTO CUOTA:', f'${cuota.monto_total:,.2f}'],
            ['ESTADO:', cuota.get_estado_display()],
        ]
        
        loan_table = Table(loan_data, colWidths=[2.5*inch, 3.5*inch])
        loan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f3f4')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(loan_table)
        story.append(Spacer(1, 30))
        
        # Sección de monto en grande (estilo letra de cambio)
        monto_entero = int(cuota.monto_pagado)
        monto_decimales = int(round((cuota.monto_pagado - monto_entero) * 100))
        
        if monto_decimales == 0:
            amount_text = f"SON: {self.numero_a_palabras(monto_entero)} {self.moneda_plural() if monto_entero != 1 else self.moneda_singular()} EXACTOS"
        else:
            amount_text = f"SON: {self.numero_a_palabras(monto_entero)} {self.moneda_plural() if monto_entero != 1 else self.moneda_singular()} CON {self.numero_a_palabras(monto_decimales)}/100"
        amount_style = ParagraphStyle(
            'AmountText',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            alignment=1,
            backColor=colors.HexColor('#f8f9fa'),
            leftPadding=22,  # 20 + 2
            rightPadding=22, # 20 + 2
            topPadding=17,   # 15 + 2
            bottomPadding=17  # 15 + 2
        )
        story.append(Paragraph(amount_text, amount_style))
        
        # Monto en números grande
        amount_number_style = ParagraphStyle(
            'AmountNumber',
            parent=styles['Normal'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"${cuota.monto_pagado:,.2f}", amount_number_style))
        
        # Alerta si no es pago completo
        if cuota.estado != 'PAGADO':
            alert_text = f"⚠️ PAGO PARCIAL - SALDO PENDIENTE: ${cuota.saldo_pendiente:,.2f}"
            alert_style = ParagraphStyle(
                'Alert',
                parent=styles['Normal'],
                fontSize=16,
                textColor=colors.white,
                backColor=colors.HexColor('#dc3545'),
                borderWidth=1,
                borderColor=colors.HexColor('#dc3545'),
                spaceBefore=10,
                spaceAfter=20,
                alignment=1,
                leftPadding=20,
                rightPadding=20,
                topPadding=15,
                bottomPadding=15
            )
            story.append(Paragraph(alert_text, alert_style))
        
        # Pie de página eliminado por solicitud del usuario
        
        # Generar PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprobante_pago_cuota_{cuota.numero_cuota}_{cuota.prestamo.cliente.nombre_completo.replace(" ", "_")}.pdf"'
        
        return response
