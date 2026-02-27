from django import forms
from .models import Cliente, Prestamo, Cuota, GastoAdicional


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombres', 'apellidos', 'email', 'telefono', 'telefono2', 'direccion']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10', 'placeholder': '1234567890'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com (opcional)'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0999999999'}),
            'telefono2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0999999999 (opcional)'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa'}),
        }
        labels = {
            'cedula': 'Cédula',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'email': 'Email (Opcional)',
            'telefono': 'Teléfono',
            'telefono2': 'Teléfono 2 (Opcional)',
            'direccion': 'Dirección',
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula:
            return cedula
            
        # Validar longitud
        if len(cedula) != 10:
            raise forms.ValidationError('La cédula debe tener exactamente 10 dígitos')
        
        # Validar que sean solo números
        if not cedula.isdigit():
            raise forms.ValidationError('La cédula debe contener solo números')
        
        # Validar algoritmo de cédula ecuatoriana
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        
        for i in range(9):
            valor = int(cedula[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor
        
        digito_verificador = (10 - (suma % 10)) % 10
        
        if digito_verificador != int(cedula[9]):
            raise forms.ValidationError('La cédula ingresada no es válida')
        
        # Validar unicidad (permitir la misma cédula al editar el mismo cliente)
        qs = Cliente.objects.filter(cedula=cedula)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('Ya existe un cliente con esta cédula')
        
        return cedula


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['cliente', 'monto_principal', 'tasa_interes_mensual', 'monto_interes_mensual', 'interes_total_fijo', 'duracion_meses', 'fecha_inicio', 'notas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select select2'}),
            'monto_principal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '1000.00'}),
            'tasa_interes_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '5.00'}),
            'monto_interes_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ej: 50.00'}),
            'interes_total_fijo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ej: 150.00'}),
            'duracion_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '12'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }
        labels = {
            'cliente': 'Cliente',
            'monto_principal': 'Monto Principal ($)',
            'tasa_interes_mensual': 'Tasa de Interés Mensual (%)',
            'monto_interes_mensual': 'Monto Interés Mensual ($)',
            'interes_total_fijo': 'Interés Total Fijo ($)',
            'duracion_meses': 'Duración (meses)',
            'fecha_inicio': 'Fecha de Inicio',
            'notas': 'Notas',
        }
    
    def clean_fecha_inicio(self):
        from datetime import date, timedelta
        fecha = self.cleaned_data.get('fecha_inicio')
        if fecha:
            hoy = date.today()
            hace_5_anos = hoy - timedelta(days=365*5)
            en_5_anos = hoy + timedelta(days=365*5)
            
            if fecha < hace_5_anos:
                raise forms.ValidationError('La fecha de inicio no puede ser anterior a 5 años atrás')
            if fecha > en_5_anos:
                raise forms.ValidationError('La fecha de inicio no puede ser posterior a 5 años en el futuro')
        return fecha
    
    def clean(self):
        cleaned_data = super().clean()
        tasa_interes = cleaned_data.get('tasa_interes_mensual')
        monto_interes_mensual = cleaned_data.get('monto_interes_mensual')
        interes_fijo = cleaned_data.get('interes_total_fijo')
        
        # Validar que se defina al menos uno de los tres métodos de interés
        if not tasa_interes and not monto_interes_mensual and not interes_fijo:
            raise forms.ValidationError('Debes definir al menos uno: Tasa de Interés Mensual (%), Monto Interés Mensual ($) o Interés Total Fijo ($)')
        
        return cleaned_data


class CuotaPagoForm(forms.ModelForm):
    class Meta:
        model = Cuota
        fields = ['monto_pagado', 'fecha_pago', 'notas']
        widgets = {
            'monto_pagado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
    
    def clean_monto_pagado(self):
        monto = self.cleaned_data.get('monto_pagado')
        if monto is not None and monto <= 0:
            raise forms.ValidationError('El monto pagado debe ser mayor a cero')
        return monto


class GastoAdicionalForm(forms.ModelForm):
    class Meta:
        model = GastoAdicional
        fields = ['nombre', 'monto', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Seguro, Comisión'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción (opcional)'}),
        }
        labels = {
            'nombre': 'Nombre del Gasto',
            'monto': 'Monto ($)',
            'descripcion': 'Descripción',
        }
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise forms.ValidationError('El monto del gasto debe ser mayor a cero')
        return monto


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
