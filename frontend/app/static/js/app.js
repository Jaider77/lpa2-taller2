document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('factura-form');
    const previewContainer = document.getElementById('preview-container');
    const previewFrame = document.getElementById('pdf-preview');
    const downloadLink = document.getElementById('download-link');
    const errorBox = document.getElementById('preview-error');
    const successBox = document.getElementById('preview-success');
    const printBtn = document.getElementById('print-btn');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    var pdfBlob = null;
    var pdfUrl = null;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        errorBox.style.display = 'none';
        successBox.style.display = 'none';
        previewContainer.style.display = 'none';

        var facturaId = document.getElementById('id_factura').value.trim();
        
        if (!facturaId) {
            mostrarError('Por favor ingrese un ID de factura valido');
            return;
        }

        // Mostrar que está cargando
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generando...';

        var formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Factura no encontrada');
            }
            return response.blob();
        })
        .then(function(blob) {
            if (blob.size === 0) {
                throw new Error('El PDF esta vacio');
            }

            pdfBlob = blob;
            pdfUrl = URL.createObjectURL(blob);
            
            // Limpiar iframe anterior
            previewFrame.src = '';
            
            // Esperar un poco para asegurar que se limpie
            setTimeout(function() {
                // Cargar el PDF en el iframe
                previewFrame.src = pdfUrl;
                
                // Configurar enlace de descarga
                downloadLink.href = pdfUrl;
                downloadLink.download = 'factura_' + facturaId + '.pdf';
                
                // Mostrar contenedor de vista previa
                previewContainer.style.display = 'block';
                
                // Mostrar mensaje de exito
                mostrarExito('Factura "' + facturaId + '" generada exitosamente. Vista previa cargada.');
                
                // Scroll a la vista previa
                setTimeout(function() {
                    previewContainer.scrollIntoView({ behavior: 'smooth' });
                }, 500);
            }, 100);
        })
        .catch(function(error) {
            mostrarError(error.message || 'Error al generar la factura');
        })
        .finally(function() {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generar PDF';
        });
    });

    printBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (previewFrame.src && pdfUrl) {
            try {
                previewFrame.contentWindow.print();
            } catch(err) {
                window.print();
            }
        } else {
            mostrarError('Por favor genere una factura primero');
        }
    });

    downloadLink.addEventListener('click', function(e) {
        if (!pdfUrl) {
            e.preventDefault();
            mostrarError('Por favor genere una factura primero');
        }
    });

    function mostrarError(msg) {
        errorBox.textContent = msg;
        errorBox.style.display = 'block';
        setTimeout(function() {
            errorBox.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }

    function mostrarExito(msg) {
        successBox.textContent = msg;
        successBox.style.display = 'block';
    }
});
