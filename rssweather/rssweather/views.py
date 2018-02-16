from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

import requests

def weather(request, latitude, longitude):
	#question = get_object_or_404(Question, pk=question_id)
	#return render(request, 'polls/detail.html', {'question': question})
	return HttpResponse(str(latitude) + ' ' + str(longitude))