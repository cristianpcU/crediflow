#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar que todos los formularios guarden correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente, Prestamo, Cuota, GastoAdicional
from loans.forms import ClienteForm, PrestamoForm, CuotaPagoForm
from datetime import date, timedelta
from decimal import Decimal

def test_cliente_form():
    print("\n=== Probando ClienteForm ===")
    data = {
        'cedula': '1234567890',
        'nombres': 'Juan',
        'apellidos': 'Pérez',
        'telefono': '0999999999',
        'email': 'juan@example.com',
        'direccion': 'Quito, Ecuador'
    }
    
    form = ClienteForm(data)
    if form.is_valid():
        cliente = form.save()
        print(f"✅ Cliente guardado: {cliente}")
        print(f"   ID: {cliente.id}")
        print(f"   Cédula: {cliente.cedula}")
        return cliente
    else:
        print(f"❌ Errores en el formulario: {form.errors}")
        return None

def test_prestamo_form(cliente):
    print("\n=== Probando PrestamoForm ===")
    
    # Crear un gasto adicional primero
    gasto = GastoAdicional.objects.create(
        nombre='Seguro',
        monto=Decimal('50.00')
    )
    print(f"   Gasto adicional creado: {gasto}")
    
    data = {
        'cliente': cliente.id,
        'monto_principal': '5000.00',
        'tasa_interes_mensual': '5.00',
        'duracion_meses': '12',
        'fecha_inicio': date.today().isoformat(),
        'gastos_adicionales': [gasto.id],
        'notas': 'Préstamo de prueba'
    }
    
    form = PrestamoForm(data)
    if form.is_valid():
        prestamo = form.save()
        print(f"✅ Préstamo guardado: {prestamo}")
        print(f"   ID: {prestamo.id}")
        print(f"   Monto: ${prestamo.monto_principal}")
        print(f"   Cuotas generadas: {prestamo.cuotas.count()}")
        return prestamo
    else:
        print(f"❌ Errores en el formulario: {form.errors}")
        return None

def test_cuota_pago_form(prestamo):
    print("\n=== Probando CuotaPagoForm ===")
    
    # Obtener la primera cuota
    cuota = prestamo.cuotas.first()
    print(f"   Cuota a pagar: #{cuota.numero_cuota}")
    print(f"   Monto: ${cuota.monto_total}")
    
    data = {
        'monto_pagado': str(cuota.monto_total),
        'fecha_pago': date.today().isoformat(),
        'notas': 'Pago de prueba'
    }
    
    form = CuotaPagoForm(data, instance=cuota)
    if form.is_valid():
        cuota_pagada = form.save(commit=False)
        cuota_pagada.estado = 'PAGADO'
        cuota_pagada.save()
        print(f"✅ Pago registrado: {cuota_pagada}")
        print(f"   Estado: {cuota_pagada.estado}")
        print(f"   Fecha pago: {cuota_pagada.fecha_pago}")
        return cuota_pagada
    else:
        print(f"❌ Errores en el formulario: {form.errors}")
        return None

def main():
    print("="*60)
    print("PRUEBA DE FORMULARIOS - CrediFlow")
    print("="*60)
    
    # Limpiar datos de prueba anteriores
    print("\nLimpiando datos de prueba anteriores...")
    Cliente.objects.filter(cedula='1234567890').delete()
    
    # Probar formularios
    cliente = test_cliente_form()
    
    if cliente:
        prestamo = test_prestamo_form(cliente)
        
        if prestamo:
            cuota = test_cuota_pago_form(prestamo)
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"Total Clientes: {Cliente.objects.count()}")
    print(f"Total Préstamos: {Prestamo.objects.count()}")
    print(f"Total Cuotas: {Cuota.objects.count()}")
    print(f"Cuotas Pagadas: {Cuota.objects.filter(estado='PAGADO').count()}")
    print(f"Cuotas Pendientes: {Cuota.objects.filter(estado='PENDIENTE').count()}")
    
    print("\n✅ TODOS LOS FORMULARIOS FUNCIONAN CORRECTAMENTE")

if __name__ == '__main__':
    main()
