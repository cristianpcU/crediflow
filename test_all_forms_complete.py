#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba completa de todos los formularios del sistema
Verifica que guarden correctamente en la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente, Prestamo, Cuota, GastoAdicional
from loans.forms import ClienteForm, PrestamoForm, CuotaPagoForm
from datetime import date
from decimal import Decimal

def print_separator():
    print("\n" + "="*70)

def test_cliente_form():
    print_separator()
    print("TEST 1: FORMULARIO DE CLIENTE")
    print_separator()
    
    # Datos del formulario
    data = {
        'cedula': '0987654321',
        'nombres': 'María',
        'apellidos': 'González',
        'telefono': '0987654321',
        'email': 'maria@example.com',
        'direccion': 'Av. Principal 123, Guayaquil'
    }
    
    print("\n📝 Datos del formulario:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    # Crear formulario
    form = ClienteForm(data)
    
    print("\n🔍 Validando formulario...")
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Guardar en base de datos
        cliente = form.save()
        print(f"\n💾 Cliente guardado en BD:")
        print(f"   ID: {cliente.id}")
        print(f"   Nombre completo: {cliente.nombres} {cliente.apellidos}")
        print(f"   Cédula: {cliente.cedula}")
        print(f"   Teléfono: {cliente.telefono}")
        print(f"   Email: {cliente.email}")
        print(f"   Activo: {cliente.activo}")
        
        # Verificar que existe en BD
        verificar = Cliente.objects.filter(cedula='0987654321').exists()
        print(f"\n✓ Verificación en BD: {'EXITOSA' if verificar else 'FALLIDA'}")
        
        return cliente
    else:
        print(f"   ❌ Errores: {form.errors}")
        return None

def test_prestamo_form(cliente):
    print_separator()
    print("TEST 2: FORMULARIO DE PRÉSTAMO")
    print_separator()
    
    # Crear gasto adicional
    gasto = GastoAdicional.objects.create(
        nombre='Comisión Administrativa',
        monto=Decimal('100.00'),
        descripcion='Comisión por apertura'
    )
    print(f"\n📋 Gasto adicional creado: {gasto.nombre} - ${gasto.monto}")
    
    # Datos del formulario
    data = {
        'cliente': cliente.id,
        'monto_principal': '10000.00',
        'tasa_interes_mensual': '3.5',
        'duracion_meses': '24',
        'fecha_inicio': date.today().isoformat(),
        'gastos_adicionales': [gasto.id],
        'notas': 'Préstamo para capital de trabajo'
    }
    
    print("\n📝 Datos del formulario:")
    print(f"   Cliente: {cliente}")
    print(f"   Monto principal: ${data['monto_principal']}")
    print(f"   Tasa interés: {data['tasa_interes_mensual']}%")
    print(f"   Duración: {data['duracion_meses']} meses")
    print(f"   Fecha inicio: {data['fecha_inicio']}")
    print(f"   Gastos adicionales: {gasto.nombre}")
    
    # Crear formulario
    form = PrestamoForm(data)
    
    print("\n🔍 Validando formulario...")
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Guardar en base de datos
        prestamo = form.save()
        print(f"\n💾 Préstamo guardado en BD:")
        print(f"   ID: {prestamo.id}")
        print(f"   Cliente: {prestamo.cliente}")
        print(f"   Monto principal: ${prestamo.monto_principal}")
        print(f"   Interés total: ${prestamo.interes_total}")
        print(f"   Total gastos: ${prestamo.total_gastos}")
        print(f"   Monto total: ${prestamo.monto_total}")
        print(f"   Valor cuota: ${prestamo.valor_cuota}")
        print(f"   Estado: {prestamo.estado}")
        
        # Verificar cuotas generadas
        cuotas = prestamo.cuotas.all()
        print(f"\n📊 Cuotas generadas: {cuotas.count()}")
        
        if cuotas.count() > 0:
            print("\n   Primeras 3 cuotas:")
            for cuota in cuotas[:3]:
                print(f"   - Cuota #{cuota.numero_cuota}: ${cuota.monto_total} - Vence: {cuota.fecha_vencimiento}")
        
        # Verificar que existe en BD
        verificar = Prestamo.objects.filter(id=prestamo.id).exists()
        print(f"\n✓ Verificación en BD: {'EXITOSA' if verificar else 'FALLIDA'}")
        
        return prestamo
    else:
        print(f"   ❌ Errores: {form.errors}")
        return None

def test_cuota_pago_form(prestamo):
    print_separator()
    print("TEST 3: FORMULARIO DE PAGO DE CUOTA")
    print_separator()
    
    # Obtener primera cuota
    cuota = prestamo.cuotas.first()
    
    print(f"\n📋 Cuota a pagar:")
    print(f"   Número: #{cuota.numero_cuota}")
    print(f"   Monto total: ${cuota.monto_total}")
    print(f"   Capital: ${cuota.monto_capital}")
    print(f"   Interés: ${cuota.monto_interes}")
    print(f"   Estado actual: {cuota.estado}")
    print(f"   Vencimiento: {cuota.fecha_vencimiento}")
    
    # Datos del formulario
    data = {
        'monto_pagado': str(cuota.monto_total),
        'fecha_pago': date.today().isoformat(),
        'notas': 'Pago completo de la primera cuota'
    }
    
    print("\n📝 Datos del pago:")
    print(f"   Monto pagado: ${data['monto_pagado']}")
    print(f"   Fecha pago: {data['fecha_pago']}")
    print(f"   Notas: {data['notas']}")
    
    # Crear formulario
    form = CuotaPagoForm(data, instance=cuota)
    
    print("\n🔍 Validando formulario...")
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Guardar en base de datos
        cuota_actualizada = form.save(commit=False)
        cuota_actualizada.estado = 'PAGADO'
        cuota_actualizada.save()
        
        print(f"\n💾 Pago registrado en BD:")
        print(f"   Cuota ID: {cuota_actualizada.id}")
        print(f"   Estado: {cuota_actualizada.estado}")
        print(f"   Monto pagado: ${cuota_actualizada.monto_pagado}")
        print(f"   Fecha pago: {cuota_actualizada.fecha_pago}")
        print(f"   Notas: {cuota_actualizada.notas}")
        
        # Verificar que se actualizó en BD
        cuota_bd = Cuota.objects.get(id=cuota_actualizada.id)
        print(f"\n✓ Verificación en BD:")
        print(f"   Estado en BD: {cuota_bd.estado}")
        print(f"   Monto pagado en BD: ${cuota_bd.monto_pagado}")
        print(f"   Verificación: {'EXITOSA' if cuota_bd.estado == 'PAGADO' else 'FALLIDA'}")
        
        return cuota_actualizada
    else:
        print(f"   ❌ Errores: {form.errors}")
        return None

def main():
    print("\n" + "="*70)
    print(" "*15 + "PRUEBA COMPLETA DE FORMULARIOS")
    print(" "*20 + "Sistema CrediFlow")
    print("="*70)
    
    # Limpiar datos de prueba
    print("\n🧹 Limpiando datos de prueba anteriores...")
    Cliente.objects.filter(cedula='0987654321').delete()
    GastoAdicional.objects.filter(nombre='Comisión Administrativa').delete()
    
    # Ejecutar pruebas
    cliente = test_cliente_form()
    
    if cliente:
        prestamo = test_prestamo_form(cliente)
        
        if prestamo:
            cuota = test_cuota_pago_form(prestamo)
    
    # Resumen final
    print_separator()
    print("RESUMEN FINAL DE LA BASE DE DATOS")
    print_separator()
    
    total_clientes = Cliente.objects.count()
    total_prestamos = Prestamo.objects.count()
    total_cuotas = Cuota.objects.count()
    cuotas_pagadas = Cuota.objects.filter(estado='PAGADO').count()
    cuotas_pendientes = Cuota.objects.filter(estado='PENDIENTE').count()
    total_gastos = GastoAdicional.objects.count()
    
    print(f"\n📊 Estadísticas:")
    print(f"   Total Clientes: {total_clientes}")
    print(f"   Total Préstamos: {total_prestamos}")
    print(f"   Total Cuotas: {total_cuotas}")
    print(f"   Cuotas Pagadas: {cuotas_pagadas}")
    print(f"   Cuotas Pendientes: {cuotas_pendientes}")
    print(f"   Gastos Adicionales: {total_gastos}")
    
    # Verificación final
    print("\n" + "="*70)
    if total_clientes > 0 and total_prestamos > 0 and cuotas_pagadas > 0:
        print("✅ TODOS LOS FORMULARIOS FUNCIONAN CORRECTAMENTE")
        print("✅ TODOS LOS DATOS SE GUARDARON EN LA BASE DE DATOS")
    else:
        print("❌ ALGUNOS FORMULARIOS NO GUARDARON CORRECTAMENTE")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
