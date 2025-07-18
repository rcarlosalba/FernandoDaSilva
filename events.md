# Eventos del Proyecto FDS

## 2024 - Resolución de Conflictos en Django ORM

### Problema: AttributeError en Categorías de Eventos
**Fecha**: Diciembre 2024  
**Problema**: Error `AttributeError: property 'event_count' of 'Category' object has no setter` al intentar crear categorías de eventos.

**Diagnóstico**:
- Conflicto entre la propiedad `@property event_count` en el modelo `Category` y las anotaciones de Django ORM que intentaban asignar el mismo nombre
- Django ORM intentaba asignar el resultado de `Count('events')` al atributo `event_count`, pero este estaba definido como una propiedad de solo lectura

**Solución Implementada**:
- Renombrar todas las anotaciones de `event_count` a `annotated_event_count` en las vistas
- Mantener la propiedad `event_count` en el modelo para uso directo
- Actualizar templates para usar `annotated_event_count` cuando esté disponible, con fallback a `event_count`

**Archivos Modificados**:
- `events/views.py`: Actualizadas 4 vistas para usar `annotated_event_count`
  - `category_list()`
  - `category_detail()`
  - `public_event_list()`
  - `event_statistics()`

**Resultado**: ✅ Problema resuelto - Las categorías de eventos ahora funcionan correctamente sin conflictos de nombres.

---

### Problema: TemplateDoesNotExist en Detalle de Eventos
**Fecha**: Diciembre 2024  
**Problema**: Error `TemplateDoesNotExist at /dashboard/eventos/1/` - Faltaba el template `dashboard/events/event_detail.html`.

**Diagnóstico**:
- La vista `event_detail` intentaba renderizar un template que no existía
- El template era necesario para mostrar los detalles completos de un evento en el dashboard

**Solución Implementada**:
- Crear el template `templates/dashboard/events/event_detail.html` completo
- Mantener congruencia con el diseño actual del dashboard
- Incluir toda la información del evento, estadísticas de inscripciones y lista de inscritos

**Características del Template**:
- Header con título del evento y botones de acción (Editar/Eliminar)
- Información principal del evento con imagen, descripción y badges de estado
- Layout de 2 columnas con información detallada y estadísticas
- Tabla de inscripciones con estado de pagos
- Diseño responsive con Tailwind CSS
- Iconos de Font Awesome para mejor UX

**Archivos Creados**:
- `templates/dashboard/events/event_detail.html`: Template completo de 346 líneas

**Resultado**: ✅ Problema resuelto - El detalle de eventos ahora funciona correctamente con un diseño profesional y completo.

---

### Problema: AttributeError en Inscripción de Eventos
**Fecha**: Diciembre 2024  
**Problema**: Error `AttributeError: 'User' object has no attribute 'first_name'` al intentar inscribirse a un evento.

**Diagnóstico**:
- El modelo `User` personalizado no tiene los campos `first_name` y `last_name`
- Estos campos están en el modelo `Profile` relacionado
- La vista `event_registration` intentaba acceder directamente a `request.user.first_name` y `request.user.last_name`

**Solución Implementada**:
- Modificar la vista para acceder a los campos de nombre a través del perfil del usuario
- Usar `request.user.profile.full_name` que ya existe como propiedad en el modelo Profile
- Agregar validación para verificar que el perfil existe antes de acceder a sus campos

**Archivos Modificados**:
- `events/views.py`: Corregida la función `event_registration()` para usar el perfil del usuario

**Código Corregido**:
```python
# Antes (causaba error):
'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),

# Después (funciona correctamente):
full_name = ""
if hasattr(request.user, 'profile') and request.user.profile:
    full_name = request.user.profile.full_name
```

**Resultado**: ✅ Problema resuelto - La inscripción a eventos ahora funciona correctamente para usuarios autenticados.

---

### Problema: TemplateDoesNotExist en Lista de Inscripciones
**Fecha**: Diciembre 2024  
**Problema**: Error `TemplateDoesNotExist at /dashboard/inscripciones/` - Faltaba el template `dashboard/events/registration_list.html`.

