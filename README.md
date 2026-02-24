# CrediFlow - Sistema de Gestión de Préstamos

Sistema completo de gestión de préstamos desarrollado en Django 5 con generación automática de cuotas, interfaz moderna con Bootstrap 5 y panel de administración con AdminLTE.

## Características Principales

- ✅ **Gestión de Clientes**: Registro completo de clientes con validación de cédula ecuatoriana
- ✅ **Gestión de Préstamos**: Creación de préstamos con cálculo automático de intereses
- ✅ **Generación Automática de Cuotas**: Las cuotas se generan automáticamente al crear un préstamo
- ✅ **Gastos Adicionales**: Soporte para gastos adicionales (seguros, comisiones, etc.)
- ✅ **Dashboard Interactivo**: Visualización de estadísticas y métricas clave
- ✅ **Gestión de Vencimientos**: Módulo para cuotas próximas a vencer y vencidas
- ✅ **Formularios Modales**: Interfaz AJAX con modales Bootstrap 5
- ✅ **Panel Admin**: Django Admin nativo con estilos AdminLTE (CSS CDN)
- ✅ **Diseño Moderno**: AdminLTE 3 CSS + Bootstrap 5 + CSS personalizado
- ✅ **Comando de Actualización**: Actualización automática de estados de cuotas
- ✅ **Paquetes Actualizados**: Solo dependencias compatibles con Django 5.0

## Tecnologías Utilizadas

- **Backend**: Django 5.0 (última versión estable)
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: Bootstrap 5, AdminLTE 3 CSS (CDN), jQuery, Select2
- **Admin**: Django Admin nativo con estilos AdminLTE personalizados
- **Formularios**: Django Crispy Forms con Bootstrap 5
- **Dependencias**: Solo paquetes actualizados compatibles con Django 5.0

## Instalación

### ⚠️ IMPORTANTE: Entorno Virtual

**SIEMPRE usa el entorno virtual** para evitar instalar paquetes en todo el sistema.

Ver guía completa: [ENTORNO_VIRTUAL.md](ENTORNO_VIRTUAL.md)

### 1. Clonar el repositorio

```bash
cd /Users/cristiangiovannypaguaycadme/code/proyectos/crediflow
```

### 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual (solo la primera vez)
python3 -m venv venv

# Activar entorno virtual (SIEMPRE antes de trabajar)
source venv/bin/activate  # En macOS/Linux
# O en Windows: venv\Scripts\activate

# Verificar que está activo (deberías ver "(venv)" en tu terminal)
which python  # Debe mostrar: .../crediflow/venv/bin/python
```

**Atajo rápido:**

```bash
source activate_venv.sh  # Script que activa y verifica el venv
```

### 3. Instalar dependencias

**⚠️ ASEGÚRATE de que el entorno virtual esté activo antes de instalar:**

```bash
# Verificar que venv está activo
which pip  # Debe mostrar: .../crediflow/venv/bin/pip

# Instalar dependencias (SOLO con venv activo)
pip install -r requirements.txt

# Verificar instalación
pip list
```

**Dependencias instaladas en el entorno virtual:**

- Django 5.0.14 (última versión estable)
- django-crispy-forms 2.5
- crispy-bootstrap5 2025.6
- django-widget-tweaks 1.5.1
- python-decouple 3.8

**Notas importantes:**

- ✅ Todos los paquetes están actualizados y compatibles con Django 5.0
- ✅ No se usa `django-adminlte3` (desactualizado)
- ✅ AdminLTE 3 CSS se carga vía CDN
- ⚠️ **NUNCA** instales paquetes sin activar el entorno virtual

### 4. Ejecutar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor de desarrollo

**Con entorno virtual activo:**

```bash
python manage.py runserver
```

**Sin activar venv (usando ruta completa):**

```bash
./venv/bin/python manage.py runserver
```

El sistema estará disponible en: http://127.0.0.1:8000/

**Nota:** Puedes ejecutar comandos Django sin activar el venv usando `./venv/bin/python` en lugar de `python`

## Acceso al Sistema

### Panel Principal

- URL: http://127.0.0.1:8000/
- Dashboard con estadísticas y métricas

### Panel de Administración

- URL: http://127.0.0.1:8000/admin/
- Usuario: admin
- Contraseña: admin123

## Estructura del Proyecto

```
crediflow/
├── manage.py
├── requirements.txt
├── README.md
├── crediflow/              # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── loans/                  # Aplicación principal
    ├── models.py           # Modelos: Cliente, Prestamo, Cuota, GastoAdicional
    ├── admin.py            # Configuración del admin
    ├── views.py            # Vistas basadas en clases
    ├── forms.py            # Formularios con widgets Bootstrap
    ├── urls.py             # URLs de la aplicación
    ├── mixins.py           # Mixins para AJAX
    ├── templates/          # Templates HTML
    │   └── loans/
    │       ├── base.html
    │       ├── dashboard.html
    │       ├── cliente_list.html
    │       ├── prestamo_list.html
    │       └── modals/     # Formularios modales
    ├── static/             # Archivos estáticos
    │   └── loans/
    │       └── js/
    │           └── modals.js
    └── management/
        └── commands/
            └── actualizar_estados_cuotas.py
