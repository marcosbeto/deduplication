from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from snippets.models import Snippet
from snippets.models import Ads_equals_with_filters
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
def snippet_list_api(request, filters):
	"""
	List all code snippets, or create a new snippet.
	"""
	filters = filters.split("/")[:-1]

	titulo = request.GET.get('titulo')
	idzona = request.GET.get('idzona')
	idempresa = request.GET.get('idempresa')
	idtipodepropiedad = request.GET.get('idtipodepropiedad')
	idsubtipodepropiedad = request.GET.get('idsubtipodepropiedad')
	idavisopadre = request.GET.get('idavisopadre')
	idciudad = request.GET.get('idciudad')
	precio = request.GET.get('precio')
	direccion = request.GET.get('direccion')
	codigopostal = request.GET.get('codigopostal')
	habitaciones = request.GET.get('habitaciones')
	garages = request.GET.get('garages')
	banos = request.GET.get('banos')
	mediosbanos = request.GET.get('mediosbanos')
	metroscubiertos = request.GET.get('metroscubiertos')
	metrostotales = request.GET.get('metrostotales')
	idtipodeoperacion = request.GET.get('idtipodeoperacion')

	if request.method == 'GET':

		for filter_unique in filters:

			if filter_unique=="all":
				snippets = Snippet.objects.all()
				serializer = SnippetSerializer(snippets, many=True)
				return JSONResponse(serializer.data)
			else:
				snippets = list(Ads_equals_with_filters.objects.raw_query(
					{
						'rea.data.idtipodeoperacion':int(idtipodeoperacion),
						'$and': [{'$where': "this.rea.length > 1"}]
					}
				))
				serializer = SnippetSerializer(snippets, many=True)

				new_json = []

				for i in xrange(len(serializer.data)):
					reas = serializer.data[i].get("rea")
					# print reas
					if len(reas)<10:
						print "eae"
						del serializer.data[i]
					# for rea in reas:
					# 	print rea.get("id_aviso")

					# 	if filter_unique=="idtipodeoperacion":

				# print new_json
				# for aviso2 in new_json.data:
				# 	reas = aviso2.get("rea")
				# 	print len(reas)
					# for rea in reas:
					# 	print rea.get("id_aviso")

					# 	if filter_unique=="idtipodeoperacion":


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
		print ad_details_response
		if ad_details_response['errorCode']:
			return JSONResponse({"Aviso OFFLINE"}, status=201)
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