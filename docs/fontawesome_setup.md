# Configuración de Font Awesome Local

Este proyecto utiliza Font Awesome servido localmente para evitar dependencias de CDN externos y mejorar el rendimiento.

## Estructura de Archivos

```
static/
├── css/
│   ├── fontawesome/
│   │   └── all.min.css          # CSS principal de Font Awesome
│   └── webfonts/
│       ├── fa-solid-900.woff2   # Fuente sólida (iconos principales)
│       ├── fa-regular-400.woff2 # Fuente regular (iconos outline)
│       └── fa-brands-400.woff2  # Fuente brands (iconos de marcas)
```

## Iconos Disponibles

### Iconos Sólidos (fas)
- `fa-bars` - Menú hamburguesa
- `fa-blog` - Blog
- `fa-check-circle` - Círculo con check
- `fa-chevron-right` - Flecha derecha
- `fa-envelope` - Sobre/email
- `fa-exclamation-circle` - Círculo con exclamación
- `fa-exclamation-triangle` - Triángulo con exclamación
- `fa-external-link-alt` - Enlace externo
- `fa-graduation-cap` - Gorro de graduación
- `fa-info-circle` - Círculo con información
- `fa-times` - X (cerrar)
- `fa-trash` - Papelera
- `fa-tachometer-alt` - Dashboard
- `fa-user-check` - Usuario verificado
- `fa-user-circle` - Usuario con círculo
- `fa-user-times` - Usuario con X
- `fa-users` - Múltiples usuarios
- `fa-users-cog` - Usuarios con engranaje

### Iconos Regulares (far)
- Disponibles para uso futuro

### Iconos de Marcas (fab)
- Disponibles para uso futuro

## Uso en Templates

### Clases Básicas
```html
<!-- Icono sólido -->
<i class="fas fa-user"></i>

<!-- Icono regular -->
<i class="far fa-user"></i>

<!-- Icono de marca -->
<i class="fab fa-github"></i>
```

### Con Tamaños
```html
<!-- Tamaños disponibles -->
<i class="fas fa-user text-sm"></i>    <!-- 14px -->
<i class="fas fa-user text-base"></i>  <!-- 16px -->
<i class="fas fa-user text-lg"></i>    <!-- 18px -->
<i class="fas fa-user text-xl"></i>    <!-- 20px -->
<i class="fas fa-user text-2xl"></i>   <!-- 24px -->
```

### Con Colores
```html
<!-- Colores de Tailwind -->
<i class="fas fa-user text-blue-500"></i>
<i class="fas fa-user text-green-500"></i>
<i class="fas fa-user text-red-500"></i>
<i class="fas fa-user text-gray-500"></i>
```

## Configuración en el Proyecto

### 1. Enlace en Head
El CSS de Font Awesome se incluye en `templates/common/head.html`:

```html
<!-- Font Awesome -->
<link rel="stylesheet" href="{% static 'css/fontawesome/all.min.css' %}">
```

### 2. Ubicación de Fuentes
Las fuentes se encuentran en `static/css/webfonts/` y el CSS las referencia con rutas relativas:

```css
@font-face {
  font-family: "Font Awesome 6 Free";
  font-weight: 900;
  src: url("../webfonts/fa-solid-900.woff2") format("woff2");
}
```

## Ventajas de la Configuración Local

✅ **Sin dependencias externas**: No depende de CDNs  
✅ **Mejor rendimiento**: Carga más rápida  
✅ **Control total**: Versión específica y estable  
✅ **Offline**: Funciona sin conexión a internet  
✅ **Seguridad**: No hay llamadas a servidores externos  

## Mantenimiento

### Agregar Nuevos Iconos
1. Identificar el código Unicode del icono en [Font Awesome](https://fontawesome.com/icons)
2. Agregar la regla CSS en `static/css/fontawesome/all.min.css`:

```css
.fa-nuevo-icono:before {
  content: "\f123";
}
```

### Actualizar Versión
1. Descargar nueva versión desde [Font Awesome](https://fontawesome.com/download)
2. Reemplazar archivos en `static/css/webfonts/`
3. Actualizar `static/css/fontawesome/all.min.css` si es necesario

## Ejemplos de Uso en el Proyecto

### Dashboard
```html
<i class="fas fa-tachometer-alt mr-3 h-5 w-5 text-primary-500"></i>
```

### Usuarios
```html
<i class="fas fa-users mr-3 h-5 w-5 text-primary-500"></i>
```

### Menú Móvil
```html
<i class="fas fa-bars text-xl"></i>
```

### Modal de Eliminación
```html
<i class="fas fa-exclamation-triangle text-white text-lg"></i>
<i class="fas fa-trash mr-2"></i>
``` 