$(function() {

  // page is now ready, initialize the calendar...

  $('#calendar').fullCalendar({
      events: function(start, end, timezone, callback) {
        $.ajax({
          url: '/api/get_case_and_alert',
          dataType: 'json',
          data: {
            start: start.format('YYYY-MM-DD'),
            end: end.format('YYYY-MM-DD')
          },
          success: function(response) {
            var events = [];
            var case_options = {}
            var case_id = ''
            var id = ''
            Object.keys(response).forEach(function(key) {
              if ('deadline' in response[key]) {
                events.push({
                  title: response[key]['title'],
                  start: response[key]['start'],
                  color: response[key]['color'],
                  id: response[key]['id'],
                  case_id: response[key]['case_id'],
                  deadline: response[key]['deadline'],
                });
              }
              else {
                events.push({
                  title: response[key]['title'],
                  start: response[key]['start'],
                  color: response[key]['color'],
                  id: response[key]['id'],
                  case_id: response[key]['case_id'],
                });
              }
              case_id = response[key]['case_id']
              id = response[key]['id']
              if (!(case_id in case_options)){
                case_options[case_id]=id
              }
            });
            callback(events);
            for (var case_key in case_options) {
              if (case_options.hasOwnProperty(case_key)) {
                $("#case_selector").append(new Option(case_key, case_options[case_key]));
              }
            }
          }
        });
      },
    eventRender: function(event, element){
      if ('deadline' in event) {
        element.popover({
          animation:true,
          delay: 300,
          content: 'deadline:'+event.deadline,
          trigger: 'hover'
        });
      }
      return ['all', event.id].indexOf($('#case_selector').val()) >= 0
    }
  })

  $('#case_selector').on('change',function(){
    $('#calendar').fullCalendar('rerenderEvents');
  })
});

