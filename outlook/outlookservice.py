import requests
import uuid
import json
from datetime import timedelta

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'


# Generic API Sending
def make_api_call(method, url, token, payload = None, parameters = None):
	# Send these headers with all API calls
	headers = { 'User-Agent' : 'python_tutorial/1.0',
	          'Authorization' : 'Bearer {0}'.format(token),
	          'Accept' : 'application/json' }

	# Use these headers to instrument calls. Makes it easier
	# to correlate requests and responses in case of problems
	# and is a recommended best practice.
	request_id = str(uuid.uuid4())
	instrumentation = {'client-request-id' : request_id,
	                   'return-client-request-id' : 'true' }

	headers.update(instrumentation)

	response = None

	if method.upper() == 'GET':
		response = requests.get(url, headers=headers, params=parameters)
	elif method.upper() == 'DELETE':
		response = requests.delete(url, headers = headers, params=parameters)
	elif method.upper() == 'PATCH':
		headers.update({'Content-Type': 'application/json'})
		response = requests.patch(url, headers=headers, data=json.dumps(payload), params=parameters)
	elif method.upper() == 'POST':
		headers.update({'Content-Type': 'application/json'})
		response = requests.post(url, headers=headers, data=json.dumps(payload), params=parameters)

	return response


def get_me(access_token):
	get_me_url = graph_endpoint.format('/me')

	# Use OData query parameters to control the results
	#  - Only return the displayName and mail fields
	query_parameters = {'$select': 'displayName,mail'}

	r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

	if (r.status_code == requests.codes.ok):
		return r.json()
	else:
		return "{0}: {1}".format(r.status_code, r.text)


def get_my_events(access_token):
	# post_events_url = graph_endpoint.format('/me/events')
	# request_body = {
	# 	"subject": "Let's go for lunch",
	# 	"body": {
	# 		"contentType": "HTML",
	# 		"content": "Does late morning work for you?"
	# 	},
	# 	"start": {
	# 		"dateTime": "2018-12-15T12:00:00",
	# 		"timeZone": "Pacific Standard Time"
	# 	},
	# 	"end": {
	# 		"dateTime": "2018-12-15T14:00:00",
	# 		"timeZone": "Pacific Standard Time"
	# 	},
	# 	"location": {
	# 		"displayName": "this is a displayname"
	# 	},
	# 	"attendees": [
	# 		{
	# 			"emailAddress": {
	# 				"address": "samanthab@contoso.onmicrosoft.com",
	# 				"name": "yigang tao"
	# 			},
	# 			"type": "required"
	# 		}
	# 	]
	# }
	#
	# r = make_api_call('POST', post_events_url, access_token, payload=request_body)
	get_events_url = graph_endpoint.format('/me/events')
	query_parameters = {'$top': '10',
	                    '$select': 'subject,start,end',
	                    '$orderby': 'start/dateTime ASC'}

	r = make_api_call('GET', get_events_url, access_token, parameters=query_parameters)

	if (r.status_code == requests.codes.ok):
		return r.json()
	else:
		return "{0}: {1}".format(r.status_code, r.text)


def post_my_event(access_token, obj, is_case=False):
	event = make_event(obj, is_case)
	post_events_url = graph_endpoint.format('/me/events')
	request_body = {
		"subject": event['subject'],
		"body": {
			"contentType": "HTML",
			"content": event["content"]
		},
		"start": {
			"dateTime": event["start_at"],
			"timeZone": "Eastern Standard Time"
		},
		"end": {
			"dateTime": event["end_at"],
			"timeZone": "Eastern Standard Time"
		},
		"location": {
			"displayName": "office"
		},
		"attendees": [

		]
	}

	make_api_call('POST', post_events_url, access_token, payload=request_body)


def make_event(obj, is_case):
	event = {
		"subject": "",
		"content": "",
		"start_at": "",
		"end_at": "",
	}
	if is_case:
		event['subject'] = obj.case_id
		event["content"] = "deadline alert for case: {}".format(obj.case_id)
		deadline_date = obj.deadline.strftime("%Y-%m-%d")
		event["start_at"] = "{}T08:30:00".format(deadline_date)
		event["end_at"] = "{}T17:30:00".format(deadline_date)
		return event
	else:
		day_diff = (obj.case.deadline - obj.alert_date).days
		if obj.comment:
			event['subject'] = "{},\n{}".format(obj.case.case_id, obj.comment)
		else:
			event['subject'] = "{},\n{} days before deadline".format(obj.case.case_id, day_diff)
		event["content"] = "case alert for case: {}".format(obj.case_id)
		alert_date = obj.alert_date.strftime("%Y-%m-%d")
		event["start_at"] = "{}T08:30:00".format(alert_date)
		event["end_at"] = "{}T17:30:00".format(alert_date)
		return event