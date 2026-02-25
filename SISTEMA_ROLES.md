# Sistema de Roles y Permisos - CrediFlow

## 📋 Descripción

CrediFlow implementa un sistema de control de acceso basado en roles (RBAC) utilizando el sistema de autenticación nativo de Django. Este sistema permite gestionar permisos de usuarios de manera granular y segura.

## 👥 Roles Disponibles

### 1. **Administrador**
- **Descripción**: Acceso total al sistema
- **Permisos**: Todos (44 permisos)
- **Puede**:
  - ✅ Gestionar usuarios y roles
  - ✅ Todas las operaciones CRUD en clientes, préstamos y cuotas
  - ✅ Acceso al panel de administración de Django
  - ✅ Configuración del sistema
  - ✅ Ver todos los reportes y estadísticas

### 2. **Gerente**
- **Descripción**: Supervisión y aprobación de operaciones
- **Permisos**: 13 permisos específicos
- **Puede**:
  - ✅ Ver, crear, editar y eliminar clientes
  - ✅ Ver, crear, editar y eliminar préstamos
  - ✅ Registrar pagos de cuotas
  - ✅ Ver cuotas vencidas y próximas
  - ✅ Gestionar gastos adicionales
  - ✅ Ver dashboard completo
- **No puede**:
  - ❌ Gestionar usuarios del sistema
  - ❌ Acceder al panel de administración

### 3. **Cajero**
- **Descripción**: Registro de pagos diarios
- **Permisos**: 4 permisos específicos
- **Puede**:
  - ✅ Ver clientes (solo lectura)
  - ✅ Ver préstamos (solo lectura)
  - ✅ Registrar pagos de cuotas
  - ✅ Ver cuotas vencidas y próximas
  - ✅ Ver dashboard limitado
- **No puede**:
  - ❌ Crear, editar o eliminar clientes
  - ❌ Crear, editar o eliminar préstamos
  - ❌ Gestionar usuarios
  - ❌ Acceder al panel de administración

## 🔧 Configuración Inicial

### 1. Ejecutar Migraciones
```bash
python manage.py migrate
```

### 2. Crear Grupos y Permisos
```bash
python manage.py crear_roles
```

Este comando crea automáticamente:
- Grupo "Administrador" con todos los permisos
- Grupo "Gerente" con permisos de supervisión
- Grupo "Cajero" con permisos limitados

### 3. Crear Usuarios de Prueba (Opcional)
```bash
python manage.py crear_usuarios_prueba
```

Esto crea 3 usuarios de ejemplo:

| Usuario  | Contraseña   | Rol           |
|----------|--------------|---------------|
| admin    | admin123     | Administrador |
| gerente  | gerente123   | Gerente       |
| cajero   | cajero123    | Cajero        |

## 📝 Uso del Sistema

### Crear un Usuario Nuevo

**Opción 1: Desde el Admin de Django**
1. Acceder a `/admin/`
2. Ir a "Usuarios" → "Agregar usuario"
3. Completar username y contraseña
4. Guardar
5. Ir a "Perfiles de Usuario" → Buscar el usuario
6. Asignar el rol correspondiente

**Opción 2: Desde la Consola**
```python
from django.contrib.auth.models import User, Group
from loans.models import UserProfile

# Crear usuario
user = User.objects.create_user(
    username='nuevo_usuario',
    password='contraseña123',
    email='usuario@crediflow.com',
    first_name='Nombre',
    last_name='Apellido'
)

# Asignar rol
profile = user.profile
profile.rol = 'CAJERO'  # o 'GERENTE' o 'ADMINISTRADOR'
profile.telefono = '0999123456'
profile.save()

# Agregar al grupo correspondiente
grupo = Group.objects.get(name='Cajero')
user.groups.add(grupo)
```

### Verificar Permisos en Código

**En vistas de función:**
```python
from loans.decorators import role_required, permission_required

@role_required('ADMINISTRADOR', 'GERENTE')
def vista_solo_gerentes(request):
    # Solo accesible por Administrador y Gerente
    pass

@permission_required('crear_cliente')
def crear_cliente(request):
    # Solo si el rol tiene permiso 'crear_cliente'
    pass
```

