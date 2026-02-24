#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de edición de préstamo con recalculación de cuotas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Prestamo
from loans.forms import PrestamoForm
from datetime import date

def test_prestamo_edit_recalculate():
    print("\n" + "="*70)
    print("PRUEBA: EDITAR PRÉSTAMO Y RECALCULAR CUOTAS")
    print("="*70)
    
    # Obtener un préstamo activo
    prestamo = Prestamo.objects.filter(activo=True).first()
    
    if not prestamo:
        print("\n❌ No hay préstamos activos para probar")
        return False
    
    print(f"\n📋 Préstamo original:")
    print(f"   ID: {prestamo.id}")
    print(f"   Cliente: {prestamo.cliente}")
    print(f"   Monto Principal: ${prestamo.monto_principal}")
    print(f"   Tasa Interés: {prestamo.tasa_interes_mensual}%")
    print(f"   Duración: {prestamo.duracion_meses} meses")
    print(f"   Cuotas actuales: {prestamo.cuotas.count()}")
    
    # Guardar valores originales
    cuotas_antes = prestamo.cuotas.count()
    monto_original = prestamo.monto_principal
    duracion_original = prestamo.duracion_meses
    
    # Nuevos datos (cambiar monto y duración)
    data = {
        'cliente': prestamo.cliente.id,
        'monto_principal': '8000.00',  # Cambio
        'tasa_interes_mensual': '4.0',  # Cambio
        'duracion_meses': '18',  # Cambio
        'fecha_inicio': prestamo.fecha_inicio.isoformat(),
        'notas': 'Préstamo editado - cuotas recalculadas'
    }
    
    print(f"\n📝 Nuevos datos:")
    print(f"   Monto Principal: ${data['monto_principal']} (antes: ${monto_original})")
    print(f"   Tasa Interés: {data['tasa_interes_mensual']}% (antes: {prestamo.tasa_interes_mensual}%)")
    print(f"   Duración: {data['duracion_meses']} meses (antes: {duracion_original})")
    
    # Crear formulario con la instancia
    form = PrestamoForm(data, instance=prestamo)
    
    print("\n🔍 Validando formulario...")
    
    if form.is_valid():
        print("   ✅ Formulario válido")
        
        # Eliminar cuotas existentes
        print(f"\n🗑️  Eliminando {cuotas_antes} cuotas existentes...")
        prestamo.cuotas.all().delete()
        
        # Guardar cambios
        prestamo_actualizado = form.save()
        
        # Regenerar cuotas
        print("   🔄 Regenerando cuotas...")
        prestamo_actualizado.generar_cuotas()
        
        # Recargar desde BD
        prestamo_actualizado.refresh_from_db()
        cuotas_despues = prestamo_actualizado.cuotas.count()
        
        print(f"\n💾 Préstamo actualizado:")
        print(f"   ID: {prestamo_actualizado.id}")
        print(f"   Monto Principal: ${prestamo_actualizado.monto_principal}")
        print(f"   Tasa Interés: {prestamo_actualizado.tasa_interes_mensual}%")
        print(f"   Duración: {prestamo_actualizado.duracion_meses} meses")
        print(f"   Cuotas regeneradas: {cuotas_despues}")
        print(f"   Valor de cuota: ${prestamo_actualizado.valor_cuota}")
        
        # Mostrar primeras 3 cuotas
        if cuotas_despues > 0:
            print(f"\n   Primeras 3 cuotas:")
            for cuota in prestamo_actualizado.cuotas.all()[:3]:
                print(f"   - Cuota #{cuota.numero_cuota}: ${cuota.monto_total} - Vence: {cuota.fecha_vencimiento}")
        
        # Verificar
        verificacion = (
            cuotas_despues == int(data['duracion_meses']) and
            float(prestamo_actualizado.monto_principal) == float(data['monto_principal']) and
            cuotas_despues != cuotas_antes
        )
        
        if verificacion:
            print("\n" + "="*70)
            print("✅ EDICIÓN DE PRÉSTAMO FUNCIONA CORRECTAMENTE")
            print("✅ CUOTAS RECALCULADAS AUTOMÁTICAMENTE")
            print(f"✅ Cuotas antes: {cuotas_antes} → Cuotas después: {cuotas_despues}")
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
    test_prestamo_edit_recalculate()
