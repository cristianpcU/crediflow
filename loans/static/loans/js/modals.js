// Funciones para manejar modales AJAX

function openModal(url, modalId) {
    $.ajax({
        url: url,
        type: 'GET',
        success: function(data) {
            $(modalId).find('.modal-body').html(data);
            $(modalId).modal('show');
            initializeFormPlugins();
        },
        error: function(xhr) {
            console.error('Error al cargar el modal:', xhr);
            alert('Error al cargar el formulario');
        }
    });
}

function submitFormAjax(form, successCallback) {
    $.ajax({
        url: form.attr('action'),
        type: 'POST',
        data: form.serialize(),
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(response) {
            if (response.success) {
                $(form).closest('.modal').modal('hide');
                if (typeof successCallback === 'function') {
                    successCallback(response);
                } else {
                    showSuccessMessage(response.message || 'Guardado exitosamente');
                    // Recargar la página después de un breve delay
                    setTimeout(function() {
                        window.location.reload();
                    }, 500);
                }
            }
        },
        error: function(xhr) {
            if (xhr.status === 400) {
                displayFormErrors(form, xhr.responseJSON.errors);
            } else {
                alert('Error al procesar la solicitud');
            }
        }
    });
}

function initializeFormPlugins() {
    // Inicializar Select2 si existe
    if ($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap-5',
            dropdownParent: $('.modal')
        });
        
        $('.select2-multiple').select2({
            theme: 'bootstrap-5',
            dropdownParent: $('.modal'),
            multiple: true
        });
    }
}

function displayFormErrors(form, errors) {
    // Limpiar errores anteriores
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').remove();
    
    // Mostrar nuevos errores
    for (var field in errors) {
        var input = form.find('#id_' + field);
        input.addClass('is-invalid');
        var errorMsg = errors[field].join(', ');
        input.after('<div class="invalid-feedback d-block">' + errorMsg + '</div>');
    }
}

function showSuccessMessage(message) {
    // Crear y mostrar mensaje de éxito
    var alertHtml = '<div class="alert alert-success alert-dismissible fade show" role="alert">' +
                    message +
                    '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                    '</div>';
    
    // Insertar al inicio del contenido principal
    $('main').prepend(alertHtml);
    
    // Auto-cerrar después de 3 segundos
    setTimeout(function() {
        $('.alert').alert('close');
    }, 3000);
}

// Inicializar cuando el documento esté listo
$(document).ready(function() {
    // Inicializar Select2 en elementos existentes
    if ($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap-5'
        });
    }
});
