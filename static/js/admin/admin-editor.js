document.addEventListener('DOMContentLoaded', function() {
    // Prevenir múltiples inicializaciones
    if (window.editorInitialized) return;
    
    const editorElement = document.querySelector('#id_content');
    if (!editorElement) return;

    // Marcar como inicializado
    window.editorInitialized = true;

    // Asegurarse de que el elemento tenga una altura mínima
    editorElement.style.minHeight = '400px';

    // Adaptador personalizado para carga de imágenes
    class CustomUploadAdapter {
        constructor(loader) {
            this.loader = loader;
        }

        upload() {
            return new Promise((resolve, reject) => {
                this.loader.file.then(file => {
                    const formData = new FormData();
                    formData.append('image', file);
                    
                    fetch('/ckeditor5/image_upload/', {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        }
                    })
                    .then(response => response.json())
                    .then(response => {
                        if (response.url) {
                            resolve({ default: response.url });
                        } else {
                            reject(response.error || 'Error en la carga de imagen');
                        }
                    })
                    .catch(error => {
                        console.error('Error de carga:', error);
                        reject(error);
                    });
                });
            });
        }

        abort() {}
    }

    function CustomUploadAdapterPlugin(editor) {
        editor.plugins.get('FileRepository').createUploadAdapter = loader => {
            return new CustomUploadAdapter(loader);
        };
    }

    // Configuración del editor
    ClassicEditor
        .create(editorElement, {
            extraPlugins: [CustomUploadAdapterPlugin],
            toolbar: {
                items: [
                    'heading',
                    '|',
                    'bold',
                    'italic',
                    'link',
                    'bulletedList',
                    'numberedList',
                    'blockQuote',
                    '|',
                    'codeBlock',
                    'imageUpload',
                    'insertTable',
                    '|',
                    'undo',
                    'redo'
                ],
                shouldNotGroupWhenFull: true
            },
            codeBlock: {
                languages: [
                    { language: 'plaintext', label: 'Texto plano' },
                    { language: 'python', label: 'Python' },
                    { language: 'javascript', label: 'JavaScript' },
                    { language: 'html', label: 'HTML' },
                    { language: 'css', label: 'CSS' },
                    { language: 'django', label: 'Django/Jinja2' },
                    { language: 'sql', label: 'SQL' },
                    { language: 'bash', label: 'Bash' }
                ]
            },
            heading: {
                options: [
                    { model: 'paragraph', title: 'Párrafo', class: 'ck-heading_paragraph' },
                    { model: 'heading1', view: 'h1', title: 'Encabezado 1', class: 'ck-heading_heading1' },
                    { model: 'heading2', view: 'h2', title: 'Encabezado 2', class: 'ck-heading_heading2' },
                    { model: 'heading3', view: 'h3', title: 'Encabezado 3', class: 'ck-heading_heading3' }
                ]
            },
            image: {
                toolbar: [
                    'imageTextAlternative',
                    'imageStyle:inline',
                    'imageStyle:block',
                    'imageStyle:side'
                ],
                styles: {
                    options: ['inline', 'block', 'side']
                },
                upload: {
                    types: ['jpeg', 'png', 'gif', 'jpg', 'webp']
                }
            },
            table: {
                contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells']
            },
            // Configuración específica de altura y tamaño
            ui: {
                height: '400px',
                width: '100%'
            },
            language: 'es'
        })
        .then(editor => {
            console.log('Editor initialized successfully');
            window.editor = editor;

            // Asegurarse de que el contenedor del editor tenga la altura correcta
            const editorContainer = editor.ui.view.element;
            if (editorContainer) {
                editorContainer.style.minHeight = '400px';
                
                // Asegurarse de que el área editable tenga la altura correcta
                const editableElement = editorContainer.querySelector('.ck-editor__editable');
                if (editableElement) {
                    editableElement.style.minHeight = '350px'; // Altura menor que el contenedor para la barra de herramientas
                }
            }

            // Ajustar el estilo del contenedor principal
            const mainContainer = document.querySelector('.ck.ck-editor__main');
            if (mainContainer) {
                mainContainer.style.minHeight = '350px';
            }
        })
        .catch(error => {
            console.error('Error initializing editor:', error);
            window.editorInitialized = false;
            editorElement.style.display = 'block';
        });
});