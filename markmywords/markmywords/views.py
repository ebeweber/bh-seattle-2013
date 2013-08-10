from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseRedirect

import requests
import urllib

import unicodedata
import pdb

API_AUTHORIZATION_URL = 'https://runkeeper.com/apps/authorize'
API_DEAUTHORIZATION_URL = 'https://runkeeper.com/apps/de-authorize'
API_ACCESS_TOKEN_URL = 'https://runkeeper.com/apps/token'

client_id = 'fde6b0c09d464fa2a9155118dbb0d6da'
client_secret = '3d397e2bfb054a48a876e0dc5596dab1'
redirect_uri = 'http://127.0.0.1:8000/'

def authorize(request):
	payload = {'response_type': 'code',
		'client_id': 'fde6b0c09d464fa2a9155118dbb0d6da',
		'redirect_uri': 'http://127.0.0.1:8000/',
		'state': 2}
	
	print (urllib.urlencode(payload))
	return HttpResponseRedirect("%s?%s" % (API_AUTHORIZATION_URL, 
		urllib.urlencode(payload)))

def index(request):
	if 'code' in request.GET:
		# The user is authorized to use the app
		code = request.GET['code']
		code = normalize_arg(code)
		print(code)
		state = request.GET['state']
		
		access_token = get_access_token(request, code)
		pdb.set_trace()

		t = get_template('index.html')
		html = t.render(Context({}))
		return HttpResponse(html)
	else:
		return authorize(request)

def normalize_arg(arg):
	return unicodedata.normalize('NFKD', arg).encode('ascii','ignore')

def get_access_token(request,code):
	payload = {'grant_type': 'authorization_code',
		'code': code,
		'client_id': client_id,
		'client_secret': client_secret,
		'redirect_uri': redirect_uri,}
	
	req = requests.post(API_ACCESS_TOKEN_URL, data=payload)
	data = req.json()
	pdb.set_trace()
	return data.get('access_token')
	