**Diagnóstico**:
- La vista `registration_list` intentaba renderizar un template que no existía
- El template era necesario para mostrar la lista de todas las inscripciones a eventos en el dashboard
- Necesitaba incluir filtros, estadísticas y funcionalidades de gestión

**Solución Implementada**:
- Crear el template `templates/dashboard/events/registration_list.html` completo
- Mantener congruencia con el diseño actual del dashboard
- Incluir todas las funcionalidades necesarias para gestionar inscripciones

**Características del Template**:
- **Header**: Título y enlace a eventos
- **Estadísticas**: 4 tarjetas con total, pendientes, aceptadas y lista de espera
- **Filtros**: Formulario con filtros por estado, evento y búsqueda de texto
- **Tabla de Inscripciones**: Lista completa con información del participante, evento, estado y pago
- **Acciones**: Botones para ver detalles, aprobar, rechazar y verificar pagos
- **Paginación**: Sistema de paginación con preservación de filtros
- **Diseño Responsive**: Adaptado para diferentes tamaños de pantalla

**Datos Mostrados**:
- Información del participante (nombre, email, teléfono)
- Evento asociado y fecha
- Estado de la inscripción (pendiente, aceptada, rechazada, lista de espera)
- Estado del pago (verificado, pendiente, fallido, sin pago)
- Fecha de inscripción
- Acciones contextuales según el estado

**Archivos Creados**:
- `templates/dashboard/events/registration_list.html`: Template completo de 275 líneas

**Resultado**: ✅ Problema resuelto - La lista de inscripciones ahora funciona correctamente con un diseño profesional y funcional completo.

---

### Problema: Campo de Notas Faltante y Sistema de Emails Pendiente
**Fecha**: Diciembre 2024  
**Problema**: 
1. El formulario de inscripción mostraba el label "Información adicional que quieras compartir (opcional)" pero no había campo para escribir
2. Los campos se "vacían" cuando hay errores de validación
3. TODO pendiente para implementar el sistema de emails de confirmación
4. Falta email de rechazo cuando se rechaza una inscripción

**Diagnóstico**:
- El modelo `Registration` tiene un campo `notes` pero el `RegistrationForm` no lo incluía
- El formulario no mantenía los datos cuando había errores de validación
- No existía sistema de emails para confirmaciones de inscripción

**Solución Implementada**:

#### 1. Campo de Notas
- Agregar el campo `notes` al `RegistrationForm` con widget de textarea
- Incluir placeholder y estilos apropiados de Tailwind CSS

#### 2. Mejora del Manejo de Formularios
- Pasar el objeto `event` al formulario para validaciones correctas
- Mejorar el manejo de errores manteniendo los datos del formulario

#### 3. Sistema de Emails Completo
- **Templates de Email**: Crear 4 templates profesionales con diseño responsive
  - `registration_confirmation.html`: Confirmación de recepción
  - `registration_approved.html`: Notificación de aprobación
  - `registration_rejected.html`: Notificación de rechazo (amable)
  - `event_reminder.html`: Recordatorio 24h antes del evento

- **Funciones de Email**: Implementar sistema completo en `events/utils.py`
  - `send_registration_confirmation_email()`: Email inicial
  - `send_registration_approved_email()`: Email de aprobación
  - `send_registration_rejected_email()`: Email de rechazo (amable)
  - `send_event_reminder_email()`: Recordatorio del evento
  - `send_waitlist_notification_email()`: Notificación de cupo liberado
  - `schedule_event_reminders()`: Función para programar recordatorios

- **Integración en Vistas**: Actualizar vistas para enviar emails automáticamente
  - `event_registration()`: Envía confirmación al inscribirse
  - `registration_approve()`: Envía notificación de aprobación
  - `registration_reject()`: Envía notificación de rechazo (amable)
  - `payment_verify()`: Envía aprobación cuando se verifica pago

