from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from .models import Cliente, Prestamo, Cuota, GastoAdicional
from .forms import ClienteForm, PrestamoForm, CuotaPagoForm, GastoAdicionalForm, PrestamoGastosForm
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
        context['total_prestamos'] = Prestamo.objects.filter(estado='ACTIVO').count()
        context['total_clientes'] = Cliente.objects.filter(activo=True).count()
        context['cuotas_vencidas'] = Cuota.objects.vencidas().count()
        context['cuotas_proximas'] = Cuota.objects.proximas_a_vencer(dias=7).count()
        
        # Listas para el dashboard
        context['cuotas_vencidas_list'] = Cuota.objects.vencidas()[:5]
        context['cuotas_proximas_list'] = Cuota.objects.proximas_a_vencer(dias=7)[:5]
        context['prestamos_recientes'] = Prestamo.objects.filter(estado='ACTIVO')[:5]
        
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
        context['prestamos'] = self.object.prestamo_set.all()
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
        queryset = super().get_queryset().filter(activo=True)
        estado = self.request.GET.get('estado')
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset


class PrestamoDetailView(LoginRequiredMixin, DetailView):
    model = Prestamo
    template_name = 'loans/prestamo_detail_zen.html'
    context_object_name = 'prestamo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cuotas'] = self.object.cuotas.all()
        return context


class PrestamoCreateView(LoginRequiredMixin, AjaxFormMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'loans/modals/prestamo_form_zen.html'
    success_url = reverse_lazy('loans:prestamo-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Generar cuotas automáticamente
        self.object.generar_cuotas()
        return response


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


class CuotaPagoView(LoginRequiredMixin, AjaxFormMixin, UpdateView):
    model = Cuota
    form_class = CuotaPagoForm
    template_name = 'loans/modals/cuota_pago_form_zen.html'
    success_url = reverse_lazy('loans:dashboard')
    
    def form_valid(self, form):
        cuota = form.save(commit=False)
        cuota.estado = 'PAGADO'
        cuota.save()
        return super().form_valid(form)


class GastoAdicionalCreateView(LoginRequiredMixin, AjaxFormMixin, CreateView):
    model = GastoAdicional
    form_class = GastoAdicionalForm
    template_name = 'loans/modals/gasto_form_zen.html'
    success_url = reverse_lazy('loans:prestamo-list')


class PrestamoGastosUpdateView(LoginRequiredMixin, AjaxFormMixin, UpdateView):
    model = Prestamo
    form_class = PrestamoGastosForm
    template_name = 'loans/modals/prestamo_gastos_form_zen.html'
    
    def get_success_url(self):
        return reverse_lazy('loans:prestamo-detail', kwargs={'pk': self.object.pk})
