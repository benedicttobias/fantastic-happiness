from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

import requests

class Position:
	def __init__(self, positionArray):
		self.longitude = positionArray[0]
		self.langitude = positionArray[1]

	def __str__(self):
		return 'Longitude: ' + self.longitude + ' -- Langitude: ' + self.langitude

def parseQueryToPosition(longitudelatitude):
	position = [x.strip() for x in longitudelatitude.split(',')]
	return position

def weather(request, longitudelatitude):
	positionParsed = parseQueryToPosition(longitudelatitude)
	positionObject = Position(positionParsed)

	apiKey = 'db88a36f0e9a8b4b62252702452bab42'

	url = 'https://api.darksky.net/forecast/'

	callURL = url + apiKey + '/' + positionObject.longitude + ',' + positionObject.langitude

	response = requests.get(callURL)

	return HttpResponse(response)