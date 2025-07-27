from django.contrib import admin
from .models import Category, PaymentMethod, Event, Registration, Payment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_event_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def get_event_count(self, obj):
        return obj.event_count
    get_event_count.short_description = 'Eventos'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name', 'instructions']
    ordering = ['name']


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ['registration_date']
    fields = ['full_name', 'email', 'phone', 'status', 'registration_date']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at']
    fields = ['payment_method', 'status', 'amount', 'created_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'event_type', 'modality', 'status', 'start_date',
        'max_capacity', 'available_spots', 'created_by'
    ]
    list_filter = [
        'event_type', 'modality', 'status', 'start_date',
        'categories', 'created_at'
    ]
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['categories', 'payment_methods']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'description', 'featured_image')
        }),
        ('Fechas y Horarios', {
            'fields': ('start_date', 'end_date')
        }),
        ('Configuración del Evento', {
            'fields': ('event_type', 'modality', 'price', 'max_capacity')
        }),
        ('Ubicación y Enlaces', {
            'fields': ('location', 'event_link')
        }),
        ('Clasificación', {
            'fields': ('categories', 'status', 'send_survey')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def available_spots(self, obj):
        return obj.available_spots
    available_spots.short_description = 'Cupos disponibles'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'event', 'status', 'registration_date'
    ]
    list_filter = ['status', 'registration_date', 'event']
    search_fields = ['full_name', 'email', 'event__title']
    readonly_fields = ['registration_date']
    ordering = ['-registration_date']

    fieldsets = (
        ('Información Personal', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Evento', {
            'fields': ('event', 'status', 'notes')
        }),
        ('Metadatos', {
            'fields': ('registration_date',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'registration', 'payment_method', 'status', 'amount', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'registration__full_name', 'registration__email',
        'registration__event__title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Información del Pago', {
            'fields': ('registration', 'payment_method', 'status', 'amount')
        }),
        ('Comprobante', {
            'fields': ('receipt',)
        }),
        ('Verificación', {
            'fields': ('verification_date', 'verified_by'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
