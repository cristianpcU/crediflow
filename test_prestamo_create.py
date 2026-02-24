#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba del formulario de crear préstamo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente, Prestamo
from loans.forms import PrestamoForm
from datetime import date

def test_prestamo_create():
    print("\n" + "="*70)
    print("PRUEBA: FORMULARIO DE CREAR PRÉSTAMO")
    print("="*70)
    
    # Verificar que hay clientes
    cliente = Cliente.objects.first()
    if not cliente:
        print("\n❌ No hay clientes en la base de datos")
        return False
    
    print(f"\n📋 Cliente seleccionado: {cliente}")
    
    # Datos del formulario
    data = {
        'cliente': cliente.id,
        'monto_principal': '5000.00',
        'tasa_interes_mensual': '3.5',
        'duracion_meses': '12',
        'fecha_inicio': date.today().isoformat(),
        'notas': 'Préstamo de prueba'
    }
    
    print("\n📝 Datos del formulario:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    # Crear formulario
    form = PrestamoForm(data)
    
    print("\n🔍 Validando formulario...")
    
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Contar préstamos antes
        prestamos_antes = Prestamo.objects.filter(activo=True).count()
        print(f"\n📊 Préstamos activos antes: {prestamos_antes}")
        
        # Guardar
        prestamo = form.save()
        
        print(f"\n💾 Préstamo guardado:")
        print(f"   ID: {prestamo.id}")
        print(f"   Cliente: {prestamo.cliente}")
        print(f"   Monto: ${prestamo.monto_principal}")
        print(f"   Cuotas generadas: {prestamo.cuotas.count()}")
        
        # Verificar
        prestamos_despues = Prestamo.objects.filter(activo=True).count()
        print(f"\n📊 Préstamos activos después: {prestamos_despues}")
        
        if prestamos_despues == prestamos_antes + 1:
            print("\n" + "="*70)
            print("✅ FORMULARIO DE PRÉSTAMO FUNCIONA CORRECTAMENTE")
            print("="*70)
            return True
        else:
            print("\n❌ Error en la verificación")
            return False
    else:
        print(f"   ❌ Errores en el formulario:")
        for field, errors in form.errors.items():
            print(f"      {field}: {errors}")
        return False

if __name__ == '__main__':
    test_prestamo_create()