```

## Modelos de Datos

### Cliente

- Cédula (única, 10 dígitos)
- Nombres y apellidos
- Teléfono, email, dirección
- Estado activo/inactivo

### Préstamo

- Cliente (ForeignKey)
- Monto principal
- Tasa de interés mensual (%)
- Duración en meses
- Fecha de inicio
- Gastos adicionales (ManyToMany)
- Estado: ACTIVO, LIQUIDADO, CANCELADO

### Cuota

- Préstamo (ForeignKey)
- Número de cuota
- Fecha de vencimiento
- Monto total, capital, interés
- Estado: PENDIENTE, PAGADO, VENCIDO
- Fecha y monto de pago

### GastoAdicional

- Nombre (ej: Seguro, Comisión)
- Monto
- Descripción

## Funcionalidades

### Cálculo Automático de Cuotas

Al crear un préstamo, el sistema calcula automáticamente:

1. **Interés Total**: `monto_principal × (tasa_mensual / 100) × duracion_meses`
2. **Total Gastos**: Suma de gastos adicionales seleccionados
3. **Monto Total**: `monto_principal + interes_total + total_gastos`
4. **Valor Cuota**: `monto_total / duracion_meses`

Cada cuota incluye:

- **Capital**: `monto_principal / duracion_meses`
- **Interés**: `interes_total / duracion_meses`
- **Fecha de vencimiento**: Incrementa 30 días por cada cuota

### Gestión de Vencimientos

El sistema permite visualizar:

- **Cuotas Vencidas**: Cuotas con fecha de vencimiento pasada
- **Próximas a Vencer**: Configurable (7, 15, 30 días)

### Comando de Actualización

Actualiza automáticamente el estado de cuotas pendientes a vencido:

```bash
# Ejecutar actualización
python manage.py actualizar_estados_cuotas

# Modo dry-run (sin cambios)
python manage.py actualizar_estados_cuotas --dry-run
```

**Recomendación**: Configurar en cron para ejecución diaria:

```bash
0 0 * * * cd /ruta/proyecto && /ruta/venv/bin/python manage.py actualizar_estados_cuotas
```

## Uso del Sistema

### 1. Crear un Cliente

- Ir a "Clientes" → "Nuevo Cliente"
- Completar formulario modal
- Validación automática de cédula

### 2. Crear un Préstamo

- Ir a "Préstamos" → "Nuevo Préstamo"
- Seleccionar cliente
- Ingresar monto, tasa, duración
- Opcionalmente agregar gastos adicionales
- Las cuotas se generan automáticamente

### 3. Registrar Pagos

- Ver detalle del préstamo o ir a "Cuotas"
- Clic en botón "Pagar" de la cuota
- Ingresar monto y fecha de pago
- El estado cambia automáticamente a PAGADO

### 4. Monitorear Vencimientos

- Dashboard muestra resumen de vencimientos
- "Cuotas Vencidas" lista todas las vencidas
- "Próximas a Vencer" con filtro de días

## Panel de Administración

El panel admin incluye:

### Clientes

- Lista con búsqueda por cédula, nombre
- Filtros por estado y fecha
- Inline de préstamos del cliente

### Préstamos

- Lista con filtros por estado y fecha
- Campos calculados: interés total, monto total, valor cuota
- Inline de cuotas del préstamo
- Acción: Regenerar cuotas

### Cuotas

- Lista con estados coloreados
- Indicador de días hasta vencimiento
- Acciones: Marcar como pagado, Actualizar estados

### Gastos Adicionales

- Gestión de gastos reutilizables

## Configuración para Producción

### 1. Cambiar a PostgreSQL

Editar `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crediflow_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. Configurar variables de entorno

Crear archivo `.env`:

```
SECRET_KEY=tu-secret-key-segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### 3. Recolectar archivos estáticos

```bash
python manage.py collectstatic
```

### 4. Configurar servidor web (Nginx + Gunicorn)

```bash
pip install gunicorn
gunicorn crediflow.wsgi:application --bind 0.0.0.0:8000
```

## Credenciales por Defecto

**Superusuario**:

- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: Cambiar estas credenciales en producción

## Soporte y Contacto

Para soporte técnico o consultas sobre el sistema, contactar al equipo de desarrollo.

## Licencia

Sistema desarrollado para CrediFlow - 2024

---

**Versión**: 1.0.0  
**Última actualización**: Febrero 2024
