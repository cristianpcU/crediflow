#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba completa del formulario de editar cliente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente
from loans.forms import ClienteForm

def test_cliente_edit():
    print("\n" + "="*70)
    print("PRUEBA: FORMULARIO DE EDITAR CLIENTE")
    print("="*70)
    
    # Obtener un cliente existente
    cliente = Cliente.objects.first()
    
    if not cliente:
        print("\n❌ No hay clientes en la base de datos")
        print("   Ejecuta primero: python test_all_forms_complete.py")
        return False
    
    print(f"\n📋 Cliente a editar:")
    print(f"   ID: {cliente.id}")
    print(f"   Nombre: {cliente.nombres} {cliente.apellidos}")
    print(f"   Cédula: {cliente.cedula}")
    print(f"   Teléfono: {cliente.telefono}")
    print(f"   Email: {cliente.email}")
    print(f"   Dirección: {cliente.direccion}")
    
    # Datos editados
    datos_editados = {
        'cedula': cliente.cedula,  # No cambiar cédula
        'nombres': 'Juan Carlos',  # Cambiar
        'apellidos': 'Pérez López',  # Cambiar
        'telefono': '0998877665',  # Cambiar
        'email': 'juancarlos@example.com',  # Cambiar
        'direccion': 'Nueva Dirección 456, Quito'  # Cambiar
    }
    
    print(f"\n📝 Nuevos datos:")
    print(f"   Nombres: {datos_editados['nombres']}")
    print(f"   Apellidos: {datos_editados['apellidos']}")
    print(f"   Teléfono: {datos_editados['telefono']}")
    print(f"   Email: {datos_editados['email']}")
    print(f"   Dirección: {datos_editados['direccion']}")
    
    # Crear formulario con instancia existente
    form = ClienteForm(datos_editados, instance=cliente)
    
    print("\n🔍 Validando formulario de edición...")
    
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Guardar cambios
        cliente_actualizado = form.save()
        
        print(f"\n💾 Cliente actualizado:")
        print(f"   ID: {cliente_actualizado.id}")
        print(f"   Nombre: {cliente_actualizado.nombres} {cliente_actualizado.apellidos}")
        print(f"   Teléfono: {cliente_actualizado.telefono}")
        print(f"   Email: {cliente_actualizado.email}")
        print(f"   Dirección: {cliente_actualizado.direccion}")
        
        # Verificar en BD
        cliente_bd = Cliente.objects.get(id=cliente_actualizado.id)
        
        print(f"\n✓ Verificación en BD:")
        print(f"   Nombre en BD: {cliente_bd.nombres} {cliente_bd.apellidos}")
        print(f"   Teléfono en BD: {cliente_bd.telefono}")
        print(f"   Email en BD: {cliente_bd.email}")
        
        # Verificar que los cambios se guardaron
        verificacion = (
            cliente_bd.nombres == datos_editados['nombres'] and
            cliente_bd.apellidos == datos_editados['apellidos'] and
            cliente_bd.telefono == datos_editados['telefono'] and
            cliente_bd.email == datos_editados['email'] and
            cliente_bd.direccion == datos_editados['direccion']
        )
        
        if verificacion:
            print("\n" + "="*70)
            print("✅ FORMULARIO DE EDITAR CLIENTE FUNCIONA CORRECTAMENTE")
            print("✅ TODOS LOS CAMBIOS SE GUARDARON EN LA BASE DE DATOS")
            print("="*70)
            return True
        else:
            print("\n❌ Los cambios no se guardaron correctamente")
            return False
    else:
        print(f"   ❌ Errores en el formulario:")
        for field, errors in form.errors.items():
            print(f"      {field}: {errors}")
        
        print("\n" + "="*70)
        print("❌ EL FORMULARIO TIENE ERRORES DE VALIDACIÓN")
        print("="*70)
        return False

def test_form_loads_with_data():
    print("\n" + "="*70)
    print("PRUEBA: FORMULARIO CARGA CON DATOS EXISTENTES")
    print("="*70)
    
    cliente = Cliente.objects.first()
    
    if not cliente:
        print("\n❌ No hay clientes en la base de datos")
        return False
    
    # Crear formulario sin datos (para edición)
    form = ClienteForm(instance=cliente)
    
    print(f"\n📋 Verificando que el formulario carga los datos:")
    print(f"   Cédula inicial: {form.initial.get('cedula')}")
    print(f"   Nombres inicial: {form.initial.get('nombres')}")
    print(f"   Apellidos inicial: {form.initial.get('apellidos')}")
    print(f"   Teléfono inicial: {form.initial.get('telefono')}")
    print(f"   Email inicial: {form.initial.get('email')}")
    
    verificacion = (
        form.initial.get('cedula') == cliente.cedula and
        form.initial.get('nombres') == cliente.nombres and
        form.initial.get('apellidos') == cliente.apellidos
    )
    
    if verificacion:
        print("\n✅ El formulario carga correctamente con los datos del cliente")
        return True
    else:
        print("\n❌ El formulario no carga los datos correctamente")
        return False

def main():
    print("\n" + "="*70)
    print(" "*15 + "PRUEBA COMPLETA DE EDICIÓN DE CLIENTE")
    print("="*70)
    
    # Prueba 1: Formulario carga con datos
    test1 = test_form_loads_with_data()
    
    # Prueba 2: Formulario guarda cambios
    test2 = test_cliente_edit()
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    print(f"   Formulario carga datos: {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"   Formulario guarda cambios: {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    
    if test1 and test2:
        print("\n✅ TODAS LAS PRUEBAS PASARON")
        print("✅ EL FORMULARIO DE EDITAR CLIENTE FUNCIONA PERFECTAMENTE")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
