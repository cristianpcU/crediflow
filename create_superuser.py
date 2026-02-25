#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear un superusuario para CrediFlow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    print("\n" + "="*70)
    print("CREAR SUPERUSUARIO PARA CREDIFLOW")
    print("="*70)
    
    # Verificar si ya existe un superusuario
    if User.objects.filter(is_superuser=True).exists():
        print("\n⚠️  Ya existe un superusuario en el sistema.")
        respuesta = input("¿Desea crear otro? (s/n): ")
        if respuesta.lower() != 's':
            print("\n❌ Operación cancelada.")
            return
    
    print("\nIngrese los datos del nuevo superusuario:")
    print("-" * 70)
    
    # Solicitar datos
    username = input("Usuario: ").strip()
    if not username:
        print("\n❌ El nombre de usuario es obligatorio.")
        return
    
    # Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        print(f"\n❌ El usuario '{username}' ya existe.")
        return
    
    email = input("Email (opcional): ").strip()
    first_name = input("Nombre (opcional): ").strip()
    last_name = input("Apellido (opcional): ").strip()
    
    # Solicitar contraseña
    import getpass
    password = getpass.getpass("Contraseña: ")
    password_confirm = getpass.getpass("Confirmar contraseña: ")
    
    if password != password_confirm:
        print("\n❌ Las contraseñas no coinciden.")
        return
    
    if len(password) < 4:
        print("\n❌ La contraseña debe tener al menos 4 caracteres.")
        return
    
    # Crear superusuario
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email or '',
            password=password,
            first_name=first_name or '',
            last_name=last_name or ''
        )
        
        print("\n" + "="*70)
        print("✅ SUPERUSUARIO CREADO EXITOSAMENTE")
        print("="*70)
        print(f"\n👤 Usuario: {user.username}")
        if user.email:
            print(f"📧 Email: {user.email}")
        if user.get_full_name():
            print(f"📝 Nombre completo: {user.get_full_name()}")
        print(f"\n🔐 Permisos: Superusuario (acceso total)")
        print("\n" + "="*70)
        print("Ahora puede iniciar sesión en CrediFlow con estas credenciales.")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error al crear el superusuario: {e}")

if __name__ == '__main__':
    create_superuser()
