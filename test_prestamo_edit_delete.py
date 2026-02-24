#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de editar y eliminar préstamo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Prestamo

def test_prestamo_edit_delete():
    print("\n" + "="*70)
    print("PRUEBA: EDITAR Y ELIMINAR PRÉSTAMO (BORRADO LÓGICO)")
    print("="*70)
    
    # Obtener un préstamo activo
    prestamos_activos = Prestamo.objects.filter(activo=True)
    
    print(f"\n📊 Préstamos activos: {prestamos_activos.count()}")
    
    if prestamos_activos.count() == 0:
        print("\n❌ No hay préstamos activos para probar")
        return False
    
    prestamo = prestamos_activos.first()
    
    print(f"\n📋 Préstamo seleccionado:")
    print(f"   ID: {prestamo.id}")
    print(f"   Cliente: {prestamo.cliente}")
    print(f"   Monto: ${prestamo.monto_principal}")
    print(f"   Estado: {prestamo.estado}")
    print(f"   Activo: {prestamo.activo}")
    
    # Probar borrado lógico
    print(f"\n🗑️  Realizando borrado lógico...")
    prestamo.activo = False
    prestamo.save()
    
    # Verificar
    prestamo.refresh_from_db()
    print(f"   Activo después de eliminar: {prestamo.activo}")
    
    # Verificar que no aparece en la lista
    prestamos_activos_despues = Prestamo.objects.filter(activo=True)
    print(f"\n📊 Préstamos activos después de eliminar: {prestamos_activos_despues.count()}")
    
    # Verificar que sigue en la BD
    todos_prestamos = Prestamo.objects.all()
    print(f"📊 Total de préstamos en BD: {todos_prestamos.count()}")
    
    verificacion = (
        not prestamo.activo and 
        prestamos_activos_despues.count() == prestamos_activos.count() - 1 and
        todos_prestamos.count() == prestamos_activos.count()
    )
    
    if verificacion:
        print("\n" + "="*70)
        print("✅ BORRADO LÓGICO FUNCIONA CORRECTAMENTE")
        print("✅ El préstamo se marca como inactivo (activo=False)")
        print("✅ No aparece en la lista de préstamos activos")
        print("✅ Pero permanece en la base de datos")
        print("="*70)
        
        # Restaurar para futuras pruebas
        prestamo.activo = True
        prestamo.save()
        print("\n✅ Préstamo restaurado para futuras pruebas")
        
        return True
    else:
        print("\n❌ El borrado lógico no funcionó correctamente")
        return False

if __name__ == '__main__':
    test_prestamo_edit_delete()
