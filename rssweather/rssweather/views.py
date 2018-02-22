from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from feedgen.feed import FeedGenerator
from urllib.request import urlopen
import json
import requests
import urllib.parse
import time

# Position class
class Position:
	def __init__(self, positionArray):
		self.langitude = positionArray[0]
		self.longitude = positionArray[1]

	def __str__(self):
		return 'Langitude: ' + self.langitude + 'Longitude: ' + self.longitude

# Parse raw input to list of lat and long
def parseQueryToPosition(latitudelongitude):
	position = [x.strip() for x in latitudelongitude.split(',')]
	return position

# Call Google API to get city and state
def getplace(lat, lon, key):
    # build URL
    url = "https://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    url += "key=%s" % (key)
    
    # Get response
    v = urlopen(url).read()
    j = json.loads(v)
    
    # Parse response
    components = j['results'][0]['address_components']
    state = town = None
    for c in components:
        if "administrative_area_level_1" in c['types']:
            state = c['long_name']
        if "administrative_area_level_2" in c['types']:
            city = c['long_name']

    # build return string
    cityState = city + ', ' + state
    return cityState

# Weather App
def weather(request, latitudelongitude):
	# API
	apiKey = 'db88a36f0e9a8b4b62252702452bab42'
	url = 'https://api.darksky.net/forecast/'
	googleMapsApiKey = 'AIzaSyDg9DQ1jVpiyjJtAhy01KhDOgWgYBy6tOw'

	# parse input
	positionParsed = parseQueryToPosition(latitudelongitude)
	positionObject = Position(positionParsed)

	# build URL call
	callURL = url + apiKey + '/' + positionObject.langitude + ',' + positionObject.longitude

	# Call API
	response = requests.get(callURL)

	# DEBUG: convert to Str type (which is json string) for debug purposes
	#json_string = json.dumps(response.json())
	#print (type(json_string))

	# Convert response string into JSON type
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
	title = ' | Temperature: ' + temperature + '°F | '+ 'Overall, it is ' + summary
	if alertsTitle != '':
	    title += ' | Watch out! ' + alertsTitle

	# Get place in GPS
	place = getplace(positionObject.langitude, positionObject.longitude, googleMapsApiKey)

	# Build RSS channel
	feedChannel = FeedGenerator()
	feedChannel.id('weather_' + str(time.time()))
	feedChannel.title('WeatherPy - ' + place)
	feedChannel.author( {'name':'Ben','email':'benedict.tobias@gmail.com'} )
	feedChannel.subtitle('Powered by Dark Sky API')
	feedChannel.link( href=weatherHyperLink, rel='self' )
	feedChannel.language('en')

	# Build RSS weather item/entry
	feedEntry = feedChannel.add_entry()
	feedEntry.id('weather_' + str(time.time()))
	feedEntry.title(place + title)
	feedEntry.link( href=weatherHyperLink, rel='self' )

	# Get the RSS feed as string
	rssFeed  = feedChannel.rss_str(pretty=True) 
	#print (rssfeed)

	# return as HTTPresponse
	return HttpResponse(rssFeed, content_type='application/xhtml+xml,application/xml')