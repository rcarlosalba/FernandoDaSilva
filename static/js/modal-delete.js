/**
 * Generic Delete Modal Component
 * Handles confirmation dialogs for delete operations
 */

class DeleteModal {
    constructor() {
        this.modal = document.getElementById('deleteModal');
        this.modalContent = document.getElementById('deleteModalContent');
        this.title = document.getElementById('deleteModalTitle');
        this.message = document.getElementById('deleteModalMessage');
        this.warning = document.getElementById('deleteModalWarning');
        this.confirmationInput = document.getElementById('deleteConfirmationInput');
        this.confirmationText = document.getElementById('confirmationText');
        this.confirmationWord = document.getElementById('confirmationWord');
        this.confirmButton = document.getElementById('confirmDeleteModal');
        this.confirmButtonText = document.getElementById('confirmDeleteText');
        this.deleteForm = document.getElementById('deleteForm');
        
        this.currentConfig = null;
        this.init();
    }
    
    init() {
        // Close modal events
        document.getElementById('closeDeleteModal').addEventListener('click', () => this.close());
        document.getElementById('cancelDeleteModal').addEventListener('click', () => this.close());
        
        // Close on backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.close();
            }
        });
        
        // Confirmation input handler
        this.confirmationText.addEventListener('input', () => this.validateConfirmation());
        
        // Confirm delete handler
        this.confirmButton.addEventListener('click', () => this.executeDelete());
        
        // Initialize delete triggers
        this.initializeTriggers();
    }
    
    /**
     * Initialize all elements with data-delete attributes
     */
    initializeTriggers() {
        document.querySelectorAll('[data-delete-url]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                this.show({
                    url: trigger.dataset.deleteUrl,
                    title: trigger.dataset.deleteTitle || 'Confirmar Eliminación',
                    message: trigger.dataset.deleteMessage || '¿Estás seguro de que deseas eliminar este elemento?',
                    warning: trigger.dataset.deleteWarning || 'Esta acción es permanente y no se puede revertir.',
                    confirmation: trigger.dataset.deleteConfirmation === 'true',
                    confirmWord: trigger.dataset.deleteConfirmWord || 'ELIMINAR',
                    buttonText: trigger.dataset.deleteButtonText || 'Eliminar'
                });
            });
        });
    }
    
    /**
     * Show the delete modal with custom configuration
     * @param {Object} config - Modal configuration
     */
    show(config) {
        this.currentConfig = config;
        
        // Set content
        this.title.textContent = config.title;
        this.message.textContent = config.message;
        this.warning.textContent = config.warning;
        this.confirmButtonText.textContent = config.buttonText;
        
        // Handle confirmation input
        if (config.confirmation) {
            this.confirmationWord.textContent = config.confirmWord;
            this.confirmationInput.classList.remove('hidden');
            this.confirmationText.value = '';
            this.confirmButton.disabled = true;
        } else {
            this.confirmationInput.classList.add('hidden');
            this.confirmButton.disabled = false;
        }
        
        // Set form action
        this.deleteForm.action = config.url;
        
        // Show modal with animation
        this.modal.classList.remove('hidden');
        
        // Trigger animation
        setTimeout(() => {
            this.modalContent.classList.remove('scale-95', 'opacity-0');
            this.modalContent.classList.add('scale-100', 'opacity-100');
        }, 10);
        
        // Focus first interactive element
        if (config.confirmation) {
            this.confirmationText.focus();
        } else {
            this.confirmButton.focus();
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Close the modal
     */
    close() {
        // Animate out
        this.modalContent.classList.remove('scale-100', 'opacity-100');
        this.modalContent.classList.add('scale-95', 'opacity-0');
        
        // Hide modal after animation
        setTimeout(() => {
            this.modal.classList.add('hidden');
            this.currentConfig = null;
            
            // Reset form
            this.deleteForm.action = '';
            this.confirmationText.value = '';
            this.confirmButton.disabled = false;
            
            // Restore body scroll
            document.body.style.overflow = '';
        }, 300);
    }
    
    /**
     * Validate confirmation text input
     */
    validateConfirmation() {
        if (!this.currentConfig?.confirmation) return;
        
        const isValid = this.confirmationText.value.trim() === this.currentConfig.confirmWord;
        this.confirmButton.disabled = !isValid;
        
        // Visual feedback
        if (this.confirmationText.value.length > 0) {
            if (isValid) {
                this.confirmationText.classList.remove('border-red-300', 'focus:border-red-300', 'focus:ring-red-300');
                this.confirmationText.classList.add('border-green-300', 'focus:border-green-300', 'focus:ring-green-300');
            } else {
                this.confirmationText.classList.remove('border-green-300', 'focus:border-green-300', 'focus:ring-green-300');
                this.confirmationText.classList.add('border-red-300', 'focus:border-red-300', 'focus:ring-red-300');
            }
        } else {
            this.confirmationText.classList.remove(
                'border-red-300', 'focus:border-red-300', 'focus:ring-red-300',
                'border-green-300', 'focus:border-green-300', 'focus:ring-green-300'
            );
        }
    }
    
    /**
     * Execute the delete action
     */
    executeDelete() {
        if (this.confirmButton.disabled) return;
        
        // Show loading state
        this.confirmButton.disabled = true;
        this.confirmButton.innerHTML = `
            <svg class="w-4 h-4 mr-2 inline animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Eliminando...
        `;
        
        // Submit the form
        this.deleteForm.submit();
    }
    
    /**
     * Reinitialize triggers (useful for dynamic content)
     */
    reinitialize() {
        this.initializeTriggers();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.deleteModal = new DeleteModal();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeleteModal;
}