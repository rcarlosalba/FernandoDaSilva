/**
 * Sistema de Mensajes Toast para Django
 * Maneja la visualización, animación y eliminación automática de mensajes
 */

class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
        this.toasts = [];
        this.defaultDuration = 4000; // 4 segundos
        this.init();
    }

    /**
     * Inicializa el sistema de toasts
     */
    init() {
        if (!this.container) return;

        // Configurar colores de borde según el tipo de mensaje
        this.setupToastStyles();
        
        // Mostrar toasts existentes
        this.showExistingToasts();
        
        // Configurar event listeners para botones de cerrar
        this.setupCloseButtons();
    }

    /**
     * Configura los estilos de borde según el tipo de mensaje
     */
    setupToastStyles() {
        const toastMessages = document.querySelectorAll('.toast-message');
        
        toastMessages.forEach(toast => {
            const messageType = toast.dataset.messageType;
            const progressBar = toast.querySelector('.toast-progress-bar');
            
            // Configurar color de borde y barra de progreso según el tipo
            switch (messageType) {
                case 'success':
                    toast.classList.add('border-green-500');
                    if (progressBar) progressBar.classList.add('bg-green-500');
                    break;
                case 'error':
                    toast.classList.add('border-red-500');
                    if (progressBar) progressBar.classList.add('bg-red-500');
                    break;
                case 'warning':
                    toast.classList.add('border-yellow-500');
                    if (progressBar) progressBar.classList.add('bg-yellow-500');
                    break;
                case 'info':
                    toast.classList.add('border-blue-500');
                    if (progressBar) progressBar.classList.add('bg-blue-500');
                    break;
                default:
                    toast.classList.add('border-gray-500');
                    if (progressBar) progressBar.classList.add('bg-gray-500');
                    break;
            }
        });
    }

    /**
     * Muestra los toasts existentes con animación
     */
    showExistingToasts() {
        const toastMessages = document.querySelectorAll('.toast-message');
        
        toastMessages.forEach((toast, index) => {
            // Pequeño delay para crear efecto cascada
            setTimeout(() => {
                this.showToast(toast);
            }, index * 100);
        });
    }

    /**
     * Configura los event listeners para los botones de cerrar
     */
    setupCloseButtons() {
        const closeButtons = document.querySelectorAll('.toast-close-btn');
        
        closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const toastId = button.dataset.toastId;
                const toast = document.getElementById(`toast-${toastId}`);
                if (toast) {
                    this.hideToast(toast);
                }
            });
        });
    }

    /**
     * Muestra un toast con animación
     * @param {HTMLElement} toast - Elemento del toast
     */
    showToast(toast) {
        if (!toast) return;

        // Remover clase de transformación para mostrar
        toast.classList.remove('translate-x-full');
        toast.classList.add('translate-x-0');

        // Iniciar temporizador de auto-eliminación
        this.startAutoHideTimer(toast);
        
        // Iniciar animación de la barra de progreso
        this.startProgressBar(toast);
    }

    /**
     * Oculta un toast con animación
     * @param {HTMLElement} toast - Elemento del toast
     */
    hideToast(toast) {
        if (!toast) return;

        // Añadir clase de transformación para ocultar
        toast.classList.remove('translate-x-0');
        toast.classList.add('translate-x-full');

        // Eliminar el toast después de la animación
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    /**
     * Inicia el temporizador para auto-ocultar el toast
     * @param {HTMLElement} toast - Elemento del toast
     */
    startAutoHideTimer(toast) {
        const messageType = toast.dataset.messageType;
        
        // Los mensajes de error no se auto-ocultan
        if (messageType === 'error') return;

        setTimeout(() => {
            this.hideToast(toast);
        }, this.defaultDuration);
    }

    /**
     * Inicia la animación de la barra de progreso
     * @param {HTMLElement} toast - Elemento del toast
     */
    startProgressBar(toast) {
        const progressBar = toast.querySelector('.toast-progress-bar');
        if (!progressBar) return;

        const messageType = toast.dataset.messageType;
        
        // Los mensajes de error no tienen barra de progreso
        if (messageType === 'error') {
            progressBar.style.display = 'none';
            return;
        }

        // Animar la barra de progreso de 100% a 0%
        setTimeout(() => {
            progressBar.style.width = '0%';
        }, 100);
    }

    /**
     * Crea y muestra un nuevo toast programáticamente
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de mensaje (success, error, warning, info)
     * @param {number} duration - Duración en milisegundos (opcional)
     */
    createToast(message, type = 'info', duration = null) {
        const toastId = Date.now();
        const toastHtml = this.generateToastHTML(message, type, toastId);
        
        // Crear elemento temporal para convertir HTML a DOM
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = toastHtml;
        const toast = tempDiv.firstElementChild;

        // Añadir al contenedor
        if (this.container) {
            this.container.appendChild(toast);
            
            // Configurar estilos
            this.setupToastStyles();
            
            // Mostrar con animación
            setTimeout(() => {
                this.showToast(toast);
            }, 100);

            // Configurar botón de cerrar
            const closeBtn = toast.querySelector('.toast-close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.hideToast(toast);
                });
            }
        }
    }

    /**
     * Genera el HTML para un toast
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de mensaje
     * @param {number} id - ID único del toast
     * @returns {string} HTML del toast
     */
    generateToastHTML(message, type, id) {
        const icons = {
            success: 'fas fa-check-circle text-green-500',
            error: 'fas fa-exclamation-circle text-red-500',
            warning: 'fas fa-exclamation-triangle text-yellow-500',
            info: 'fas fa-info-circle text-blue-500'
        };

        const borderColors = {
            success: 'border-green-500',
            error: 'border-red-500',
            warning: 'border-yellow-500',
            info: 'border-blue-500'
        };

        const progressColors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };

        const icon = icons[type] || icons.info;
        const borderColor = borderColors[type] || borderColors.info;
        const progressColor = progressColors[type] || progressColors.info;

        return `
            <div 
                id="toast-${id}" 
                class="toast-message transform translate-x-full transition-all duration-300 ease-in-out max-w-sm w-full bg-white border-l-4 shadow-lg rounded-lg overflow-hidden ${borderColor}"
                data-message-type="${type}"
                data-message-id="${id}"
                role="alert"
                aria-live="polite"
                aria-atomic="true"
            >
                <div class="flex items-start p-4">
                    <div class="flex-shrink-0 mr-3">
                        <i class="${icon} text-lg"></i>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900">${message}</p>
                    </div>
                    <div class="flex-shrink-0 ml-3">
                        <button 
                            type="button"
                            class="toast-close-btn inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 transition-colors duration-200"
                            aria-label="Cerrar mensaje"
                            data-toast-id="${id}"
                        >
                            <i class="fas fa-times text-sm"></i>
                        </button>
                    </div>
                </div>
                <div class="toast-progress h-1 bg-gray-200">
                    <div class="toast-progress-bar h-full ${progressColor} transition-all duration-300 ease-linear" style="width: 100%"></div>
                </div>
            </div>
        `;
    }
}

// Inicializar el sistema de toasts cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.toastManager = new ToastManager();
});

// Exponer métodos útiles globalmente
window.showToast = (message, type = 'info', duration = null) => {
    if (window.toastManager) {
        window.toastManager.createToast(message, type, duration);
    }
}; 