**Características del Sistema de Emails**:
- **Diseño Profesional**: Templates con CSS inline para compatibilidad
- **Información Completa**: Detalles del evento, estado, próximos pasos
- **Personalización**: Diferentes contenidos según tipo de evento (online/presencial)
- **Manejo de Errores**: Try/catch para no fallar la funcionalidad principal
- **Responsive**: Emails que se ven bien en móviles y desktop

**Archivos Creados/Modificados**:
- `events/forms.py`: Agregado campo `notes` al formulario
- `events/utils.py`: Sistema completo de emails (nuevo archivo)
- `templates/events/emails/registration_confirmation.html`: Template de confirmación
- `templates/events/emails/registration_approved.html`: Template de aprobación
- `templates/events/emails/event_reminder.html`: Template de recordatorio
- `events/views.py`: Integración de emails en las vistas

**Resultado**: ✅ Problema resuelto - Sistema completo de inscripciones con emails automáticos y campo de notas funcional.

---

### Problema: Lógica Incorrecta de Lista de Espera
**Fecha**: Diciembre 2024  
**Problema**: El estado "En Lista de Espera" no se asignaba correctamente porque la lógica de `is_full` solo consideraba inscripciones aceptadas, no las pendientes.

**Diagnóstico**:
- La propiedad `is_full` del modelo `Event` solo contaba inscripciones con estado `'accepted'`
- Esto causaba que las primeras inscripciones fueran `'pending'` en lugar de `'waitlist'` cuando el evento estaba lleno
- Solo cuando ya había 20 inscripciones aceptadas, las siguientes iban a lista de espera
- La propiedad `available_spots` tenía el mismo problema

**Solución Implementada**:
- **Corregir lógica de `is_full`**: Ahora considera inscripciones `'accepted'` y `'pending'` como activas
- **Corregir lógica de `available_spots`**: Calcula cupos disponibles basándose en inscripciones activas
- **Nueva propiedad `active_registrations_count`**: Para mostrar el total de inscripciones activas
- **Actualizar templates**: Mostrar información más clara sobre cupos y inscripciones activas

**Código Corregido**:
```python
@property
def is_full(self):
    """Verifica si el evento está lleno."""
    # Contar inscripciones aceptadas y pendientes (excluyendo rechazadas y waitlist)
    active_registrations = self.registrations.filter(
        status__in=['accepted', 'pending']
    ).count()
    return active_registrations >= self.max_capacity

@property
def available_spots(self):
    """Retorna el número de cupos disponibles."""
    # Contar inscripciones aceptadas y pendientes (excluyendo rechazadas y waitlist)
    active_registrations = self.registrations.filter(
        status__in=['accepted', 'pending']
    ).count()
    return max(0, self.max_capacity - active_registrations)

@property
def active_registrations_count(self):
    """Retorna el número total de inscripciones activas (aceptadas + pendientes)."""
    return self.registrations.filter(
        status__in=['accepted', 'pending']
    ).count()
```

**Archivos Modificados**:
- `events/models.py`: Corregidas las propiedades `is_full` y `available_spots`, agregada `active_registrations_count`
- `templates/dashboard/events/registration_detail.html`: Agregada información de inscripciones activas
- `templates/dashboard/events/event_list.html`: Mostrar número de inscripciones activas

**Resultado**: ✅ Problema resuelto - La lista de espera ahora funciona correctamente cuando el evento está lleno.

---

### Problema: Email de Rechazo de Inscripción
**Fecha**: Diciembre 2024  
**Problema**: Cuando se rechaza una inscripción a un evento, no se envía ningún email al participante para notificarle la decisión.

**Diagnóstico**:
- La vista `registration_reject()` solo cambiaba el estado de la inscripción
- No había sistema de notificación por email para rechazos
- Los participantes quedaban sin saber por qué no se aprobó su inscripción

**Solución Implementada**:

#### 1. Template de Email de Rechazo
- Crear `templates/events/emails/registration_rejected.html` con diseño profesional
- **Características del Email**:
  - Mensaje amable y empático
  - Información detallada del evento rechazado
  - Explicación de posibles razones del rechazo
  - Invitación a futuros eventos
  - Información de contacto para consultas
  - Diseño responsive y profesional

