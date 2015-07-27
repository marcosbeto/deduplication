#-*- coding: utf-8 -*-
import api.settings as settings
import requests
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.http import HttpResponse, Http404

class api_interface:

    @staticmethod
    def get_ads_from_api(filters, barrios_list):

        if "type" in filters.keys():
            if filters['type'] in ["house", "casa"]:
                idTipoDePropriedad = 1
            elif filters['type'] in ["apartment", "apartamento"]:
                idTipoDePropriedad = 2
            elif filters['type'] in ["terrain", "terreno"]:
                idTipoDePropriedad = 1003
            elif filters['type'] in ["rural"]:
                idTipoDePropriedad = 1004
            elif filters['type'] in ["comercial"]:
                idTipoDePropriedad = 1005
        else:
            idTipoDePropriedad = None

        if "negotiation" in filters.keys():
            if filters['negotiation']=="venda":
                idTipoDeOperacion = 1
            elif filters['negotiation']=="aluguel":
                idTipoDeOperacion = 2
            elif filters['negotiation']=="temporada":
                idTipoDeOperacion = 4
            elif filters['negotiation']=="lancamentos":
                idTipoDeOperacion = 5
            else:
                idTipoDeOperacion = 1
        else:
            idTipoDeOperacion = 1

        if 'priceRange' in filters.keys():
            min_price = filters['priceRange']['min']
            max_price = filters['priceRange']['max']

        query_url = settings.IMOVELWEB_API_QUERY_URL
        auth_uuid = settings.IMOVELWEB_API_UUID
        username = settings.IMOVELWEB_API_USERNAME
        password = settings.IMOVELWEB_API_PASSWORD
        user_agent = settings.IMOVELWEB_API_USER_AGENT
        
        barrios_params = ""

        if(len(barrios_list)==0 or barrios_list[0]=="all"):
            barrios_params = []
        elif len(barrios_list) == 1:
            barrios_params = barrios_list[0]
        elif len(barrios_list) > 1:
            for barrio in barrios_list:
                barrios_params = "%s:%s" % (barrio,barrios_params)
            barrios_params = barrios_params[:-1]
        else:
            return []


        url_params = {'idciudad': 109668}
        url_params['idzona'] = barrios_params

        if idTipoDePropriedad:
            url_params['idtipodepropiedad'] = idTipoDePropriedad

        if filters['rooms']:
            url_params['habitaciones'] = filters['rooms']

        if filters['page']:
            url_params['pagina'] = filters['page']

        if filters['sort']:
            url_params['sort'] = filters['sort']
        
        if idTipoDeOperacion:
            if idTipoDeOperacion==5:
                url_params['perteneceAUnDesarrollo'] = "true"
            else:
                url_params['idtipodeoperacion'] = idTipoDeOperacion  

        url_params['preciomin'] = min_price
        url_params['preciomax'] = max_price
        # url_params['sort'] = "desc"

        headers = {'username': username, 'password': password, 'User-Agent': user_agent, 'uuid': auth_uuid}

        r = requests.get(query_url, params=url_params, headers=headers)

        json_response = r.json()

        ads_count = json_response['data']['total']
        ads = json_response['data']['avisos']

        resp_object = {}
        resp_object["ads"] = ads
        resp_object["ads_count"] = ads_count

        return resp_object

    @staticmethod
    def get_ad_details_from_api(ad_id):

        headers = {
        'username': settings.IMOVELWEB_API_USERNAME, 
        'password': settings.IMOVELWEB_API_PASSWORD, 
        'User-Agent': settings.IMOVELWEB_API_USER_AGENT, 
        'uuid': settings.IMOVELWEB_API_UUID
        }

        request = requests.get(settings.IMOVELWEB_API_QUERY_URL_AD_DETAIL + ad_id, headers=headers)

        return request.json()

    @staticmethod
    def semilogin(email, uuid):

        headers = {'uuid': uuid}
        url_params = {'email': email}

        request = requests.get(settings.IMOVELWEB_API_QUERY_SEMILOGIN, params=url_params, headers=headers)
        jsonRequest = request.json()

        return jsonRequest

    @staticmethod
    def get_uuid_from_email(email):

        url_params = {'email': email}

        request = requests.get(settings.IMOVELWEB_API_QUERY_UUID_RETRIEVE, params=url_params)
        jsonRequest = request.json()

        return jsonRequest

    @staticmethod
    def add_favorite(email, adId, uuid):

        headers = {
        'uuid': uuid
        }

        url_params = {'email': email}

        request = requests.get(settings.IMOVELWEB_API_QUERY_ADD_FAVORITE + adId, params=url_params, headers=headers)
        jsonRequest = request.json()

        return jsonRequest

    @staticmethod
    def remove_favorite(email, adId, uuid):

        headers = {
        'uuid': uuid
        }

        url_params = {'email': email}

        request = requests.get(settings.IMOVELWEB_API_QUERY_REMOVE_FAVORITE + adId, params=url_params, headers=headers)
        jsonRequest = request.json()

        return jsonRequest

   

    @staticmethod
    def send_email_seller(email, telefono, mensaje, adId, uuid):

        headers = {
        'uuid': uuid
        }

        url_params = {
            'email': email,
            'telefono': telefono,
            'mensaje': mensaje            
        }

        request = requests.get(settings.IMOVELWEB_API_QUERY_SEND_EMAIL + adId, params=url_params, headers=headers)
        jsonRequest = request.json()

        return jsonRequest

    @staticmethod
    def list_favorites(email, uuid):

        headers = {
        'uuid': uuid
        }

        url_params = {'email': email}

        request = requests.get(settings.IMOVELWEB_API_QUERY_LIST_FAVORITE, params=url_params, headers=headers)
        jsonRequest = request.json()

        return jsonRequest

