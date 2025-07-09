# Sistema de Mensajes Toast para Django

Este sistema proporciona una forma elegante y accesible de mostrar mensajes del framework de Django como notificaciones toast.

## Características

- ✅ **Reutilizable**: Funciona automáticamente con el sistema de mensajes de Django
- ✅ **Accesible**: Incluye atributos ARIA para lectores de pantalla
- ✅ **Responsivo**: Se adapta a diferentes tamaños de pantalla
- ✅ **Animaciones suaves**: Transiciones CSS para entrada y salida
- ✅ **Auto-eliminación**: Los mensajes se ocultan automáticamente después de 4 segundos
- ✅ **Cierre manual**: Botón X para cerrar manualmente
- ✅ **Barra de progreso**: Indicador visual del tiempo restante
- ✅ **Tipos de mensaje**: Diferentes estilos para success, error, warning, info
- ✅ **API JavaScript**: Permite crear toasts programáticamente

## Uso en Django

### 1. En las vistas (Python)

```python
from django.contrib import messages

# Mensaje de éxito
messages.success(request, "Usuario creado exitosamente.")

# Mensaje de error
messages.error(request, "Error al procesar la solicitud.")

# Mensaje de advertencia
messages.warning(request, "Los datos pueden estar desactualizados.")

# Mensaje informativo
messages.info(request, "Nueva funcionalidad disponible.")
```

### 2. En templates (HTML)

Los mensajes se muestran automáticamente en todas las páginas que heredan de `base.html`.

### 3. Programáticamente (JavaScript)

```javascript
// Mostrar un toast desde JavaScript
showToast("Operación completada", "success");

// Diferentes tipos
showToast("Error en el servidor", "error");
showToast("Actualización disponible", "warning");
showToast("Información importante", "info");

// Con duración personalizada (en milisegundos)
showToast("Mensaje temporal", "info", 2000);
```

## Tipos de Mensaje

| Tipo | Color | Icono | Auto-ocultar | Barra de progreso |
|------|-------|-------|--------------|-------------------|
| `success` | Verde | ✓ | Sí | Sí |
| `error` | Rojo | ⚠ | No | No |
| `warning` | Amarillo | ⚠ | Sí | Sí |
| `info` | Azul | ℹ | Sí | Sí |

## Comportamiento

- **Mensajes de error**: No se auto-ocultan, requieren cierre manual
- **Otros mensajes**: Se ocultan automáticamente después de 4 segundos
- **Múltiples mensajes**: Se muestran en cascada con pequeños delays
- **Responsivo**: Se adaptan al tamaño de pantalla
- **Accesible**: Compatible con lectores de pantalla

## Estructura de Archivos

```
templates/
├── base.html              # Template principal (incluye messages.html)
└── common/
    ├── messages.html      # Componente de mensajes
    └── scripts.html       # Incluye messages.js

static/
└── js/
    └── messages.js        # Lógica JavaScript del sistema
```

## Personalización

### Cambiar duración por defecto

En `static/js/messages.js`, línea 8:
```javascript
this.defaultDuration = 4000; // Cambiar a 6000 para 6 segundos
```

### Cambiar posición

En `templates/common/messages.html`, línea 2:
```html
<div id="toast-container" class="fixed top-4 right-4 z-50 space-y-2">
<!-- Cambiar a: -->
<div id="toast-container" class="fixed bottom-4 left-4 z-50 space-y-2">
```

### Añadir nuevos tipos de mensaje

1. En `templates/common/messages.html`, añadir nuevo caso en el switch de iconos
2. En `static/js/messages.js`, añadir colores en `setupToastStyles()` y `generateToastHTML()`

## Ejemplos de Uso Común

### Después de crear un registro
```python
def create_user(request):
    if form.is_valid():
        user = form.save()
        messages.success(request, f"Usuario {user.username} creado exitosamente.")
        return redirect('user_list')
    else:
        messages.error(request, "Por favor, corrija los errores en el formulario.")
```

### Después de eliminar un registro
```python
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.warning(request, f"Usuario {user.username} eliminado permanentemente.")
    return redirect('user_list')
```

### Validación de formularios
```python
def update_profile(request):
    if form.is_valid():
        form.save()
        messages.success(request, "Perfil actualizado correctamente.")
    else:
        messages.error(request, "Error al actualizar el perfil.")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
```

## Consideraciones de Accesibilidad

- ✅ Atributos `role="alert"` para lectores de pantalla
- ✅ `aria-live="polite"` para anuncios no intrusivos
- ✅ `aria-atomic="true"` para leer el mensaje completo
- ✅ Botones con `aria-label` descriptivo
- ✅ Contraste de colores adecuado
- ✅ Navegación por teclado soportada 