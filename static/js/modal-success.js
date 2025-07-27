// Muestra el modal de éxito con el mensaje recibido y, opcionalmente, una URL de redirección
function showModalSuccess(message, redirectUrl = null) {
  const modal = document.getElementById('modal-success');
  const content = document.getElementById('modal-success-content');
  if (modal && content) {
    content.innerHTML = message;
    modal.classList.remove('hidden');
    // Guardar la URL de redirección en el modal
    modal.setAttribute('data-redirect-url', redirectUrl || '');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const closeBtn = document.getElementById('close-modal-success');
  const modal = document.getElementById('modal-success');
  if (closeBtn && modal) {
    closeBtn.addEventListener('click', function() {
      const redirectUrl = modal.getAttribute('data-redirect-url');
      modal.classList.add('hidden');
      if (redirectUrl) {
        window.location.href = redirectUrl;
      }
    });
  }
}); 