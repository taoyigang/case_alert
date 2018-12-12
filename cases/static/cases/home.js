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

            Object.keys(response).forEach(function(key) {
              if ('deadline' in response[key]) {
                events.push({
                  title: response[key]['title'],
                  start: response[key]['start'],
                  color: response[key]['color'],
                  deadline: response[key]['deadline'],
                });
              }
              else {
                events.push({
                  title: response[key]['title'],
                  start: response[key]['start'],
                  color: response[key]['color'],
                });
              }
            });
            callback(events);
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
    }
  })
});