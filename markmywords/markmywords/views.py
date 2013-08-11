from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from goals.models import Goal
from datetime import datetime, date, time, timedelta

from django.utils import simplejson 
import requests
import urllib

import unicodedata
import pdb
import paypalrestsdk
import logging

from django.core.mail import send_mail

API_AUTHORIZATION_URL = 'https://runkeeper.com/apps/authorize'
API_DEAUTHORIZATION_URL = 'https://runkeeper.com/apps/de-authorize'
API_ACCESS_TOKEN_URL = 'https://runkeeper.com/apps/token'

client_id = 'fde6b0c09d464fa2a9155118dbb0d6da'
client_secret = '3d397e2bfb054a48a876e0dc5596dab1'
redirect_uri = 'http://127.0.0.1:8000/'
API_URL = 'https://api.runkeeper.com/fitnessActivities'


logging.basicConfig(level=logging.INFO)

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AWs7BhBcB_vM9tUa-Y-i_kc6hvWL59rKhTU_Y4ozRo9EzGEXicjdoc2VDT3U",
  "client_secret": "ELE7XxC9-Zvm4kU0_h0xj_Nqhk3CelUQhJTeYwCEQ5s02iJkZHbCgD9N_9l1" })


def authorize(request, uri):
	payload = {'response_type': 'code',
		'client_id': 'fde6b0c09d464fa2a9155118dbb0d6da',
		'redirect_uri': uri,
		'state': 2}
	
	print (urllib.urlencode(payload))
	return HttpResponseRedirect("%s?%s" % (API_AUTHORIZATION_URL, 
		urllib.urlencode(payload)))

def paypal(request):
	amount = int(normalize_arg(request.GET['amt']))
	distance = int(normalize_arg(request.GET['distance']))

	goal = Goal(distance=distance, created_date=datetime.now(),
		end_date=(timedelta(days=7) + datetime.now()), money=amount,
		charity_ppid=70)
	goal.save()

	return create_paypal_payment(amount, goal.id)


def index(request):
	t = get_template('index.html')
	html = t.render(Context({}))
	return HttpResponse(html)


def goals(request, goal_id):
	goal_id = int(normalize_arg(goal_id))

	if 'code' in request.GET:
		code = request.GET['code']
		code = normalize_arg(code)
		state = request.GET['state']
		
		redirect = '%sgoal/%d' % (redirect_uri, goal_id)
		access_token = get_access_token(request, code, redirect)
		goal = Goal.objects.get(id=goal_id)
		json_object=get_workouts_in_time(request, access_token, goal)
		total_miles=get_total_miles(json_object)
		paths=[]
		paths.append(get_points_from_path(get_specific_path(request,access_token, "/223098561")))
		t = get_template('go.html')
		html=t.render(Context({'miles_goal': goal.distance/1600,
		 "current_progress": total_miles, 'pledge_amount':goal.money, 
		 "avg_speed":0, "distance":3000, "time_left":2, 
		 "percent_completed":get_total_miles(json_object)/goal.distance*100/1600,
		 "paths":simplejson.dumps(paths)}))
		return HttpResponse(html)
	else:
		return authorize(request, '%sgoal/%d' % (redirect_uri, goal_id))

def normalize_arg(arg):
	return unicodedata.normalize('NFKD', arg).encode('ascii','ignore')

def get_access_token(request, code, redirect):
	payload = {'grant_type': 'authorization_code',
		'code': code,
		'client_id': client_id,
		'client_secret': client_secret,
		'redirect_uri': redirect}
	
	req = requests.post(API_ACCESS_TOKEN_URL, data=payload)
	data = req.json()
	return data.get('access_token')


def get_specific_path(request,token, specific_workout):
	payload = {'access_token': token,}
	headers = {'Authorization': "Bearer %s" % token,
				'Accept': 'application/vnd.com.runkeeper.FitnessActivity+json'}
	response=requests.get(API_URL+specific_workout, headers=headers).json()['path']
	return response

def get_all_workouts(request, token):
	payload = {'access_token': token,}
	headers = {'Authorization': "Bearer %s" % token,
				'Accept': 'application/vnd.com.runkeeper.FitnessActivityFeed+json'}

	response=requests.get(API_URL, headers=headers).json().get('items')
	return response

def get_workouts_in_time(request, token, goal):
	token = normalize_arg(token)

	start_param = date_to_param(goal.created_date)
	end_param = date_to_param(goal.end_date)

	payload = {'access_token': token,
		'noEarlierThan': start_param,
		'noLaterThan': end_param}
	headers = {'Authorization': "Bearer %s" % token,
		'Accept': 'application/vnd.com.runkeeper.FitnessActivityFeed+json',
		'If-Modified-Since': 'Sun, 1 Jan 2012 00:00:00 GMT'}

	response = requests.get('%s?noEarlierThan=%s&noLaterThan=%s' % (API_URL, start_param, end_param),
	 headers=headers, data=payload).json().get('items')
	return response

def get_total_calories(json_object):
	return sum([item['total_calories'] for item in json_object])

def get_total_miles(json_object):
	return sum([item['total_distance'] for item in json_object])


def get_points_from_path(path):
	return [[point['longitude'], point['latitude'], point['timestamp']] for point in path]


def send_email():
	send_mail('Subject here', 'Here is the message.', 'from@example.com', ['amni2015@example.com'], fail_silently=False)

def date_to_param(date):
	return '%d-%d-%d' % (date.year, date.month, date.day)

def create_paypal_payment(amount, goal_id):
	payment = paypalrestsdk.Payment({
	  "intent":  "sale",

	  # ###Payer
	  # A resource representing a Payer that funds a payment
	  # Payment Method as 'paypal'
	  "payer":  {
	    "payment_method":  "paypal" },

	  # ###Redirect URLs
	  "redirect_urls": {
	    "return_url": "http://127.0.0.1:8000/goal/%d" % goal_id,
	    "cancel_url": "http://localhost:3000/" },

	  # ###Transaction
	  # A transaction defines the contract of a
	  # payment - what is the payment for and who
	  # is fulfilling it.
	  "transactions":  [ {

	    # ### ItemList
	    "item_list": {
	      "items": [{
	        "name": "item",
	        "sku": "item",
	        "price": amount,
	        "currency": "USD",
	        "quantity": 1 }]},

	    # ###Amount
	    # Let's you specify a payment amount.
	    "amount":  {
	      "total":  amount,
	      "currency":  "USD" },
	    "description":  "This is the payment transaction description." } ] } )

	# Create Payment and return status
	if payment.create():
	  print("Payment[%s] created successfully"%(payment.id))
	  # Redirect the user to given approval url
	  for link in payment.links:
	    if link.method == "REDIRECT":
	      redirect_url = link.href
	      print("Redirect for approval: %s" % (redirect_url))
	      return HttpResponseRedirect(redirect_url)
	else:
	  print("Error while creating payment:")
	  print(payment.error)



