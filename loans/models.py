# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from decimal import Decimal
import math


class Cliente(models.Model):
    cedula = models.CharField(max_length=10, unique=True, verbose_name="Cédula")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    telefono2 = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono 2")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def get_prestamos_activos(self):
        return self.prestamo_set.filter(estado='ACTIVO')


class GastoAdicional(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Gasto Adicional"
        verbose_name_plural = "Gastos Adicionales"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - ${self.monto}"


class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('LIQUIDADO', 'Liquidado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    monto_principal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto Principal"
    )
    tasa_interes_mensual = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Tasa de Interés Mensual (%)",
        blank=True,
        null=True
    )
    monto_interes_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Monto Interés Mensual ($)",
        blank=True,
        null=True,
        help_text="Define el monto mensual a cobrar como interés. El porcentaje se calculará automáticamente"
    )
    interes_total_fijo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Interés Total ($)",
        blank=True,
        null=True,
        help_text="Si defines este valor, se usará en lugar de calcular por porcentaje"
    )
    duracion_meses = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Duración (meses)"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    gastos_adicionales = models.ManyToManyField(
        GastoAdicional, 
        blank=True, 
        verbose_name="Gastos Adicionales"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='ACTIVO',
        verbose_name="Estado"
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Préstamo #{self.pk} - {self.cliente}"

    @property
    def interes_total(self):
        # Prioridad 1: Si se definió un interés total fijo, usarlo
        if self.interes_total_fijo is not None:
            return self.interes_total_fijo
        # Prioridad 2: Si se definió un monto mensual de interés, calcular total
        if self.monto_interes_mensual is not None:
            return self.monto_interes_mensual * self.duracion_meses
        # Prioridad 3: Calcular por porcentaje
        if self.tasa_interes_mensual is not None:
            return self.monto_principal * (self.tasa_interes_mensual / 100) * self.duracion_meses
        return Decimal('0')
    
    @property
    def porcentaje_interes_calculado(self):
        """Calcula el porcentaje de interés basado en el monto mensual definido"""
        if self.monto_interes_mensual is not None and self.monto_principal > 0:
            # Porcentaje = (Monto Mensual / Monto Principal) * 100
            return (self.monto_interes_mensual / self.monto_principal) * 100
        return self.tasa_interes_mensual or Decimal('0')

    @property
    def total_gastos(self):
        return sum(gasto.monto for gasto in self.gastos_adicionales.all())

    @property
    def monto_total(self):
        return self.monto_principal + self.interes_total + self.total_gastos

    @property
    def valor_cuota(self):
        """Valor de la cuota mensual basado en las cuotas generadas"""
        # Si hay cuotas generadas, usar el valor de la primera cuota
        primera_cuota = self.cuotas.first()
        if primera_cuota:
            return primera_cuota.monto_total
        # Si no hay cuotas, calcular el promedio (sin gastos)
        if self.duracion_meses > 0:
            return (self.monto_principal + self.interes_total) / self.duracion_meses
        return Decimal('0')
    
    # Propiedades para totales REALES basados en cuotas generadas
    @property
    def total_capital_cuotas(self):
        """Suma real del capital de todas las cuotas generadas"""
        return self.cuotas.aggregate(total=Sum('monto_capital'))['total'] or Decimal('0')
    
    @property
    def total_interes_cuotas(self):
        """Suma real del interés de todas las cuotas generadas"""
        return self.cuotas.aggregate(total=Sum('monto_interes'))['total'] or Decimal('0')
    
    @property
    def total_cuotas(self):
        """Suma real del monto total de todas las cuotas generadas"""
        return self.cuotas.aggregate(total=Sum('monto_total'))['total'] or Decimal('0')

    @property
    def cuotas_pagadas(self):
        """Cantidad de cuotas pagadas"""
        return self.cuotas.filter(estado='PAGADO').count()
    
    @property
    def total_pagado(self):
        """Suma real de lo pagado en todas las cuotas"""
        return self.cuotas.aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0')

    @property
    def saldo_total_pendiente(self):
        """Total faltante: suma de saldos pendientes de todas las cuotas no pagadas completamente"""
        total = Decimal('0')
        for cuota in self.cuotas.exclude(estado='PAGADO'):
            total += cuota.saldo_pendiente
        return total

    @property
    def cuotas_no_pagadas(self):
        """Cantidad de cuotas que no están completamente pagadas"""
        return self.cuotas.exclude(estado='PAGADO').count()

    @property
    def tiene_pagos(self):
        """Indica si ya se registró al menos un pago en alguna cuota"""
        return self.cuotas.filter(estado__in=['PAGADO', 'PARCIAL']).exists()

    @property
    def fecha_fin_estimada(self):
        return self.fecha_inicio + timedelta(days=30 * self.duracion_meses)

    def generar_cuotas(self):
        # Eliminar cuotas existentes si las hay
        self.cuotas.all().delete()
        
        # CÁLCULO EXACTO basado en el monto mensual real del usuario
        
        # 1. El monto mensual total es el que ingresa el usuario
        valor_cuota = self.valor_cuota
        
        # 2. Calcular el total pagado durante todo el préstamo
        total_pagado = valor_cuota * self.duracion_meses
        
        # 3. Calcular el interés total real
        interes_total_real = total_pagado - self.monto_principal
        
        # 4. Calcular capital por cuota exacto (con alta precisión)
        capital_por_cuota = self.monto_principal / self.duracion_meses
        
        # 5. Calcular interés por cuota exacto (con alta precisión)
        interes_por_cuota = interes_total_real / self.duracion_meses
        
        # 6. Redondear a 2 decimales para display, pero mantener precisión interna
        capital_display = capital_por_cuota.quantize(Decimal('0.01'))
        interes_display = interes_por_cuota.quantize(Decimal('0.01'))
        
        # 7. Verificación y ajuste para asegurar que la suma sea exacta
        suma_display = capital_display + interes_display
        diferencia = valor_cuota - suma_display
        
        # Si hay diferencia por redondeo, ajustar el interés de la última cuota
        ajuste_interes = Decimal('0')
        if diferencia != Decimal('0'):
            ajuste_interes = diferencia
        
        # Crear todas las cuotas con valores precisos
        for i in range(1, self.duracion_meses + 1):
            fecha_vencimiento = self.fecha_inicio + timedelta(days=30 * i)
            
            # Para la última cuota, aplicar ajuste si es necesario
            if i == self.duracion_meses:
                capital_final = capital_display
                interes_final = interes_display + ajuste_interes
                # Asegurar que el total sea exactamente el monto de cuota
                total_final = valor_cuota
            else:
                capital_final = capital_display
                interes_final = interes_display
                total_final = valor_cuota
            
            Cuota.objects.create(
                prestamo=self,
                numero_cuota=i,
                fecha_vencimiento=fecha_vencimiento,
                monto_total=total_final,
                monto_capital=capital_final,
                monto_interes=interes_final,
                estado='PENDIENTE'
            )

    def get_cuotas_pendientes(self):
        return self.cuotas.filter(estado='PENDIENTE')

    def get_progreso_pago(self):
        total_cuotas = self.cuotas.count()
        if total_cuotas == 0:
            return 0
        cuotas_pagadas = self.cuotas.filter(estado='PAGADO').count()
        return (cuotas_pagadas / total_cuotas) * 100

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar cuotas automáticamente al crear el préstamo
        if is_new:
            self.generar_cuotas()


