# -*- coding: utf-8 -*-
"""
Comando para crear usuarios de prueba con diferentes roles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from loans.models import UserProfile


class Command(BaseCommand):
    help = 'Crea usuarios de prueba con diferentes roles para testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('CREANDO USUARIOS DE PRUEBA PARA CREDIFLOW'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # Definir usuarios de prueba
        usuarios_prueba = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@crediflow.com',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'rol': 'ADMINISTRADOR',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'gerente',
                'password': 'gerente123',
                'email': 'gerente@crediflow.com',
                'first_name': 'Juan',
                'last_name': 'Gerente',
                'rol': 'GERENTE',
                'telefono': '0999123456',
            },
            {
                'username': 'cajero',
                'password': 'cajero123',
                'email': 'cajero@crediflow.com',
                'first_name': 'María',
                'last_name': 'Cajera',
                'rol': 'CAJERO',
                'telefono': '0999234567',
            },
        ]

        for user_data in usuarios_prueba:
            username = user_data['username']
            
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'○ Usuario ya existe: {username}'))
                user = User.objects.get(username=username)
            else:
                # Crear usuario
                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data.get('is_staff', False),
                    is_superuser=user_data.get('is_superuser', False),
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Usuario creado: {username}'))
            
            # Actualizar o crear perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.rol = user_data['rol']
            profile.telefono = user_data.get('telefono', '')
            profile.activo = True
            profile.save()
            
            # Asignar al grupo correspondiente
            rol_nombre = user_data['rol'].capitalize()
            try:
                grupo = Group.objects.get(name=rol_nombre)
                user.groups.clear()
                user.groups.add(grupo)
                self.stdout.write(f'  → Rol: {user_data["rol"]}')
                self.stdout.write(f'  → Grupo: {grupo.name}')
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  ✗ Grupo no encontrado: {rol_nombre}'))
            
            self.stdout.write(f'  → Email: {user_data["email"]}')
            self.stdout.write(f'  → Contraseña: {user_data["password"]}\n')

        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('USUARIOS DE PRUEBA CREADOS EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # Mostrar tabla de credenciales
        self.stdout.write(self.style.SUCCESS('Credenciales de acceso:\n'))
        self.stdout.write('┌─────────────┬──────────────┬────────────────┐')
        self.stdout.write('│ Usuario     │ Contraseña   │ Rol            │')
        self.stdout.write('├─────────────┼──────────────┼────────────────┤')
        for user_data in usuarios_prueba:
            username = user_data['username'].ljust(11)
            password = user_data['password'].ljust(12)
            rol = user_data['rol'].ljust(14)
            self.stdout.write(f'│ {username} │ {password} │ {rol} │')
        self.stdout.write('└─────────────┴──────────────┴────────────────┘\n')
