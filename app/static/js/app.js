// Reusable Toast and Confirm Modal Helpers
window.showToast = function(message, type) {
    type = type || 'info';
    var bgClass = 'bg-primary';
    if (type === 'success') bgClass = 'bg-success';
    if (type === 'danger' || type === 'error') bgClass = 'bg-danger';
    if (type === 'warning') bgClass = 'bg-warning text-dark';

    var $toast = $('#appToast');
    $toast.removeClass('bg-primary bg-success bg-danger bg-warning text-dark').addClass(bgClass);
    $('#appToastBody').text(message);

    var toastInstance = bootstrap.Toast.getOrCreateInstance($toast[0]);
    toastInstance.show();
};

window.showConfirm = function(message, onConfirmCallback) {
    $('#appConfirmBody').text(message);
    var modalEl = document.getElementById('appConfirmModal');
    var modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);

    $('#appConfirmBtn').off('click').one('click', function() {
        modalInstance.hide();
        if (typeof onConfirmCallback === 'function') {
            onConfirmCallback();
        }
    });

    modalInstance.show();
};

document.addEventListener('DOMContentLoaded', function() {
    // Preserve active tab across page reloads using URL hash or localStorage
    var activeTab = localStorage.getItem('activeTab');
    if (activeTab && window.switchTab) {
        window.switchTab(activeTab);
    }

    // Initialize Persian Datepicker on elements with class .pdate
    if ($.fn.pDatepicker) {
        $('.pdate').pDatepicker({
            format: 'YYYY/MM/DD',
            autoClose: true,
            initialValue: false,
            calendar:{
                persian: {
                    locale: 'fa'
                }
            }
        });
    }

    // Modal Form Auto-Submit via AJAX if data-ajax="true"
    $(document).on('submit', 'form[data-ajax="true"]', function(e) {
        e.preventDefault();
        var $form = $(this);
        var $btn = $form.find('button[type="submit"]');
        var originalBtnText = $btn.html();

        $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال ثبت...');

        var csrfToken = $('meta[name="csrf-token"]').attr('content');

        $.ajax({
            url: $form.attr('action'),
            method: $form.attr('method') || 'POST',
            data: $form.serialize(),
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    var modalEl = $form.closest('.modal');
                    if (modalEl.length) {
                        var modalInstance = bootstrap.Modal.getInstance(modalEl[0]);
                        if (modalInstance) modalInstance.hide();
                    }
                    if (response.message) {
                        showToast(response.message, 'success');
                    }
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else if (response.open_newborn_modal) {
                        if (window.triggerNewbornModal) {
                            window.triggerNewbornModal(response.newborn_data);
                        } else {
                            window.location.reload();
                        }
                    } else {
                        window.location.reload();
                    }
                } else {
                    if (response.errors) {
                        var errorMsg = Object.values(response.errors).flat().join(' - ');
                        showToast('خطا در ثبت اطلاعات: ' + errorMsg, 'danger');
                    } else if (response.message) {
                        showToast('خطا: ' + response.message, 'danger');
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Form Error:', xhr, status, error);
                var msg = 'خطایی در ثبت اطلاعات رخ داده است.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    msg = xhr.responseJSON.message;
                }
                showToast(msg, 'danger');
            },
            complete: function() {
                $btn.prop('disabled', false).html(originalBtnText);
            }
        });
    });
});
