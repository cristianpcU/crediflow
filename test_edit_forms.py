#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de formularios de edición
Verifica que los formularios UPDATE funcionen correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente, Prestamo, Cuota, GastoAdicional
from loans.forms import ClienteForm, PrestamoForm
from datetime import date
from decimal import Decimal

def print_separator():
    print("\n" + "="*70)

def test_cliente_edit():
    print_separator()
    print("TEST 1: EDITAR CLIENTE")
    print_separator()
    
    # Obtener cliente existente
    try:
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ No hay clientes en la base de datos")
            return None
            
        print(f"\n📋 Cliente original:")
        print(f"   ID: {cliente.id}")
        print(f"   Nombre: {cliente.nombres} {cliente.apellidos}")
        print(f"   Cédula: {cliente.cedula}")
        print(f"   Teléfono: {cliente.telefono}")
        print(f"   Email: {cliente.email}")
        print(f"   Dirección: {cliente.direccion}")
        
        # Datos para editar
        data_editada = {
            'cedula': cliente.cedula,  # No cambiar cédula
            'nombres': 'María Fernanda',  # Cambiar nombre
            'apellidos': 'González Pérez',  # Cambiar apellido
            'telefono': '0999888777',  # Cambiar teléfono
            'email': 'mariafernanda@example.com',  # Cambiar email
            'direccion': 'Av. 9 de Octubre 456, Guayaquil'  # Cambiar dirección
        }
        
        print(f"\n📝 Datos editados:")
        print(f"   Nombres: {data_editada['nombres']}")
        print(f"   Apellidos: {data_editada['apellidos']}")
        print(f"   Teléfono: {data_editada['telefono']}")
        print(f"   Email: {data_editada['email']}")
        print(f"   Dirección: {data_editada['direccion']}")
        
        # Crear formulario con instancia existente
        form = ClienteForm(data_editada, instance=cliente)
        
        print("\n🔍 Validando formulario de edición...")
        if form.is_valid():
            print("   ✅ Formulario válido")
            
            # Guardar cambios
            cliente_actualizado = form.save()
            
            print(f"\n💾 Cliente actualizado en BD:")
            print(f"   ID: {cliente_actualizado.id}")
            print(f"   Nombre: {cliente_actualizado.nombres} {cliente_actualizado.apellidos}")
            print(f"   Teléfono: {cliente_actualizado.telefono}")
            print(f"   Email: {cliente_actualizado.email}")
            print(f"   Dirección: {cliente_actualizado.direccion}")
            
            # Verificar en BD
            cliente_bd = Cliente.objects.get(id=cliente_actualizado.id)
            verificacion = (
                cliente_bd.nombres == data_editada['nombres'] and
                cliente_bd.apellidos == data_editada['apellidos'] and
                cliente_bd.telefono == data_editada['telefono'] and
                cliente_bd.email == data_editada['email']
            )
            
            print(f"\n✓ Verificación en BD: {'EXITOSA' if verificacion else 'FALLIDA'}")
            
            if verificacion:
                print("   ✅ Todos los cambios se guardaron correctamente")
            
            return cliente_actualizado
        else:
            print(f"   ❌ Errores: {form.errors}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_prestamo_edit():
    print_separator()
    print("TEST 2: EDITAR PRÉSTAMO")
    print_separator()
    
    try:
        # Obtener préstamo existente
        prestamo = Prestamo.objects.first()
        if not prestamo:
            print("❌ No hay préstamos en la base de datos")
            return None
        
        print(f"\n📋 Préstamo original:")
        print(f"   ID: {prestamo.id}")
        print(f"   Cliente: {prestamo.cliente}")
        print(f"   Monto principal: ${prestamo.monto_principal}")
        print(f"   Tasa interés: {prestamo.tasa_interes_mensual}%")
        print(f"   Duración: {prestamo.duracion_meses} meses")
        print(f"   Notas: {prestamo.notas}")
        
        # Obtener gastos actuales
        gastos_actuales = list(prestamo.gastos_adicionales.values_list('id', flat=True))
        
        # Datos para editar (solo campos que se pueden editar sin regenerar cuotas)
        data_editada = {
            'cliente': prestamo.cliente.id,
            'monto_principal': str(prestamo.monto_principal),
            'tasa_interes_mensual': str(prestamo.tasa_interes_mensual),
            'duracion_meses': str(prestamo.duracion_meses),
            'fecha_inicio': prestamo.fecha_inicio.isoformat(),
            'gastos_adicionales': gastos_actuales,
            'notas': 'Préstamo actualizado - Cambio en las notas del sistema'
        }
        
        print(f"\n📝 Datos editados:")
        print(f"   Notas: {data_editada['notas']}")
        
        # Crear formulario con instancia existente
        form = PrestamoForm(data_editada, instance=prestamo)
        
        print("\n🔍 Validando formulario de edición...")
        if form.is_valid():
            print("   ✅ Formulario válido")
            
            # Guardar cambios
            prestamo_actualizado = form.save()
            
            print(f"\n💾 Préstamo actualizado en BD:")
            print(f"   ID: {prestamo_actualizado.id}")
            print(f"   Notas: {prestamo_actualizado.notas}")
            
            # Verificar en BD
            prestamo_bd = Prestamo.objects.get(id=prestamo_actualizado.id)
            verificacion = prestamo_bd.notas == data_editada['notas']
            
            print(f"\n✓ Verificación en BD: {'EXITOSA' if verificacion else 'FALLIDA'}")
            
            if verificacion:
                print("   ✅ Los cambios se guardaron correctamente")
            
            return prestamo_actualizado
        else:
            print(f"   ❌ Errores: {form.errors}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n" + "="*70)
    print(" "*20 + "PRUEBA DE FORMULARIOS DE EDICIÓN")
    print(" "*25 + "Sistema CrediFlow")
    print("="*70)
    
    # Verificar que hay datos
    if Cliente.objects.count() == 0:
        print("\n⚠️  No hay datos en la base de datos")
        print("   Ejecuta primero: python test_all_forms_complete.py")
        return
    
    # Probar edición de cliente
    cliente = test_cliente_edit()
    
    # Probar edición de préstamo
    prestamo = test_prestamo_edit()
    
    # Resumen
    print_separator()
    print("RESUMEN DE PRUEBAS")
    print_separator()
    
    print(f"\n📊 Resultados:")
    print(f"   Edición de Cliente: {'✅ EXITOSA' if cliente else '❌ FALLIDA'}")
    print(f"   Edición de Préstamo: {'✅ EXITOSA' if prestamo else '❌ FALLIDA'}")
    
    print("\n" + "="*70)
    if cliente and prestamo:
        print("✅ TODOS LOS FORMULARIOS DE EDICIÓN FUNCIONAN CORRECTAMENTE")
    else:
        print("❌ ALGUNOS FORMULARIOS DE EDICIÓN TIENEN PROBLEMAS")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
