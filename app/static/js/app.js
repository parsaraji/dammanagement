document.addEventListener('DOMContentLoaded', function() {
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

        $.ajax({
            url: $form.attr('action'),
            method: $form.attr('method') || 'POST',
            data: $form.serialize(),
            success: function(response) {
                if (response.success) {
                    var modalEl = $form.closest('.modal');
                    if (modalEl.length) {
                        var modalInstance = bootstrap.Modal.getInstance(modalEl[0]);
                        if (modalInstance) modalInstance.hide();
                    }
                    if (response.message) {
                        alert(response.message);
                    }
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else if (response.reload) {
                        window.location.reload();
                    } else if (response.open_newborn_modal) {
                        // Handle auto-opening newborn form after calving
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
                        var errorMsg = Object.values(response.errors).flat().join('\n');
                        alert('خطا در ثبت اطلاعات:\n' + errorMsg);
                    } else if (response.message) {
                        alert('خطا: ' + response.message);
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Form Error:', xhr, status, error);
                var msg = 'خطایی رخ داده است.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    msg = xhr.responseJSON.message;
                } else if (xhr.responseText) {
                    msg += '\n' + xhr.responseText.substring(0, 300);
                }
                alert(msg);
            },
            complete: function() {
                $btn.prop('disabled', false).html(originalBtnText);
            }
        });
    });
});
