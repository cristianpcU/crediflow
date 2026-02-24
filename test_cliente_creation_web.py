#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de creación de cliente simulando el formulario web
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from django.test import Client as TestClient
from loans.models import Cliente
import json

def test_cliente_creation():
    print("\n" + "="*70)
    print("PRUEBA DE CREACIÓN DE CLIENTE VÍA FORMULARIO WEB")
    print("="*70)
    
    # Limpiar cliente de prueba si existe
    Cliente.objects.filter(cedula='1122334455').delete()
    
    # Datos del formulario
    form_data = {
        'cedula': '1122334455',
        'nombres': 'Pedro',
        'apellidos': 'Ramírez',
        'telefono': '0987654321',
        'email': 'pedro@example.com',
        'direccion': 'Calle Principal 123'
    }
    
    print("\n📝 Datos del formulario:")
    for key, value in form_data.items():
        print(f"   {key}: {value}")
    
    # Crear cliente de prueba usando Django Test Client
    client = TestClient()
    
    # Hacer POST request simulando AJAX
    print("\n🔄 Enviando POST request...")
    response = client.post(
        '/clientes/crear/',
        data=form_data,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"\n📊 Respuesta del servidor:")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            if data.get('success'):
                print("\n✅ Formulario procesado exitosamente")
                
                # Verificar en base de datos
                try:
                    cliente = Cliente.objects.get(cedula='1122334455')
                    print(f"\n💾 Cliente guardado en BD:")
                    print(f"   ID: {cliente.id}")
                    print(f"   Nombre: {cliente.nombres} {cliente.apellidos}")
                    print(f"   Cédula: {cliente.cedula}")
                    print(f"   Teléfono: {cliente.telefono}")
                    print(f"   Email: {cliente.email}")
                    print(f"   Dirección: {cliente.direccion}")
                    print(f"   Activo: {cliente.activo}")
                    
                    print("\n✅ CLIENTE GUARDADO CORRECTAMENTE EN LA BASE DE DATOS")
                    return True
                except Cliente.DoesNotExist:
                    print("\n❌ ERROR: Cliente no encontrado en la base de datos")
                    return False
            else:
                print("\n❌ El servidor respondió con success=False")
                return False
        except json.JSONDecodeError:
            print(f"   Contenido: {response.content[:200]}")
    elif response.status_code == 400:
        try:
            data = json.loads(response.content)
            print(f"   Errores: {data.get('errors')}")
        except:
            print(f"   Contenido: {response.content[:200]}")
    else:
        print(f"   Contenido: {response.content[:200]}")
    
    print("\n❌ PRUEBA FALLIDA")
    return False

def main():
    result = test_cliente_creation()
    
    print("\n" + "="*70)
    if result:
        print("✅ EL FORMULARIO DE CLIENTE FUNCIONA Y GUARDA CORRECTAMENTE")
    else:
        print("❌ EL FORMULARIO TIENE PROBLEMAS")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
