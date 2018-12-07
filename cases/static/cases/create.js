$( document ).ready(function() {
    $('.datepicker input').each(function(index, ele) {
        $(this).datetimepicker({
            format : 'YYYY-MM-DD'
        });
    });
    $('.form-group input').addClass('form-control')
    $('.form-inline').addClass('m15');
    $('.form-inline input').addClass('form-control')
});
