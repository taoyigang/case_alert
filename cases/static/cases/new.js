$( document ).ready(function() {
    $('#id_alert_date').addClass('form-control')
    $('#id_file_id').addClass('form-control')
    $('#id_alert_date').datetimepicker({
        format : 'YYYY-MM-DD'
    });
});