class CuotaManager(models.Manager):
    def proximas_a_vencer(self, dias=7):
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        return self.filter(
            estado='PENDIENTE',
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date(),
            prestamo__estado='ACTIVO'
        ).order_by('fecha_vencimiento')

    def vencidas(self):
        return self.filter(
            estado__in=['PENDIENTE', 'VENCIDO'],
            fecha_vencimiento__lt=timezone.now().date(),
            prestamo__estado='ACTIVO'
        ).order_by('fecha_vencimiento')


class Cuota(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PARCIAL', 'Pago Parcial'),
        ('PAGADO', 'Pagado'),
        ('VENCIDO', 'Vencido'),
    ]

    prestamo = models.ForeignKey(
        Prestamo, 
        on_delete=models.CASCADE, 
        related_name='cuotas',
        verbose_name="Préstamo"
    )
    numero_cuota = models.PositiveIntegerField(verbose_name="Número de Cuota")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Total")
    monto_capital = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Capital")
    monto_interes = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Interés")
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='PENDIENTE',
        verbose_name="Estado"
    )
    fecha_pago = models.DateField(blank=True, null=True, verbose_name="Fecha de Pago")
    monto_pagado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0'),
        verbose_name="Monto Pagado"
    )
    cobrador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cobrador",
        related_name="cobros_realizados"
    )
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")

    objects = CuotaManager()

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ['prestamo', 'numero_cuota']
        unique_together = ['prestamo', 'numero_cuota']

    def __str__(self):
        return f"Cuota #{self.numero_cuota} - {self.prestamo}"

    def actualizar_estado(self):
        if self.estado == 'PENDIENTE' and self.fecha_vencimiento < timezone.now().date():
            self.estado = 'VENCIDO'
            self.save()

    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de la cuota"""
        return self.monto_total - self.monto_pagado
    
    @property
    def interes_pagado(self):
        """Interés pagado: el interés se cobra primero"""
        return min(self.monto_pagado, self.monto_interes)
    
    @property
    def capital_pagado(self):
        """Capital pagado: lo que sobra después de cubrir el interés"""
        return max(Decimal('0'), self.monto_pagado - self.monto_interes)
    
    @property
    def capital_pendiente(self):
        """Capital que falta por pagar en esta cuota"""
        return self.monto_capital - self.capital_pagado
    
    @property
    def tiene_pago_parcial(self):
        """Indica si la cuota tiene un pago parcial"""
        return self.estado == 'PARCIAL'

    def registrar_pago(self, monto=None, fecha=None):
        if monto is None:
            monto = self.monto_total
        if fecha is None:
            fecha = timezone.now().date()
        
        self.monto_pagado = self.monto_pagado + monto
        self.fecha_pago = fecha
        
        # Si el monto pagado cubre el total, marcar como PAGADO
        if self.monto_pagado >= self.monto_total:
            self.monto_pagado = self.monto_total
            self.estado = 'PAGADO'
        else:
            self.estado = 'PARCIAL'
        self.save()

    @property
    def dias_hasta_vencimiento(self):
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days
    
    @property
    def dias_mora(self):
        """Calcula los días de mora si el pago se realizó con retraso"""
        if self.estado == 'PAGADO' and self.fecha_pago:
            # Si se pagó después de la fecha de vencimiento
            if self.fecha_pago > self.fecha_vencimiento:
                delta = self.fecha_pago - self.fecha_vencimiento
                return delta.days
        return 0

    def esta_vencida(self):
        return self.fecha_vencimiento < timezone.now().date() and self.estado != 'PAGADO'


class UserProfile(models.Model):
    """Perfil de usuario con información adicional y rol"""
    
    ROL_CHOICES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('GERENTE', 'Gerente'),
        ('CAJERO', 'Cajero'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='CAJERO', verbose_name='Rol')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"
    
    def tiene_permiso(self, permiso):
        """Verifica si el usuario tiene un permiso específico basado en su rol"""
        permisos_por_rol = {
            'ADMINISTRADOR': ['all'],  # Acceso total
            'GERENTE': [
                'ver_dashboard', 'crear_cliente', 'editar_cliente', 'ver_cliente',
                'crear_prestamo', 'editar_prestamo', 'ver_prestamo', 
                'registrar_pago', 'ver_cuotas', 'eliminar_cliente', 'eliminar_prestamo'
            ],
            'CAJERO': [
                'ver_dashboard_limitado', 'ver_cliente', 'ver_prestamo', 
                'registrar_pago', 'ver_cuotas'
            ],
        }
        
        permisos = permisos_por_rol.get(self.rol, [])
        return 'all' in permisos or permiso in permisos


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        UserProfile.objects.create(user=instance)
