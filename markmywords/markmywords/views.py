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
BASE_URL='https://api.runkeeper.com'


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
	date = normalize_arg(request.GET['date'])
	time = datetime.strptime(date, '%d %b, %y')

	goal = Goal(distance=distance, created_date=datetime.now(),
		end_date=time, money=amount, charity_ppid=70)
	goal.save()

	return create_paypal_payment(amount, goal.id)

def ppsupport(request):
	print ("test")
	amount = int(normalize_arg(request.GET['amt']))
	distance = int(normalize_arg(request.GET['distance']))

	return create_paypal_support_payment(amount, 21)



def index(request):
	t = get_template('index.html')
	html = t.render(Context({}))
	return HttpResponse(html)

def update_goal_info(request, goal_id):
	goal_id = int(normalize_arg(goal_id))
	access_token = request.GET['access_token']
	
	redirect = '%sgoal/%d' % (redirect_uri, goal_id)
	goal = Goal.objects.get(id=goal_id)
	json_object=get_workouts_in_time(request, access_token, goal)

	total_miles=get_total_miles(json_object, goal)
	paths=[]
	paths.append(get_points_from_path(get_specific_path(request,access_token, "/223098561")))

	timeleft = get_time_left(goal)
	days = timeleft.days
	hours = timeleft.seconds / 60 / 60
	minutes = (timeleft - timedelta(seconds=hours*60*60)).seconds / 60
	

	json = ({
		'miles_goal': float(goal.distance/1600),
		"current_progress": total_miles, 
		'pledge_amount': float(goal.money), 
		 "avg_speed":0, 
		 "distance": float(goal.distance), 
		 "time_left":2, 
		 "days": days, 
		 "hours": hours, 
		 "minutes": minutes,
		 "percent_completed":float(get_total_miles(json_object, goal))/float(goal.distance)*100/1600,
		 "paths":simplejson.dumps(paths)})

	return HttpResponse(simplejson.dumps(json), 'application/json')


def goals(request, goal_id):
	goal_id = int(normalize_arg(goal_id))
	if 'code' in request.GET:
		code = request.GET['code']
		code = normalize_arg(code)
		state = request.GET['state']
		
		redirect = '%sgoal/%d' % (redirect_uri, goal_id)
		access_token = get_access_token(request, code, redirect)
		goal = Goal.objects.get(id=goal_id)
		send_email_to_friend(goal)
		json_object=get_workouts_in_time(request, access_token, goal)

		total_miles=get_total_miles(json_object, goal)
		paths=[]
		timeleft = get_time_left(goal)
		days = timeleft.days
		hours = timeleft.seconds / 60 / 60
		minutes = (timeleft - timedelta(seconds=hours*60*60)).seconds / 60
		all_workouts=get_all_workouts(request, access_token)
		for path in get_all_individual_ids(all_workouts):
			paths.append(get_points_from_path(get_specific_path(request,access_token, path)))
		t = get_template('go.html')

		html=t.render(Context({
			'miles_goal': goal.distance/1600,
		 	"current_progress": float(total_miles),
		 	'pledge_amount': goal.money, 
			"avg_speed":0, 
			"distance": int(goal.distance), 
			"time_left":2, "days": days, 
			"hours": hours, "minutes": minutes,
		 	"percent_completed": int(float(get_total_miles(json_object))/float(goal.distance)*100/1600),
>>>>>>> 3697afb08a5b9a8ddc39345a154aa7f0aeaeb46a
		 	"paths":simplejson.dumps(paths), 
		 	'access_token': access_token, 
		 	'goal_id': goal_id}))
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
	response=requests.get(BASE_URL+specific_workout, headers=headers).json()['path']
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

def get_time_left(goal):
	return goal.end_date.replace(tzinfo=None) - datetime.utcnow()

def get_total_miles(json_object, goal):
	created_time = goal.created_date.replace(tzinfo=None)
	return sum([item['total_distance'] for item in json_object if ((datetime.strptime(normalize_arg(item["start_time"]), '%a, %d %b %Y %H:%M:%S').replace(tzinfo=None) + timedelta(hours=7)) > created_time)])


def get_points_from_path(path):
	return [[point['longitude'], point['latitude'], point['timestamp']] for point in path]


def get_all_individual_ids(json_object):
	return [item['uri'] for item in json_object]

def send_email(goal):
	send_mail('You created a goal', 'You made the goal to run %d miles by %s.  Good luck!' % (goal.distance, goal.end_date), 'team@ontherun.com', ['amni2015@gmail.com'], fail_silently=False)


def send_email_to_friend(goal):
	send_mail('Help Support Your Friend Matthew', 'Your friend Matthew made the goal to run %d miles by %s.  Pledge money to help him out!  You can help him by going to this <a href="127.0.0.1:8000/support/6"> address </a>' % (goal.distance, goal.end_date), 'team@ontherun.com', ['amni2015@gmail.com'], fail_silently=False)

def date_to_param(date):
	return '%d-%d-%d' % (date.year, date.month, date.day)

def create_paypal_support_payment(amount, goal_id):
	payment = paypalrestsdk.Payment({
	  "intent":  "sale",

	  # ###Payer
	  # A resource representing a Payer that funds a payment
	  # Payment Method as 'paypal'
	  "payer":  {
	    "payment_method":  "paypal" },

	  # ###Redirect URLs
	  "redirect_urls": {
	    "return_url": "http://127.0.0.1:8000/completedsupport",
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
	  for link in payment.links:
	    if link.method == "REDIRECT":
	      redirect_url = link.href
	      print("Redirect for approval: %s" % (redirect_url))
	      return HttpResponseRedirect(redirect_url)
	else:
	  print("Error while creating payment:")
	  print(payment.error)

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


def support(request, goal_id):
	goal = Goal.objects.get(id=goal_id)
	t = get_template('support.html')
	html = t.render(Context({'miles_goal':goal.distance, "end_time":goal.end_date}))
	return HttpResponse(html)


def completedsupport(request):
	t = get_template('supportcomplete.html')
	html = t.render(Context({}))
	return HttpResponse(html)




