/**
 * Book Download Form Handler
 * Handles AJAX form submission and file download
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[method="post"]');

    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;

        // Disable button and show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = 'Procesando...';

        // Get form data
        const formData = new FormData(form);

        // Send AJAX request
        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw data;
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Update UI to show success state FIRST
                showSuccessState();

                // Then trigger file download after a short delay
                setTimeout(() => {
                    window.location.href = data.download_url;
                }, 300);
            } else {
                // Show error messages
                showErrors(data.errors || { __all__: [data.error] });
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.errors) {
                showErrors(error.errors);
            } else if (error.error) {
                alert(error.error);
            } else {
                alert('Ocurrió un error. Por favor intenta nuevamente.');
            }
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        });
    });
});

/**
 * Show success state in the UI
 */
function showSuccessState() {
    const formContainer = document.getElementById('form-container');

    const successHTML = `
        <div class="text-center py-8">
            <div class="w-20 h-20 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </div>
            <h3 class="title-subsection text-success mb-4">¡Descarga exitosa!</h3>
            <p class="text-body text-neutral-700 mb-6">
                Tu capítulo 1 ya fue descargado. Revisa tu email para completar tu perfil y acceder a más contenido exclusivo.
            </p>
            <div class="bg-primary-50 rounded-lg p-4 mb-6">
                <p class="text-small text-primary-700">
                    <strong>Próximos pasos:</strong><br />
                    1. Revisa tu correo electrónico<br />
                    2. Completa tu perfil con el link recibido<br />
                    3. Accede a contenido exclusivo y recursos
                </p>
            </div>
            <a href="https://calendly.com/proffernandodasilva/30min" class="btn-primary bg-primary-300 text-white rounded-lg hover:bg-primary-400 transition-colors duration-300 inline-block">
                Agenda una consulta gratuita
            </a>
        </div>
    `;

    formContainer.innerHTML = successHTML;
}

/**
 * Show form errors
 */
function showErrors(errors) {
    // Clear previous errors
    document.querySelectorAll('.text-danger').forEach(el => el.remove());

    // Show new errors
    for (const [field, messages] of Object.entries(errors)) {
        if (field === 'email') {
            const emailInput = document.querySelector('input[type="email"]');
            if (emailInput) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'mt-2';
                messages.forEach(msg => {
                    const errorP = document.createElement('p');
                    errorP.className = 'text-small text-danger';
                    errorP.textContent = msg;
                    errorDiv.appendChild(errorP);
                });
                emailInput.parentElement.parentElement.appendChild(errorDiv);
            }
        } else {
            // General errors
            const firstError = Array.isArray(messages) ? messages[0] : messages;
            alert(firstError);
        }
    }
}
