#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba directa del formulario de cliente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente
from loans.forms import ClienteForm

def test_cliente_form_creation():
    print("\n" + "="*70)
    print("PRUEBA DIRECTA: FORMULARIO DE CREAR CLIENTE")
    print("="*70)
    
    # Limpiar cliente de prueba
    Cliente.objects.filter(cedula='9988776655').delete()
    
    print(f"\n📊 Clientes antes de crear: {Cliente.objects.count()}")
    
    # Datos del formulario
    form_data = {
        'cedula': '9988776655',
        'nombres': 'Carlos',
        'apellidos': 'Mendoza',
        'telefono': '0991234567',
        'email': 'carlos@example.com',
        'direccion': 'Av. Amazonas 789, Quito'
    }
    
    print("\n📝 Datos del formulario:")
    for key, value in form_data.items():
        print(f"   {key}: {value}")
    
    # Crear formulario
    form = ClienteForm(data=form_data)
    
    print("\n🔍 Validando formulario...")
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Guardar
        cliente = form.save()
        
        print(f"\n💾 Cliente creado:")
        print(f"   ID: {cliente.id}")
        print(f"   Nombre completo: {cliente.nombres} {cliente.apellidos}")
        print(f"   Cédula: {cliente.cedula}")
        print(f"   Teléfono: {cliente.telefono}")
        print(f"   Email: {cliente.email}")
        print(f"   Dirección: {cliente.direccion}")
        print(f"   Activo: {cliente.activo}")
        
        # Verificar en BD
        print(f"\n📊 Clientes después de crear: {Cliente.objects.count()}")
        
        cliente_bd = Cliente.objects.get(cedula='9988776655')
        print(f"\n✓ Verificación en BD:")
        print(f"   Encontrado: {cliente_bd.nombres} {cliente_bd.apellidos}")
        print(f"   ID en BD: {cliente_bd.id}")
        
        print("\n" + "="*70)
        print("✅ EL FORMULARIO DE CREAR CLIENTE FUNCIONA CORRECTAMENTE")
        print("✅ LOS DATOS SE GUARDAN EN LA BASE DE DATOS")
        print("="*70)
        return True
    else:
        print(f"   ❌ Errores en el formulario:")
        for field, errors in form.errors.items():
            print(f"      {field}: {errors}")
        
        print("\n" + "="*70)
        print("❌ EL FORMULARIO TIENE ERRORES DE VALIDACIÓN")
        print("="*70)
        return False

if __name__ == '__main__':
    test_cliente_form_creation()
