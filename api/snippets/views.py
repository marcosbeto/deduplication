from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from django.core import serializers
from django.template import RequestContext, loader
from django.shortcuts import render, redirect

from api_interface import api_interface
import os

class JSONResponse(HttpResponse):
	"""
	Um HttpReponse  que renderiza seu conteudo em, json.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def snippet_list(request):
	"""
	List all code snippets, or create a new snippet.
	"""
	if request.method == 'GET':
		snippets = Snippet.objects.all()
		serializer = SnippetSerializer(snippets, many=True)

		context = {'duplicateds_avisos': snippets}
		return render(request, 'all_duplicateds.html', context)

		return JSONResponse(serializer.data)

	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = SnippetSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def snippet_list_api(request):
	"""
	List all code snippets, or create a new snippet.
	"""
	if request.method == 'GET':
		snippets = Snippet.objects.all()
		serializer = SnippetSerializer(snippets, many=True)

		return JSONResponse(serializer.data)

	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = SnippetSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def redirect_to_aviso(request, id):
	try:
		ad_details_response = api_interface.get_ad_details_from_api(id)
		return redirect("http://" + ad_details_response['data']['url'])
		# print JSONResponse(snippet.data)
	except Snippet.DoesNotExist:
		return HttpResponse(status=404)

@csrf_exempt
def snippet_detail(request, id):
	"""
	Retrieve, update or delete a code snippet.
	"""
	try:
		snippet = Snippet.objects.raw_query({'rea' : int(id)})
		
		if not snippet:
			return HttpResponse(status=404)

		all_avisos = snippet.values('rea')[0]
	except Snippet.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = SnippetSerializer(all_avisos)
		context = {'duplicateds_avisos': all_avisos['rea']}

		return render(request, 'duplicateds.html', context)

	elif request.method == 'PUT':
		data = JSONParser().parse(request)
		serializer = SnippetSerializer(snippet, data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data)
		return JSONResponse(serializer.errors, status=400)

	elif request.method == 'DELETE':
		snippet.delete()
		return HttpResponse(status=204)

@csrf_exempt
def snippet_detail_api(request, id):
	"""
	Retrieve, update or delete a code snippet.
	"""
	try:
		snippet = Snippet.objects.raw_query({'rea' : int(id)})
		# print JSONResponse(snippet.data)
	except Snippet.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':

		if snippet:
			all_avisos = snippet.values('rea')[0]
			serializer = SnippetSerializer(all_avisos)
			return JSONResponse(serializer.data)
		else:
			all_avisos = [{"Message":"No duplicated ads found."}]
		
		return JSONResponse(all_avisos)
		

	elif request.method == 'PUT':
		data = JSONParser().parse(request)
		serializer = SnippetSerializer(snippet, data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data)
		return JSONResponse(serializer.errors, status=400)

	elif request.method == 'DELETE':
		snippet.delete()
		return HttpResponse(status=204)