#### 2. Función de Envío
- Agregar configuración en `events/utils.py`:
  - Nuevo tipo de email: `'registration_rejected'`
  - Template: `'events/emails/registration_rejected.html'`
  - Asunto: `'Inscripción No Aprobada - {event.title}'`

- Crear función `send_registration_rejected_email(registration)`:
  - Utiliza el sistema genérico de emails existente
  - Manejo de errores sin fallar el proceso de rechazo

#### 3. Integración en la Vista
- Actualizar `registration_reject()` en `events/views.py`:
  - Importar la nueva función de email
  - Enviar email automáticamente al rechazar
  - Manejo de errores para no fallar el rechazo

**Características del Email de Rechazo**:
- **Tono Empático**: Mensaje amable que no desanima al participante
- **Información Clara**: Detalles del evento y posibles razones del rechazo
- **Orientación Futura**: Invitación a próximos eventos
- **Contacto**: Información para consultas y aclaraciones
- **Diseño Profesional**: Consistente con otros emails del sistema

**Archivos Creados/Modificados**:
- `templates/events/emails/registration_rejected.html`: Template completo de email de rechazo
- `events/utils.py`: Agregada configuración y función de envío
- `events/views.py`: Integrado envío automático en vista de rechazo
- `events.md`: Documentación actualizada

**Resultado**: ✅ Problema resuelto - Ahora se envía un email amable y profesional cuando se rechaza una inscripción, mejorando la experiencia del usuario y la comunicación.

---

### Problema: TemplateDoesNotExist en Detalle de Inscripción
**Fecha**: Diciembre 2024  
**Problema**: Error `TemplateDoesNotExist at /dashboard/inscripciones/1/` - Faltaba el template `dashboard/events/registration_detail.html`.

**Diagnóstico**:
- La vista `registration_detail` intentaba renderizar un template que no existía
- El template era necesario para mostrar los detalles completos de una inscripción
- Necesitaba incluir botones de acción para aprobar o rechazar inscripciones pendientes
- También requería funcionalidad para verificar pagos cuando correspondiera

**Solución Implementada**:
- Crear el template `templates/dashboard/events/registration_detail.html` completo
- Mantener congruencia con el diseño actual del dashboard
- Incluir todas las funcionalidades necesarias para gestionar inscripciones individuales

**Características del Template**:
- **Header**: Título con ID de inscripción y botón de volver
- **Información Principal**: Datos del participante con badges de estado
- **Layout de 2 Columnas**: Información personal y estado de la inscripción
- **Información del Evento**: Enlace al evento, fechas, modalidad y precio
- **Estado de Pago**: Detalles completos del pago si existe (método, monto, estado, verificación)
- **Botones de Acción**: 
  - Aprobar inscripción (solo para estado 'pending')
  - Rechazar inscripción (solo para estado 'pending')
  - Verificar pago (solo para pagos pendientes)
- **Panel Lateral**: Resumen del evento con información general y cupos
- **Diseño Responsive**: Adaptado para diferentes tamaños de pantalla

**Funcionalidades Implementadas**:
- **Estados Visuales**: Badges de colores para diferentes estados de inscripción
- **Acciones Contextuales**: Botones que aparecen según el estado actual
- **Información de Pago**: Sección completa con detalles de verificación
- **Navegación**: Enlaces al evento y lista de inscripciones
- **Validación Visual**: Indicadores claros del estado actual

**Datos Mostrados**:
- Información personal del participante (nombre, email, teléfono)
- Detalles del evento asociado
- Estado actual de la inscripción
- Información completa del pago (si aplica)
- Notas adicionales del participante
- Fechas de inscripción y verificación

**Archivos Creados**:
- `templates/dashboard/events/registration_detail.html`: Template completo de 284 líneas

**Resultado**: ✅ Problema resuelto - El detalle de inscripciones ahora funciona correctamente con botones de acción para aprobar/rechazar y verificar pagos.

--- 