from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from feedgen.feed import FeedGenerator
from urllib.request import urlopen
import json
import requests
import urllib.parse
import time

class Position:
	def __init__(self, positionArray):
		self.langitude = positionArray[0]
		self.longitude = positionArray[1]

	def __str__(self):
		return 'Langitude: ' + self.langitude + 'Longitude: ' + self.longitude

def parseQueryToPosition(latitudelongitude):
	position = [x.strip() for x in latitudelongitude.split(',')]
	return position

def getplace(lat, lon):
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    v = urlopen(url).read()
    j = json.loads(v)
    components = j['results'][0]['address_components']
    country = town = None
    for c in components:
        if "administrative_area_level_1" in c['types']:
            state = c['long_name']
        if "locality" in c['types']:
            city = c['long_name']

    cityState = city + ', ' + state

    return cityState

def weather(request, latitudelongitude):
	positionParsed = parseQueryToPosition(latitudelongitude)
	positionObject = Position(positionParsed)

	apiKey = 'db88a36f0e9a8b4b62252702452bab42'

	url = 'https://api.darksky.net/forecast/'

	callURL = url + apiKey + '/' + positionObject.langitude + ',' + positionObject.longitude

	response = requests.get(callURL)

	# Str type
	json_string = json.dumps(response.json())
	#print (type(json_string))

	# Print keys
	weatherData = response.json()
	#print (weatherData.keys())

	# Get necessary info
	currentWeather = weatherData['currently']
	temperature = str(int(currentWeather['temperature']))
	summary = currentWeather['summary']

	# Get alert if any
	if 'alerts' in weatherData:
		alerts = weatherData['alerts'][0]
		alertsTitle = alerts['title']
		alertsURI = alerts['uri']
	else:
		alertsTitle = ''
	#print (alertsTitle + ' -- ' + alertsURI)

	# Weather hyperlink
	weatherHyperLink = 'http://forecast.weather.gov/MapClick.php?'
	query = { 'lat' : positionObject.langitude, 'lon' : positionObject.longitude}
	weatherHyperLink = weatherHyperLink + urllib.parse.urlencode(query)

	# Set RSS title
	title = ' | Temperature: ' + temperature + '°F | '+ 'Summary: ' + summary
	if alertsTitle != '':
	    title += ' | Alert: ' + alertsTitle

	# Build RSS 
	fg = FeedGenerator()
	fg.id('weather_' + str(time.time()))
	fg.title('WeatherPy')
	fg.author( {'name':'Ben','email':'benedict.tobias@gmail.com'} )
	fg.subtitle('Powered by Dark Sky API')
	fg.link( href=weatherHyperLink, rel='self' )
	fg.language('en')

	fe = fg.add_entry()
	fe.id('weather_' + str(time.time()))
	fe.title(getplace(positionObject.langitude, positionObject.longitude) + title)
	fe.link( href=weatherHyperLink, rel='self' )

	rssfeed  = fg.rss_str(pretty=True) # Get the RSS feed as string
	#print (rssfeed)


	return HttpResponse(rssfeed, content_type='application/xhtml+xml,application/xml')