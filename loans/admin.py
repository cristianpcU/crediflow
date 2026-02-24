# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, GastoAdicional, Prestamo, Cuota


class CuotaInline(admin.TabularInline):
    model = Cuota
    extra = 0
    readonly_fields = ['numero_cuota', 'fecha_vencimiento', 'monto_total', 'monto_capital', 'monto_interes', 'estado']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class PrestamoInline(admin.TabularInline):
    model = Prestamo
    extra = 0
    fields = ['monto_principal', 'tasa_interes_mensual', 'duracion_meses', 'estado', 'fecha_inicio']
    readonly_fields = ['fecha_creacion']
    can_delete = False


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombres', 'apellidos', 'telefono', 'email', 'activo', 'fecha_registro']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['cedula', 'nombres', 'apellidos', 'telefono']
    readonly_fields = ['fecha_registro']
    inlines = [PrestamoInline]
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('cedula', 'nombres', 'apellidos')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_registro')
        }),
    )


@admin.register(GastoAdicional)
class GastoAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'monto', 'activo', 'descripcion']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'monto_principal', 'tasa_interes_mensual', 'duracion_meses', 'estado', 'fecha_inicio', 'get_monto_total']
    list_filter = ['estado', 'fecha_inicio', 'fecha_creacion']
    search_fields = ['cliente__nombres', 'cliente__apellidos', 'cliente__cedula']
    readonly_fields = ['fecha_creacion', 'get_interes_total', 'get_total_gastos', 'get_monto_total', 'get_valor_cuota', 'get_progreso']
    filter_horizontal = ['gastos_adicionales']
    inlines = [CuotaInline]
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Detalles del Préstamo', {
            'fields': ('monto_principal', 'tasa_interes_mensual', 'duracion_meses', 'fecha_inicio')
        }),
        ('Gastos Adicionales', {
            'fields': ('gastos_adicionales',)
        }),
        ('Cálculos', {
            'fields': ('get_interes_total', 'get_total_gastos', 'get_monto_total', 'get_valor_cuota', 'get_progreso'),
            'classes': ('collapse',)
        }),
        ('Estado y Notas', {
            'fields': ('estado', 'notas', 'fecha_creacion')
        }),
    )
    
    def get_monto_total(self, obj):
        return f"${obj.monto_total:,.2f}"
    get_monto_total.short_description = 'Monto Total'
    
    def get_interes_total(self, obj):
        return f"${obj.interes_total:,.2f}"
    get_interes_total.short_description = 'Interés Total'
    
    def get_total_gastos(self, obj):
        return f"${obj.total_gastos:,.2f}"
    get_total_gastos.short_description = 'Total Gastos'
    
    def get_valor_cuota(self, obj):
        return f"${obj.valor_cuota:,.2f}"
    get_valor_cuota.short_description = 'Valor Cuota'
    
    def get_progreso(self, obj):
        progreso = obj.get_progreso_pago()
        return f"{progreso:.1f}%"
    get_progreso.short_description = 'Progreso de Pago'
    
    actions = ['regenerar_cuotas']
    
    def regenerar_cuotas(self, request, queryset):
        for prestamo in queryset:
            prestamo.generar_cuotas()
        self.message_user(request, f"Se regeneraron las cuotas para {queryset.count()} préstamo(s).")
    regenerar_cuotas.short_description = "Regenerar cuotas"


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ['id', 'prestamo', 'numero_cuota', 'fecha_vencimiento', 'monto_total', 'get_estado_display', 'get_dias_vencimiento']
    list_filter = ['estado', 'fecha_vencimiento']
    search_fields = ['prestamo__cliente__nombres', 'prestamo__cliente__apellidos']
    readonly_fields = ['prestamo', 'numero_cuota', 'fecha_vencimiento', 'monto_total', 'monto_capital', 'monto_interes']
    
    fieldsets = (
        ('Préstamo', {
            'fields': ('prestamo', 'numero_cuota')
        }),
        ('Montos', {
            'fields': ('monto_total', 'monto_capital', 'monto_interes')
        }),
        ('Vencimiento', {
            'fields': ('fecha_vencimiento',)
        }),
        ('Pago', {
            'fields': ('estado', 'fecha_pago', 'monto_pagado', 'notas')
        }),
    )
    
    def get_estado_display(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'PAGADO': 'green',
            'VENCIDO': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    get_estado_display.short_description = 'Estado'
    
    def get_dias_vencimiento(self, obj):
        dias = obj.dias_hasta_vencimiento()
        if dias < 0:
            return format_html('<span style="color: red;">Vencida ({} días)</span>', abs(dias))
        elif dias <= 7:
            return format_html('<span style="color: orange;">{} días</span>', dias)
        else:
            return f"{dias} días"
    get_dias_vencimiento.short_description = 'Días hasta vencimiento'
    
    actions = ['marcar_como_pagado', 'actualizar_estados']
    
    def marcar_como_pagado(self, request, queryset):
        for cuota in queryset:
            cuota.registrar_pago()
        self.message_user(request, f"Se marcaron {queryset.count()} cuota(s) como pagadas.")
    marcar_como_pagado.short_description = "Marcar como pagado"
    
    def actualizar_estados(self, request, queryset):
        count = 0
        for cuota in queryset:
            if cuota.esta_vencida() and cuota.estado == 'PENDIENTE':
                cuota.actualizar_estado()
                count += 1
        self.message_user(request, f"Se actualizaron {count} cuota(s) a estado VENCIDO.")
    actualizar_estados.short_description = "Actualizar estados vencidos"


# Personalización del sitio admin
admin.site.site_header = "CrediFlow Administración"
admin.site.site_title = "CrediFlow Admin"
admin.site.index_title = "Panel de Control de Préstamos"

# Asegurar que Django use los verbose_name correctamente
admin.site.enable_nav_sidebar = True
