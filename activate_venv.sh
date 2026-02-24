#!/bin/bash
# Script para activar el entorno virtual de CrediFlow

# Verificar que estamos en el directorio correcto
if [ ! -d "venv" ]; then
    echo "❌ Error: No se encuentra el directorio 'venv'"
    echo "Asegúrate de estar en el directorio del proyecto CrediFlow"
    exit 1
fi

# Activar el entorno virtual
source venv/bin/activate

# Verificar que se activó correctamente
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Entorno virtual activado correctamente"
    echo "📍 Ubicación: $VIRTUAL_ENV"
    echo ""
    echo "Paquetes instalados:"
    pip list
    echo ""
    echo "Para desactivar el entorno virtual, ejecuta: deactivate"
else
    echo "❌ Error: No se pudo activar el entorno virtual"
    exit 1
fi
