document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('factura-form');
    const previewContainer = document.getElementById('preview-container');
    const previewFrame = document.getElementById('pdf-preview');
    const downloadLink = document.getElementById('download-link');
    const errorBox = document.getElementById('preview-error');

    if (!form) {
        return;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        errorBox.style.display = 'none';
        errorBox.textContent = '';

        const facturaId = form.id_factura.value.trim();
        if (!facturaId) {
            errorBox.textContent = 'Por favor ingrese un ID de factura válido.';
            errorBox.style.display = 'block';
            previewContainer.style.display = 'none';
            return;
        }

        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                let message = `Error ${response.status}: no se pudo generar la factura.`;
                try {
                    const text = await response.text();
                    if (text) {
                        message += ` ${text}`;
                    }
                } catch (_) {
                }
                errorBox.textContent = message;
                errorBox.style.display = 'block';
                previewContainer.style.display = 'none';
                return;
            }

            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            previewFrame.src = blobUrl;
            downloadLink.href = blobUrl;
            downloadLink.download = `factura_${facturaId}.pdf`;
            previewContainer.style.display = 'block';
        } catch (error) {
            errorBox.textContent = 'Error de conexión con el servidor. Intenta nuevamente.';
            errorBox.style.display = 'block';
            previewContainer.style.display = 'none';
        }
    });
});

