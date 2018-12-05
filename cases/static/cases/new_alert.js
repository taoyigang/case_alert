$( document ).ready(function() {
    $('#id_comment').addClass('form-control')
    $('#id_deadline').addClass('form-control')
    $('#id_deadline').datetimepicker({
        format : 'YYYY-MM-DD HH:mm',
        sideBySide: true
    });
});
