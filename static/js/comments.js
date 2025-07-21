function commentSection() {
  return {
    content: '',
    parent: '',
    originalFormParent: null,
    submitComment() {
      const formData = new FormData(this.$refs.form);
      fetch(this.$refs.form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const list = document.getElementById('comments-list');
          if (this.parent) {
            // Si es respuesta, buscar el bloque de replies del padre
            const parentComment = list.querySelector('[data-comment-id="' + this.parent + '"]');
            let parentDiv = parentComment ? parentComment.querySelector('.replies') : null;
            if (!parentDiv && parentComment) {
              // Crear el bloque de replies si no existe
              parentDiv = document.createElement('div');
              parentDiv.className = 'ml-6 mt-3 border-l-2 border-primary-100 pl-4 replies';
              parentComment.appendChild(parentDiv);
            }
            if (parentDiv) {
              parentDiv.insertAdjacentHTML('beforeend', data.html);
            }
          } else {
            list.insertAdjacentHTML('afterbegin', data.html);
          }
          this.content = '';
          this.parent = '';
          this.moveFormToRoot();
          if (window.ToastManager) {
            window.ToastManager.createToast('Comentario publicado correctamente.', 'success');
          }
        } else {
          let msg = 'Error al enviar el comentario.';
          if (data.errors) {
            msg = Object.values(data.errors).join(' ');
          }
          if (window.ToastManager) {
            window.ToastManager.createToast(msg, 'error');
          } else {
            alert(msg);
          }
        }
      })
      .catch(() => {
        if (window.ToastManager) {
          window.ToastManager.createToast('Error de red al enviar el comentario.', 'error');
        } else {
          alert('Error de red al enviar el comentario.');
        }
      });
    },
    moveFormTo(targetId) {
      const form = document.getElementById('comment-form');
      if (form) {
        form.classList.remove('hidden');
        const target = document.getElementById(targetId);
        if (target) {
          target.appendChild(form);
        }
      }
    },
    moveFormToRoot() {
      const form = document.getElementById('comment-form');
      if (form) {
        form.classList.remove('hidden');
        const root = document.getElementById('root-comment-form');
        if (root) {
          root.appendChild(form);
        }
      }
    },
    cancelReply() {
      this.parent = '';
      this.moveFormToRoot();
    },
    // Escuchar evento de respuesta
    init() {
      this.moveFormToRoot();
      this.$el.addEventListener('reply', e => {
        this.parent = e.detail.parent;
        this.moveFormTo('reply-form-' + this.parent);
        this.$refs.form.scrollIntoView({ behavior: 'smooth' });
      });
    }
  }
} 