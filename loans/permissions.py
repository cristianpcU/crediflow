# -*- coding: utf-8 -*-
"""
Mixins para control de acceso basado en roles en vistas de clase
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin para requerir uno o más roles específicos en vistas de clase
    Uso: required_roles = ['ADMINISTRADOR', 'GERENTE']
    """
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Superusuarios tienen acceso total
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # Verificar si el usuario tiene perfil
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Tu cuenta no tiene un perfil asignado. Contacta al administrador.')
            return redirect('loans:dashboard')
        
        # Verificar rol
        if request.user.profile.rol in self.required_roles:
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('loans:dashboard')


class PermissionRequiredMixin(LoginRequiredMixin):
    """
    Mixin para requerir un permiso específico en vistas de clase
    Uso: required_permission = 'crear_cliente'
    """
    required_permission = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Superusuarios tienen acceso total
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # Verificar permiso
        if hasattr(request.user, 'profile') and request.user.profile.tiene_permiso(self.required_permission):
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('loans:dashboard')
