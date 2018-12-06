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
              events.push({
                title: response[key]['title'],
                start: response[key]['start'],
                color: response[key]['color']
              });
            });
            callback(events);
          }
        });
      }
  })

});