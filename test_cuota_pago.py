#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar la vista de pago de cuotas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crediflow.settings')
django.setup()

from loans.models import Cuota, Prestamo
from django.test import RequestFactory
from django.contrib.auth.models import User
from loans.views import CuotaPagoView

def test_cuota_pago_view():
    print("\n=== Probando Vista de Pago de Cuotas ===\n")
    
    # Obtener una cuota pendiente
    cuota = Cuota.objects.filter(estado='PENDIENTE').first()
    
    if not cuota:
        print("❌ No hay cuotas pendientes para probar")
        print("\nCreando datos de prueba...")
        # Crear datos de prueba si no existen
        from loans.models import Cliente
        from datetime import date
        from decimal import Decimal
        
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ No hay clientes en el sistema")
            return
        
        prestamo = Prestamo.objects.filter(cliente=cliente).first()
        if not prestamo:
            print("❌ No hay préstamos en el sistema")
            return
            
        cuota = prestamo.cuotas.filter(estado='PENDIENTE').first()
        
    if cuota:
        print(f"✅ Cuota encontrada: #{cuota.numero_cuota}")
        print(f"   Préstamo: {cuota.prestamo}")
        print(f"   Monto: ${cuota.monto_total}")
        print(f"   Estado: {cuota.estado}")
        print(f"   URL esperada: /cuotas/{cuota.pk}/pagar/")
        
        # Simular request
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            print("❌ No hay usuarios en el sistema")
            return
            
        request = factory.get(f'/cuotas/{cuota.pk}/pagar/')
        request.user = user
        
        # Probar la vista
        try:
            view = CuotaPagoView.as_view()
            response = view(request, pk=cuota.pk)
            print(f"\n✅ Vista responde correctamente")
            print(f"   Status code: {response.status_code}")
            print(f"   Template: loans/modals/cuota_pago_form_zen.html")
            
            if response.status_code == 200:
                print("\n✅ TODO FUNCIONA CORRECTAMENTE")
                print("\nSi el modal no se abre, el problema está en:")
                print("1. JavaScript no está cargando")
                print("2. jQuery no está disponible")
                print("3. El CSS del modal no está aplicado")
            else:
                print(f"\n❌ Error: Status code {response.status_code}")
                
        except Exception as e:
            print(f"\n❌ Error al ejecutar la vista: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No se encontraron cuotas para probar")

if __name__ == '__main__':
    test_cuota_pago_view()
