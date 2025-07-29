
import json
import requests
from django.conf import settings

# create checkout function to initiate payment
def checkout(payload):
	# set headers for the request
	headers = {
		"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}", # who you are
		"Content-Type": "application/json" # what kind of content are you sending to the api
	}

	# make a http request to paystack api
	response = requests.post(
		'https://api.paystack.co/transaction/initialize', # api url
		headers=headers, # who you are and what you are sending
		data=json.dumps(payload) # the data dumped in json that you are sending
	)

	# response data in json
	response_data = response.json()

	# return status and auth url if successful
	if response_data.get('status') == True:
		return True, response_data['data']['authorization_url']
	else:
		return False, f"Failed to initiate payment, try again. {response_data.get('status')}. Payload: {payload}" # unsuccessful payment
