from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from snippets.models import Snippet
from snippets.models import Ads_equals_with_filters
from snippets.models import Ads_equals_filtered_grouped
from snippets.models import Grouped_number_of_ads_equals
from snippets.serializers import SnippetSerializer
from snippets.serializers import SnippetSerializer_Numbers
from snippets.serializers import SnippetSerializer_Grouped_Filtered
from django.core import serializers
from django.template import RequestContext, loader
from django.shortcuts import render, redirect


import pymongo
from pymongo import MongoClient

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
def snippet_list(request, filters):
	"""
	List all code snippets, or create a new snippet.
	"""
	filters = filters.split("/")[:-1]


	if request.method == 'GET':
		for filter_unique in filters:
			if filter_unique=="all":
				snippets = Snippet.objects.all()
				# serializer = SnippetSerializer(snippets, many=True)
				# return JSONResponse(serializer.data)
			else:

				raw_query_complete = get_raw_filters(request)
				snippets = Ads_equals_with_filters.objects.raw_query(raw_query_complete)
				# serializer = SnippetSerializer(snippets, many=True)
			
		context = {'duplicateds_avisos': snippets}
		return render(request, 'all_duplicateds.html', context)

	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = SnippetSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def equals_ads_list_filtered(request):
	"""
	List all code snippets, or create a new snippet.
	"""
	if request.method == 'GET':

		snippets = Ads_equals_filtered_grouped.objects.raw_query()[:10]
		context = {'duplicateds_avisos_filtered': snippets}
		return render(request, 'all_duplicateds_filtered.html', context)
	
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = SnippetSerializer(data=data)
		
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		
		return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def equals_ads_list_filtered_grouped(request):
	"""
	List all code snippets, or create a new snippet.
	"""
	if request.method == 'GET':

		snippets = Grouped_number_of_ads_equals.objects.order_by('noe')
		context = {'duplicateds_avisos_filtered': snippets}
		return render(request, 'all_duplicateds_grouped.html', context)
	
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = SnippetSerializer(data=data)
		
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		
		return JSONResponse(serializer.errors, status=400)


@csrf_exempt
def get_group_number_of_ads(request):
	context = RequestContext(request)
	number_of_ads = None

	if request.method == 'GET':

		number_of_ads = request.GET['number_of_ads']
		pagination = request.GET['pagination']
		action = request.GET['action']

		if number_of_ads:
			print number_of_ads
			if action=="prev":
				print 'pagination' + pagination
				grouped = Ads_equals_filtered_grouped.objects.raw_query({ "reas": { "$size": int(number_of_ads)}}).order_by('-equal_filters')[int(pagination)-10:int(pagination)]
			else:
				grouped = Ads_equals_filtered_grouped.objects.raw_query({ "reas": { "$size": int(number_of_ads)}}).order_by('-equal_filters')[int(pagination):int(pagination)+10]
			
			serializer = SnippetSerializer_Grouped_Filtered(grouped, many=True)
			
			return JSONResponse(serializer.data)

	return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def get_group_number_of_ads_filtered(request):
	context = RequestContext(request)

	if request.method == 'GET':

		id_aviso = request.GET['id_aviso']

		if id_aviso:
			grouped = Ads_equals_filtered_grouped.objects.raw_query({ "reas": int(id_aviso)})

			serializer = SnippetSerializer_Grouped_Filtered(grouped, many=True)

			return JSONResponse(serializer.data)

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
				snippets = Grouped_number_of_ads_equals.objects.all()
				serializer = SnippetSerializer_Numbers(snippets, many=True)
				return JSONResponse(serializer.data)
			else:
				snippets = list(Ads_equals_with_filters.objects.raw_query(
					{
						'rea.data.idtipodeoperacion':int(idtipodeoperacion),
						'$and': [{'$where': "this.rea.length > 1"}]
					}
				))
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
		if ad_details_response['errorCode']:
			return JSONResponse({"Aviso OFFLINE"}, status=201)
		return redirect("http://" + ad_details_response['data']['url'])
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
		snippet = Grouped_number_of_ads_equals.objects.raw_query({'reas':{'$elemMatch':{'$elemMatch':{'$in':[int(id)]}}}})
		# snippet = Grouped_number_of_ads_equals.objects.raw_query({'rea' : int(id)})

	except Snippet.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':

		if snippet:
			all_avisos = snippet.values('reas')[0]
			print all_avisos
			serializer = SnippetSerializer_Numbers(all_avisos)
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

def get_raw_filters(request):
	
	raw_query_complete = {}

	if request.GET.get('idtipodeoperacion'):
		raw_query_complete.update({'rea.data.idtipodeoperacion':int(request.GET.get('idtipodeoperacion'))})

	if request.GET.get('idtipodepropiedad'):
		raw_query_complete.update({'rea.data.idtipodepropiedad':int(request.GET.get('idtipodepropiedad'))})

	if request.GET.get('idsubtipodepropiedad'):
		raw_query_complete.update({'rea.data.idsubtipodepropiedad':int(request.GET.get('idsubtipodepropiedad'))})

	if request.GET.get('idtipodeoperacion'):
		raw_query_complete.update({'rea.data.idtipodeoperacion':int(request.GET.get('idtipodeoperacion'))})

	if request.GET.get('idciudad'):
		raw_query_complete.update({'rea.data.idciudad':int(request.GET.get('idciudad'))})

	if request.GET.get('idzona'):
		raw_query_complete.update({'rea.data.idzona':int(request.GET.get('idzona'))})

	if request.GET.get('idempresa'):
		raw_query_complete.update({'rea.data.idempresa':int(request.GET.get('idempresa'))})

	if request.GET.get('codigopostal'):
		raw_query_complete.update({'rea.data.codigopostal':request.GET.get('codigopostal')})

	if request.GET.get('direccion'):
		raw_query_complete.update({'rea.data.direccion':request.GET.get('direccion')})

	if request.GET.get('titulo'):
		raw_query_complete.update({'rea.data.titulo':request.GET.get('titulo')})

	# The following cases recieves a parameter that will represent the percentage of range down and up that will be searched
	# Example: metroscubiertos = 10 -> we will search for all equal ads that have the metrocubiertos between 90-110% of similar sizes

	if request.GET.get('metroscubiertos'):
		raw_query_complete.update({'rea.data.metroscubiertos':int(request.GET.get('metroscubiertos'))})

	if request.GET.get('metrostotales'):
		raw_query_complete.update({'rea.data.metrostotales':int(request.GET.get('metrostotales'))})
	
	if request.GET.get('habitaciones'):
		raw_query_complete.update({'rea.data.habitaciones':int(request.GET.get('habitaciones'))})

	if request.GET.get('precio'):
		raw_query_complete.update({'rea.data.precio':int(request.GET.get('precio'))})

	raw_query_complete.update({'$and': [{'$where': "this.rea.length > 1"}]})

	return raw_query_complete

def jsonResponse(responseDict):
	return HttpResponse(simplejson.dumps(responseDict), mimetype='application/json')