#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba del formulario de préstamo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente, Prestamo, Cuota
from loans.forms import PrestamoForm
from datetime import date

def test_prestamo_form():
    print("\n" + "="*70)
    print("PRUEBA: FORMULARIO DE CREAR PRÉSTAMO")
    print("="*70)
    
    # Verificar que hay clientes
    cliente = Cliente.objects.first()
    if not cliente:
        print("\n❌ No hay clientes en la base de datos")
        print("   Crea un cliente primero")
        return False
    
    print(f"\n📋 Cliente seleccionado: {cliente}")
    
    # Datos del formulario (sin gastos adicionales)
    data = {
        'cliente': cliente.id,
        'monto_principal': '15000.00',
        'tasa_interes_mensual': '4.5',
        'duracion_meses': '18',
        'fecha_inicio': date.today().isoformat(),
        'notas': 'Préstamo de prueba sin gastos adicionales'
    }
    
    print("\n📝 Datos del formulario:")
    print(f"   Cliente: {cliente}")
    print(f"   Monto Principal: ${data['monto_principal']}")
    print(f"   Tasa Interés: {data['tasa_interes_mensual']}%")
    print(f"   Duración: {data['duracion_meses']} meses")
    print(f"   Fecha Inicio: {data['fecha_inicio']}")
    print(f"   Notas: {data['notas']}")
    
    # Crear formulario
    form = PrestamoForm(data)
    
    print("\n🔍 Validando formulario...")
    
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Contar préstamos antes
        prestamos_antes = Prestamo.objects.count()
        print(f"\n📊 Préstamos antes de guardar: {prestamos_antes}")
        
        # Guardar
        prestamo = form.save()
        
        print(f"\n💾 Préstamo guardado:")
        print(f"   ID: {prestamo.id}")
        print(f"   Cliente: {prestamo.cliente}")
        print(f"   Monto Principal: ${prestamo.monto_principal}")
        print(f"   Tasa Interés: {prestamo.tasa_interes_mensual}%")
        print(f"   Duración: {prestamo.duracion_meses} meses")
        print(f"   Interés Total: ${prestamo.interes_total}")
        print(f"   Total Gastos: ${prestamo.total_gastos}")
        print(f"   Monto Total: ${prestamo.monto_total}")
        print(f"   Valor Cuota: ${prestamo.valor_cuota}")
        print(f"   Estado: {prestamo.estado}")
        
        # Verificar cuotas generadas
        cuotas = prestamo.cuotas.all()
        print(f"\n📊 Cuotas generadas: {cuotas.count()}")
        
        if cuotas.count() > 0:
            print("\n   Primeras 3 cuotas:")
            for cuota in cuotas[:3]:
                print(f"   - Cuota #{cuota.numero_cuota}: ${cuota.monto_total} - Vence: {cuota.fecha_vencimiento}")
        
        # Verificar en BD
        prestamos_despues = Prestamo.objects.count()
        print(f"\n📊 Préstamos después de guardar: {prestamos_despues}")
        
        verificacion = (
            prestamos_despues == prestamos_antes + 1 and
            cuotas.count() == int(data['duracion_meses'])
        )
        
        if verificacion:
            print("\n" + "="*70)
            print("✅ FORMULARIO DE PRÉSTAMO FUNCIONA CORRECTAMENTE")
            print("✅ PRÉSTAMO GUARDADO EN LA BASE DE DATOS")
            print("✅ CUOTAS GENERADAS AUTOMÁTICAMENTE")
            print("="*70)
            return True
        else:
            print("\n❌ Algo falló en la verificación")
            return False
    else:
        print(f"   ❌ Errores en el formulario:")
        for field, errors in form.errors.items():
            print(f"      {field}: {errors}")
        
        print("\n" + "="*70)
        print("❌ EL FORMULARIO TIENE ERRORES DE VALIDACIÓN")
        print("="*70)
        return False

if __name__ == '__main__':
    test_prestamo_form()
