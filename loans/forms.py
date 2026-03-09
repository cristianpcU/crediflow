from django import forms
from django.contrib.auth.models import User
from .models import Cliente, Prestamo, Cuota, GastoAdicional
from decimal import Decimal, InvalidOperation


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombres', 'apellidos', 'email', 'telefono', 'telefono2', 'direccion', 'observaciones']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10', 'placeholder': '1234567890'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com (opcional)'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0999999999'}),
            'telefono2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0999999999 (opcional)'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales (opcional)'}),
        }
        labels = {
            'cedula': 'Cédula',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'email': 'Email (Opcional)',
            'telefono': 'Teléfono',
            'telefono2': 'Teléfono 2 (Opcional)',
            'direccion': 'Dirección',
            'observaciones': 'Observaciones (Opcional)',
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
        fields = ['cliente', 'monto_principal', 'duracion_meses', 'tasa_interes_mensual', 'monto_interes_mensual', 'interes_total_fijo', 'fecha_inicio', 'notas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select select2'}),
            'monto_principal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '1000.00'}),
            'duracion_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '12'}),
            'tasa_interes_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '5.00', 'readonly': 'readonly'}),
            'monto_interes_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ej: 50.00', 'readonly': 'readonly'}),
            'interes_total_fijo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ej: 150.00', 'readonly': 'readonly'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }
        labels = {
            'cliente': 'Cliente',
            'monto_principal': 'Monto Principal ($)',
            'duracion_meses': 'Duración (meses)',
            'tasa_interes_mensual': 'Tasa de Interés Mensual (%) - Calculado',
            'monto_interes_mensual': 'Monto Interés Mensual ($) - Calculado',
            'interes_total_fijo': 'Interés Total ($) - Calculado',
            'fecha_inicio': 'Fecha de Inicio',
            'notas': 'Notas',
        }
    
    # Campo adicional para ingresar el monto mensual a cobrar
    monto_cuota_mensual = forms.DecimalField(
        required=False,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Ej: 0.00',
            'id': 'id_monto_cuota_mensual'
        }),
        label='Monto Mensual a Cobrar ($)',
        help_text='Ingrese el monto total que cobrará mensualmente (capital + interés)'
    )
    
    def __init__(self, *args, **kwargs):
        # Extraer parámetro personalizado antes de llamar a super()
        cliente_preseleccionado = kwargs.pop('cliente_preseleccionado', None)
        
        super().__init__(*args, **kwargs)
        
        # Establecer fecha actual como valor por defecto si no hay instancia
        if not self.instance or not self.instance.pk:
            from datetime import date
            today = date.today()
            fecha_str = today.strftime('%Y-%m-%d')
            
            # Establecer valor inicial
            self.fields['fecha_inicio'].initial = today
            print(f"DEBUG: Initial establecido: {self.fields['fecha_inicio'].initial}")
            
            # Establecer valor directamente en el widget
            self.fields['fecha_inicio'].widget.attrs['value'] = fecha_str
            print(f"DEBUG: Widget value establecido: {self.fields['fecha_inicio'].widget.attrs['value']}")
            
            # También establecer data-value como fallback
            self.fields['fecha_inicio'].widget.attrs['data-value'] = fecha_str
            
            print(f"DEBUG: Fecha actual establecida: {fecha_str}")
        else:
            print(f"DEBUG: Es edición, no se establece fecha por defecto. Instance PK: {self.instance.pk}")
        
        # Remover readonly de los campos calculados para que se envíen en el POST
        # Usar pop() para evitar KeyError si el atributo no existe
        self.fields['tasa_interes_mensual'].widget.attrs.pop('readonly', None)
        self.fields['monto_interes_mensual'].widget.attrs.pop('readonly', None)
        self.fields['interes_total_fijo'].widget.attrs.pop('readonly', None)
        
        # Si es edición (instance existe), deshabilitar el campo cliente y precargar cuota
        if self.instance and self.instance.pk:
            self.fields['cliente'].disabled = True
            self.fields['cliente'].widget.attrs['style'] = 'background-color: #e9ecef; cursor: not-allowed;'
            self.fields['cliente'].help_text = 'El cliente no puede ser modificado en un préstamo existente'
            # Precargar monto_cuota_mensual con el valor actual de la cuota
            if self.instance.cuotas.exists():
                self.fields['monto_cuota_mensual'].initial = self.instance.valor_cuota
        
        # Si viene desde el módulo de cliente (creación con cliente preseleccionado)
        if cliente_preseleccionado:
            self.fields['cliente'].disabled = True
            self.fields['cliente'].widget.attrs['style'] = 'background-color: #e9ecef; cursor: not-allowed;'
            self.fields['cliente'].help_text = 'Cliente seleccionado automáticamente'
    
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
        monto_principal = cleaned_data.get('monto_principal')
        duracion_meses = cleaned_data.get('duracion_meses')
        
        # Obtener monto_cuota_mensual del data (campo no está en el modelo)
        monto_cuota_str = self.data.get('monto_cuota_mensual', '').strip()
        monto_cuota = None
        
        if monto_cuota_str:
            try:
                monto_cuota = Decimal(monto_cuota_str)
            except (ValueError, InvalidOperation):
                raise forms.ValidationError('El Monto Mensual a Cobrar debe ser un número válido')
        
        # Validar que se defina al menos uno de los métodos de interés
        if not tasa_interes and not monto_interes_mensual and not interes_fijo and not monto_cuota:
            raise forms.ValidationError('Debes definir al menos uno: Monto Mensual a Cobrar, Tasa de Interés Mensual (%), Monto Interés Mensual ($) o Interés Total Fijo ($)')
        
        # Si se definió monto_cuota_mensual, validar que sea mayor que la cuota de capital
        if monto_cuota and monto_principal and duracion_meses:
            import math
            capital_por_cuota = Decimal(str(math.ceil(float(monto_principal / duracion_meses))))
            
            if monto_cuota < capital_por_cuota:
                raise forms.ValidationError(
                    f'El Monto Mensual a Cobrar (${monto_cuota}) debe ser mayor o igual que la cuota de capital (${capital_por_cuota}). '
                    f'El capital se redondea hacia arriba para garantizar que se pague todo el préstamo.'
                )
        
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


class UserProfileForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'zen-form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'zen-form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'zen-form-control', 'placeholder': 'correo@ejemplo.com'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Validar que el email no esté en uso por otro usuario
            qs = User.objects.filter(email=email)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise forms.ValidationError('Este correo electrónico ya está en uso')
        
        return email
