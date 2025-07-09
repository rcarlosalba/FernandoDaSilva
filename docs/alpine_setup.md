# Configuración de Alpine.js

## Descripción
Alpine.js ha sido configurado para servir localmente en el proyecto FDS, siguiendo las mismas prácticas que Font Awesome.

## Archivos
- **Ubicación**: `static/js/alpine.min.js`
- **Versión**: 3.13.5 (última versión estable)
- **Tamaño**: ~43KB

## Inclusión
Alpine.js se incluye automáticamente en todas las páginas a través del archivo `templates/common/scripts.html`:

```html
<script src="{% static 'js/alpine.min.js' %}"></script>
```

## Uso
Alpine.js está disponible globalmente como `Alpine` y se inicializa automáticamente cuando se carga la página.

### Ejemplo básico:
```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">
        Contenido que se muestra/oculta
    </div>
</div>
```

## Ventajas de servir localmente
1. **Rendimiento**: No depende de CDNs externos
2. **Confiabilidad**: Funciona sin conexión a internet
3. **Control**: Versión específica y estable
4. **Privacidad**: No hay tracking externo

## Actualización
Para actualizar a una nueva versión de Alpine.js:

1. Descargar la nueva versión desde: https://unpkg.com/alpinejs@[version]/dist/cdn.min.js
2. Reemplazar el archivo `static/js/alpine.min.js`
3. Actualizar esta documentación con la nueva versión

## Referencias
- [Documentación oficial de Alpine.js](https://alpinejs.dev/)
- [Guía de instalación](https://alpinejs.dev/essentials/installation) 