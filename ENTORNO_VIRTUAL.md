# Guía del Entorno Virtual - CrediFlow

## ⚠️ IMPORTANTE: Siempre Usar el Entorno Virtual

**NUNCA instales paquetes sin activar el entorno virtual**. Esto evita:
- ❌ Instalar paquetes en todo el sistema
- ❌ Conflictos con otros proyectos
- ❌ Problemas de permisos
- ❌ Versiones incompatibles

## ✅ Cómo Activar el Entorno Virtual

### Opción 1: Script Automático (Recomendado)

```bash
source activate_venv.sh
```

Este script:
- Verifica que estés en el directorio correcto
- Activa el entorno virtual
- Muestra los paquetes instalados
- Confirma que todo está correcto

### Opción 2: Activación Manual

**En macOS/Linux:**
```bash
source venv/bin/activate
```

**En Windows:**
```bash
venv\Scripts\activate
```

## 🔍 Verificar que el Entorno Virtual Está Activo

Deberías ver `(venv)` al inicio de tu línea de comando:
```
(venv) usuario@computadora:~/crediflow$
```

También puedes verificar con:
```bash
which python
# Debería mostrar: /ruta/al/proyecto/crediflow/venv/bin/python

python -c "import sys; print(sys.prefix)"
# Debería mostrar: /ruta/al/proyecto/crediflow/venv
```

## 📦 Instalar/Actualizar Paquetes (CON ENTORNO VIRTUAL ACTIVO)

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Instalar paquetes
pip install -r requirements.txt

# 3. Verificar instalación
pip list
```

## 🚫 Desactivar el Entorno Virtual

Cuando termines de trabajar:
```bash
deactivate
```

## 📋 Paquetes Instalados en el Entorno Virtual

Los siguientes paquetes están instalados SOLO en el entorno virtual:

- Django 5.0.14
- django-crispy-forms 2.5
- crispy-bootstrap5 2025.6
- django-widget-tweaks 1.5.1
- python-decouple 3.8
- asgiref 3.11.1
- sqlparse 0.5.5

## 🔧 Comandos Útiles

### Ver paquetes instalados
```bash
pip list
```

### Ver ubicación de un paquete
```bash
pip show django
```

### Verificar versión de Django
```bash
python -m django --version
```

### Ejecutar servidor (con venv activo)
```bash
python manage.py runserver
```

### Ejecutar servidor (sin activar venv manualmente)
```bash
./venv/bin/python manage.py runserver
```

## ⚡ Atajos Rápidos

### Ejecutar comandos Django sin activar venv

Si no quieres activar el entorno virtual cada vez, puedes usar la ruta completa:

```bash
# Ejecutar servidor
./venv/bin/python manage.py runserver

# Hacer migraciones
./venv/bin/python manage.py makemigrations

# Aplicar migraciones
./venv/bin/python manage.py migrate

# Crear superusuario
./venv/bin/python manage.py createsuperuser

# Ejecutar shell
./venv/bin/python manage.py shell

# Ejecutar comando personalizado
./venv/bin/python manage.py actualizar_estados_cuotas
```

## 🆘 Solución de Problemas

### Problema: "django-admin: command not found"
**Solución:** Activa el entorno virtual primero
```bash
source venv/bin/activate
```

### Problema: "ModuleNotFoundError: No module named 'django'"
**Solución:** El entorno virtual no está activo o los paquetes no están instalados
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problema: Paquetes instalados en el sistema en lugar del venv
**Solución:** Verifica que el entorno virtual esté activo antes de instalar
```bash
# Verificar
which pip
# Debe mostrar: /ruta/al/proyecto/crediflow/venv/bin/pip

# Si no es así, activa el venv
source venv/bin/activate
```

### Problema: El entorno virtual está corrupto
**Solución:** Recrear el entorno virtual
```bash
# Eliminar venv actual
rm -rf venv

# Crear nuevo venv
python3 -m venv venv

# Activar
source venv/bin/activate

# Reinstalar paquetes
pip install -r requirements.txt
```

## 📝 Buenas Prácticas

1. ✅ **SIEMPRE** activa el entorno virtual antes de trabajar
2. ✅ Usa `pip list` para verificar qué está instalado
3. ✅ Mantén actualizado el `requirements.txt`
4. ✅ No modifiques archivos dentro de `venv/`
5. ✅ Agrega `venv/` al `.gitignore` (ya está incluido)
6. ✅ Desactiva el venv cuando termines de trabajar

## 🎯 Resumen Rápido

```bash
# Iniciar trabajo
source venv/bin/activate          # Activar venv
pip list                          # Verificar paquetes
python manage.py runserver        # Ejecutar servidor

# Terminar trabajo
deactivate                        # Desactivar venv
```

---

**Recuerda:** El entorno virtual mantiene tu proyecto aislado y evita conflictos con otros proyectos Python en tu sistema. ¡Úsalo siempre! 🚀
