# -*- coding: utf-8 -*-
from django.db import models
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
        if self.duracion_meses > 0:
            return self.monto_total / self.duracion_meses
        return Decimal('0')

    @property
    def fecha_fin_estimada(self):
        return self.fecha_inicio + timedelta(days=30 * self.duracion_meses)

    def generar_cuotas(self):
        # Eliminar cuotas existentes si las hay
        self.cuotas.all().delete()
        
        # Calcular valores por cuota y redondear al entero superior
        interes_por_cuota = Decimal(str(math.ceil(float(self.interes_total / self.duracion_meses))))
        capital_por_cuota = Decimal(str(math.ceil(float(self.monto_principal / self.duracion_meses))))
        valor_cuota = Decimal(str(math.ceil(float(self.valor_cuota))))
        
        # Crear cuotas
        for i in range(1, self.duracion_meses + 1):
            fecha_vencimiento = self.fecha_inicio + timedelta(days=30 * i)
            
            Cuota.objects.create(
                prestamo=self,
                numero_cuota=i,
                fecha_vencimiento=fecha_vencimiento,
                monto_total=valor_cuota,
                monto_capital=capital_por_cuota,
                monto_interes=interes_por_cuota,
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
            fecha_vencimiento__gte=timezone.now().date()
        ).order_by('fecha_vencimiento')

    def vencidas(self):
        return self.filter(
            estado__in=['PENDIENTE', 'VENCIDO'],
            fecha_vencimiento__lt=timezone.now().date()
        ).order_by('fecha_vencimiento')


class Cuota(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
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

    def registrar_pago(self, monto=None, fecha=None):
        if monto is None:
            monto = self.monto_total
        if fecha is None:
            fecha = timezone.now().date()
        
        self.monto_pagado = monto
        self.fecha_pago = fecha
        self.estado = 'PAGADO'
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
