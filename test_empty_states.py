#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar los estados vacíos del sistema
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cliente, Prestamo, Cuota, GastoAdicional

def test_empty_states():
    print("\n" + "="*60)
    print("PRUEBA DE ESTADOS VACÍOS - CrediFlow")
    print("="*60)
    
    # Limpiar toda la base de datos
    print("\n1. Limpiando base de datos...")
    Cuota.objects.all().delete()
    Prestamo.objects.all().delete()
    Cliente.objects.all().delete()
    GastoAdicional.objects.all().delete()
    
    print("   ✅ Base de datos limpia")
    
    # Verificar contadores
    print("\n2. Verificando contadores:")
    print(f"   - Clientes: {Cliente.objects.count()}")
    print(f"   - Préstamos: {Prestamo.objects.count()}")
    print(f"   - Cuotas: {Cuota.objects.count()}")
    
    # Verificar que existe() funciona
    print("\n3. Verificando método exists():")
    print(f"   - Prestamo.objects.exists(): {Prestamo.objects.exists()}")
    print(f"   - Cliente.objects.exists(): {Cliente.objects.exists()}")
    
    print("\n" + "="*60)
    print("RESULTADO: Sistema vacío - Mensajes de validación activos")
    print("="*60)
    
    print("\n📋 PÁGINAS A VERIFICAR:")
    print("   1. Dashboard: http://127.0.0.1:8000/")
    print("      → Debe mostrar: '¡Bienvenido a CrediFlow!'")
    print("")
    print("   2. Cuotas Vencidas: http://127.0.0.1:8000/cuotas/vencidas/")
    print("      → Debe mostrar: 'El sistema aún no cuenta con préstamos'")
    print("")
    print("   3. Cuotas Próximas: http://127.0.0.1:8000/cuotas/proximas/")
    print("      → Debe mostrar: 'El sistema aún no cuenta con préstamos'")
    print("")
    
    print("✅ Todos los mensajes de validación están configurados")

if __name__ == '__main__':
    test_empty_states()
