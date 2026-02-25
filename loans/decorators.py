# -*- coding: utf-8 -*-
"""
Decoradores para control de acceso basado en roles
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """
    Decorador para requerir uno o más roles específicos
    Uso: @role_required('ADMINISTRADOR', 'GERENTE')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('loans:login')
            
            # Superusuarios tienen acceso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar si el usuario tiene perfil
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'Tu cuenta no tiene un perfil asignado. Contacta al administrador.')
                return redirect('loans:dashboard')
            
            # Verificar rol
            if request.user.profile.rol in roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('loans:dashboard')
        
        return wrapper
    return decorator


def permission_required(permission):
    """
    Decorador para requerir un permiso específico
    Uso: @permission_required('crear_cliente')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('loans:login')
            
            # Superusuarios tienen acceso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar permiso
            if hasattr(request.user, 'profile') and request.user.profile.tiene_permiso(permission):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'No tienes permisos para realizar esta acción.')
            return redirect('loans:dashboard')
        
        return wrapper
    return decorator
