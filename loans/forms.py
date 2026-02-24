from django import forms
from .models import Cliente, Prestamo, Cuota, GastoAdicional


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombres', 'apellidos', 'email', 'telefono', 'direccion']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10', 'placeholder': '1234567890'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0999999999'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa'}),
        }
        labels = {
            'cedula': 'Cédula',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'email': 'Email',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and len(cedula) != 10:
            raise forms.ValidationError('La cédula debe tener exactamente 10 dígitos')
        if cedula and not cedula.isdigit():
            raise forms.ValidationError('La cédula debe contener solo números')
        return cedula


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['cliente', 'monto_principal', 'tasa_interes_mensual', 'duracion_meses', 'fecha_inicio', 'notas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select select2'}),
            'monto_principal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '1000.00'}),
            'tasa_interes_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '5.00'}),
            'duracion_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '12'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }
        labels = {
            'cliente': 'Cliente',
            'monto_principal': 'Monto Principal ($)',
            'tasa_interes_mensual': 'Tasa de Interés Mensual (%)',
            'duracion_meses': 'Duración (meses)',
            'fecha_inicio': 'Fecha de Inicio',
            'notas': 'Notas',
        }


class CuotaPagoForm(forms.ModelForm):
    class Meta:
        model = Cuota
        fields = ['monto_pagado', 'fecha_pago', 'notas']
        widgets = {
            'monto_pagado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'monto_pagado': 'Monto Pagado ($)',
            'fecha_pago': 'Fecha de Pago',
            'notas': 'Notas',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['monto_pagado'].initial = self.instance.monto_total


class GastoAdicionalForm(forms.ModelForm):
    class Meta:
        model = GastoAdicional
        fields = ['nombre', 'monto', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Seguro, Comisión'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción (opcional)'}),
        }
        labels = {
            'nombre': 'Nombre del Gasto',
            'monto': 'Monto ($)',
            'descripcion': 'Descripción',
        }


class PrestamoGastosForm(forms.ModelForm):
    """Formulario para gestionar gastos adicionales de un préstamo existente"""
    class Meta:
        model = Prestamo
        fields = ['gastos_adicionales']
        widgets = {
            'gastos_adicionales': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'gastos_adicionales': 'Gastos Adicionales',
        }
