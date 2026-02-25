# -*- coding: utf-8 -*-
"""
Comando para crear grupos y permisos del sistema
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from loans.models import Cliente, Prestamo, Cuota, UserProfile


class Command(BaseCommand):
    help = 'Crea los grupos y permisos para el sistema de roles de CrediFlow'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('CREANDO GRUPOS Y PERMISOS PARA CREDIFLOW'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # Definir grupos y sus permisos
        grupos_permisos = {
            'Administrador': {
                'descripcion': 'Acceso total al sistema',
                'permisos': 'all'
            },
            'Gerente': {
                'descripcion': 'Supervisión y aprobación de operaciones',
                'permisos': [
                    'view_cliente', 'add_cliente', 'change_cliente', 'delete_cliente',
                    'view_prestamo', 'add_prestamo', 'change_prestamo', 'delete_prestamo',
                    'view_cuota', 'change_cuota',
                    'view_gastoadicional', 'add_gastoadicional', 'change_gastoadicional',
                ]
            },
            'Cajero': {
                'descripcion': 'Registro de pagos diarios',
                'permisos': [
                    'view_cliente',
                    'view_prestamo',
                    'view_cuota', 'change_cuota',
                ]
            },
        }

        # Crear o actualizar grupos
        for nombre_grupo, config in grupos_permisos.items():
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Grupo creado: {nombre_grupo}'))
            else:
                self.stdout.write(self.style.WARNING(f'○ Grupo existente: {nombre_grupo}'))
            
            # Limpiar permisos existentes
            grupo.permissions.clear()
            
            # Asignar permisos
            if config['permisos'] == 'all':
                # Administrador tiene todos los permisos
                all_permissions = Permission.objects.all()
                grupo.permissions.set(all_permissions)
                self.stdout.write(f'  → Permisos asignados: TODOS ({all_permissions.count()})')
            else:
                # Asignar permisos específicos
                permisos_asignados = 0
                for codename in config['permisos']:
                    try:
                        permission = Permission.objects.get(codename=codename)
                        grupo.permissions.add(permission)
                        permisos_asignados += 1
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'  ✗ Permiso no encontrado: {codename}'))
                
                self.stdout.write(f'  → Permisos asignados: {permisos_asignados}')
            
            self.stdout.write(f'  → Descripción: {config["descripcion"]}\n')

        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('GRUPOS Y PERMISOS CREADOS EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS('Resumen de grupos creados:'))
        for grupo in Group.objects.all():
            count = grupo.permissions.count()
            self.stdout.write(f'  • {grupo.name}: {count} permisos')
        
        self.stdout.write('\n')