**En vistas de clase:**
```python
from loans.permissions import RoleRequiredMixin, PermissionRequiredMixin

class MiVista(RoleRequiredMixin, ListView):
    required_roles = ['ADMINISTRADOR', 'GERENTE']
    model = Cliente

class OtraVista(PermissionRequiredMixin, CreateView):
    required_permission = 'crear_prestamo'
    model = Prestamo
```

**En templates:**
```django
{% if request.user.profile.rol == 'ADMINISTRADOR' %}
    <button>Solo para Administradores</button>
{% endif %}

{% if request.user.profile.tiene_permiso:'crear_cliente' %}
    <a href="{% url 'loans:cliente-create' %}">Crear Cliente</a>
{% endif %}
```

## 🔐 Seguridad

### Características de Seguridad Implementadas

1. **Autenticación Obligatoria**: Todas las vistas requieren login
2. **Verificación de Roles**: Control granular por rol
3. **Permisos de Django**: Integración con sistema nativo
4. **Perfil Automático**: Se crea automáticamente al crear usuario
5. **Superusuarios**: Siempre tienen acceso total

### Mejores Prácticas

- ✅ Cambiar contraseñas por defecto en producción
- ✅ Usar contraseñas fuertes (mínimo 8 caracteres)
- ✅ Revisar permisos periódicamente
- ✅ Desactivar usuarios en lugar de eliminarlos
- ✅ Auditar acciones críticas

## 📊 Tabla de Permisos Detallada

| Funcionalidad          | Administrador | Gerente | Cajero |
|------------------------|---------------|---------|--------|
| Ver Dashboard          | ✅ Completo   | ✅ Completo | ⚠️ Limitado |
| Crear Cliente          | ✅            | ✅      | ❌     |
| Editar Cliente         | ✅            | ✅      | ❌     |
| Eliminar Cliente       | ✅            | ✅      | ❌     |
| Ver Cliente            | ✅            | ✅      | ✅     |
| Crear Préstamo         | ✅            | ✅      | ❌     |
| Editar Préstamo        | ✅            | ✅      | ❌     |
| Eliminar Préstamo      | ✅            | ✅      | ❌     |
| Ver Préstamo           | ✅            | ✅      | ✅     |
| Registrar Pago         | ✅            | ✅      | ✅     |
| Ver Cuotas             | ✅            | ✅      | ✅     |
| Gestionar Usuarios     | ✅            | ❌      | ❌     |
| Panel Admin Django     | ✅            | ❌      | ❌     |
| Gastos Adicionales     | ✅            | ✅      | ❌     |

## 🛠️ Archivos del Sistema

### Modelos
- `loans/models.py` - Modelo `UserProfile`

### Decoradores y Mixins
- `loans/decorators.py` - Decoradores para vistas de función
- `loans/permissions.py` - Mixins para vistas de clase

### Comandos de Gestión
- `loans/management/commands/crear_roles.py` - Crear grupos y permisos
- `loans/management/commands/crear_usuarios_prueba.py` - Usuarios de ejemplo

### Admin
- `loans/admin.py` - Registro de `UserProfile` en admin

## 🔄 Mantenimiento

### Agregar un Nuevo Rol

1. Editar `loans/models.py`:
```python
ROL_CHOICES = [
    ('ADMINISTRADOR', 'Administrador'),
    ('GERENTE', 'Gerente'),
    ('CAJERO', 'Cajero'),
    ('NUEVO_ROL', 'Nuevo Rol'),  # Agregar aquí
]
```

2. Actualizar permisos en `tiene_permiso()`:
```python
'NUEVO_ROL': ['permiso1', 'permiso2'],
```

3. Agregar al comando `crear_roles.py`

4. Ejecutar migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py crear_roles
```

### Modificar Permisos de un Rol

1. Editar `loans/management/commands/crear_roles.py`
2. Ejecutar: `python manage.py crear_roles`

## 📞 Soporte

Para consultas sobre el sistema de roles:
- Revisar este documento
- Consultar código en `loans/models.py`
- Verificar permisos en Django Admin

## 📜 Changelog

### Versión 1.0 (Febrero 2026)
- ✅ Implementación inicial del sistema de roles
- ✅ 3 roles: Administrador, Gerente, Cajero
- ✅ Decoradores y mixins de permisos
- ✅ Comandos de gestión automatizados
- ✅ Integración con Django Admin
- ✅ Usuarios de prueba
