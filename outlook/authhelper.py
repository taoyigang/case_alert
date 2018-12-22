from urllib import urlencode
import requests
import json
import time
from Crypto.Cipher import AES
import base64
from django.conf import settings
from .models import OutlookKey

# Client ID and secret
# client_id = '3172f6d9-7786-4410-a7a8-46625cd43e74'
# client_secret = 'fhxVI4_ufglUSIVS6921-|%'

# Constant strings for OAuth2 flow
# The OAuth authority
authority = 'https://login.microsoftonline.com'

# The authorize URL that initiates the OAuth2 client credential flow for admin consent
authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

# The scopes required by the app
scopes = [ 'openid',
		   'offline_access',
		   'User.Read',
		   'Calendars.ReadWrite']


def encrypt_val(clear_text):
	enc_secret = AES.new(settings.SECRET_KEY[:32])
	tag_string = (str(clear_text) + (AES.block_size - len(str(clear_text)) % AES.block_size) * "\0")
	cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
	return cipher_text


def decrypt_val(cipher_text):
	dec_secret = AES.new(settings.SECRET_KEY[:32])
	raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
	clear_val = raw_decrypted.decode().rstrip("\0")
	return clear_val


def get_signin_url(redirect_uri, outlook_app_id):
	# Build the query parameters for the signin url
	params = { 'client_id': outlook_app_id,
			 'redirect_uri': redirect_uri,
			 'response_type': 'code',
			 'scope': ' '.join(str(i) for i in scopes)
			}

	signin_url = authorize_url.format(urlencode(params))

	return signin_url


def get_token_from_code(auth_code, redirect_uri, outlook_app_id, outlook_app_key):
	post_data = { 'grant_type': 'authorization_code',
				'code': auth_code,
				'redirect_uri': redirect_uri,
				'scope': ' '.join(str(i) for i in scopes),
				'client_id': outlook_app_id,
				'client_secret': outlook_app_key
			  }

	r = requests.post(token_url, data = post_data)

	try:
		return r.json()
	except:
		return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)


def get_token_from_refresh_token(refresh_token, redirect_uri, outlook_app_id, outlook_app_key):
	# Build the post form for the token request
	post_data = { 'grant_type': 'refresh_token',
				'refresh_token': refresh_token,
				'redirect_uri': redirect_uri,
				'scope': ' '.join(str(i) for i in scopes),
				'client_id': outlook_app_id,
				'client_secret': outlook_app_key
			  }

	r = requests.post(token_url, data = post_data)

	try:
		return r.json()
	except:
		return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)


def get_access_token(request, redirect_uri):
	if 'access_token' not in request.session:
		outlook_key = OutlookKey.objects.filter(user=request.user, valid=True).first()
		refresh_token = outlook_key.refresh_token
		new_tokens = get_token_from_refresh_token(refresh_token, redirect_uri, outlook_key.outlook_app_id,
		                                          outlook_key.outlook_app_key)
		# Update session
		# expires_in is in seconds
		# Get current timestamp (seconds since Unix Epoch) and
		# add expires_in to get expiration time
		# Subtract 5 minutes to allow for clock differences
		expiration = int(time.time()) + new_tokens['expires_in'] - 300

		# Save the token in the session
		request.session['access_token'] = new_tokens['access_token']
		request.session['refresh_token'] = new_tokens['refresh_token']
		request.session['token_expires'] = expiration
		return new_tokens['access_token']
	else:
		current_token = request.session['access_token']
		expiration = request.session['token_expires']
		now = int(time.time())
		if current_token and now < expiration:
			# Token still valid
			return current_token
		else:
			# Token expired
			outlook_key = OutlookKey.objects.filter(user=request.user, valid=True).first()
			refresh_token = request.session['refresh_token']
			new_tokens = get_token_from_refresh_token(refresh_token, redirect_uri, outlook_key.outlook_app_id,
			                                          outlook_key.outlook_app_key)
		return new_tokens['access_token']