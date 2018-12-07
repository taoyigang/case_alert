$( document ).ready(function() {
    $('.datepicker input').each(function(index, ele) {
        $(this).datetimepicker({
            format : 'YYYY-MM-DD'
        });
    });
});
