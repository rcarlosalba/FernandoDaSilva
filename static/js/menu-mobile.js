document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const closeMenuButton = document.getElementById('close-menu-button');
    const offcanvasPanel = document.getElementById('offcanvas-panel');
    const offcanvasBackdrop = document.getElementById('offcanvas-backdrop');

    const openMenu = () => {
        if (!offcanvasPanel || !offcanvasBackdrop) return;
        
        // Muestra el panel y el fondo
        offcanvasPanel.classList.remove('translate-x-full');
        offcanvasBackdrop.classList.remove('hidden');
        offcanvasBackdrop.classList.add('opacity-100');
    };

    const closeMenu = () => {
        if (!offcanvasPanel || !offcanvasBackdrop) return;

        // Oculta el panel y el fondo
        offcanvasPanel.classList.add('translate-x-full');
        offcanvasBackdrop.classList.remove('opacity-100');
        setTimeout(() => {
            offcanvasBackdrop.classList.add('hidden');
        }, 300); // Coincide con la duración de la transición
    };

    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            openMenu();
        });
    }

    if (closeMenuButton) {
        closeMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            closeMenu();
        });
    }

    if (offcanvasBackdrop) {
        // Cierra el menú si se hace clic en el overlay (el fondo)
        offcanvasBackdrop.addEventListener('click', closeMenu);
    }
    
    // Smooth scroll for anchor links y cerrar menú
    document.querySelectorAll('#offcanvas-panel a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
            
            closeMenu(); // Cierra el menú primero

            if (target) {
                // Espera a que la animación de cierre del menú no interfiera con el scroll
                setTimeout(() => {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }, 350);
            }
        });
    });
});