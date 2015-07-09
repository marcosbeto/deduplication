import json
import requests
import urllib
import os
from json import loads
from constants import Constants

# from utils import Utils
import utils

import cv2
import time
import numpy
import array

class Downloader(object):

	def download_photos(self):
		
		total_photos_from_neighborhood = 0
		total_size_downloaded_from_neighborhood = 0

		page = 1

		while (True):
			
			print "\n-> PAGINA: %s" % (str(page))

			total_photos_in_page = 0
			total_size_downloaded_in_page = 0

			url_params = {'idciudad': Constants.CITY_ID_TO_DOWNLOAD, 'idzona': Constants.NEIGHBORHOOD_ID_TO_DOWNLOAD, 'pagina': page}
			request_response = requests.get(Constants.IMOVELWEB_API_QUERY_URL, params=url_params, headers=Constants.DEFAULT_IMOVELWEB_API_HEADER)
			json_response = request_response.json()
			
			ads = json_response['data']['avisos']

			for ad in ads:

				number_of_photos_from_ad = 0
				total_size_downloaded_from_ad = 0

				for attribute, value in ad.iteritems():
					
					if attribute=='fotos':

						for photo in value:
							photo_url = photo.get('url').replace("580x465", Constants.PHOTO_SIZE_TO_DOWNLOAD); # getting smaller images

							local_dir_saved_photo = Constants.LOCAL_DIR_SAVE_PHOTO + "/" +  str(ad.get('idpropiedad'))

							local_path_to_save_photo = local_dir_saved_photo + "/" + photo_url.rpartition('/')[2]

							if not os.path.exists(local_dir_saved_photo): 
								os.mkdir(local_dir_saved_photo) #creating aviso directory to save photo

							urllib.urlretrieve(photo_url, local_path_to_save_photo) #downloading photo
							size = format(utils.bytesto(os.path.getsize(local_path_to_save_photo), 'm'),'.4f') #size in megabytes of each photo

							number_of_photos_from_ad += 1
							total_size_downloaded_from_ad = total_size_downloaded_from_ad + float(size)

				print "[#AD] Photos from:  %s: %s | Tamanho:%s\n" % (ad.get('idpropiedad'),str(number_of_photos_from_ad),str(total_size_downloaded_from_ad))
				
				total_photos_in_page = total_photos_in_page + number_of_photos_from_ad
				total_size_downloaded_in_page = total_size_downloaded_in_page + total_size_downloaded_from_ad
			
				print "[#PAGE] Photos from page %s: %s | Tamanho:%s\n" % (page,str(total_photos_in_page),str(total_size_downloaded_in_page))

				total_photos_from_neighborhood = total_photos_from_neighborhood + total_photos_in_page
				total_size_downloaded_from_neighborhood = total_size_downloaded_from_neighborhood + total_size_downloaded_in_page

				#checking if it's the end of the listings
				if len(ads)<Constants.NUMBER_OF_ADS_RETURNED_API:
					break       

			page += 1

		print "[#TOTAL] Photos from all pages: %s | Tamanho:%s\n" % (str(total_photos_from_neighborhood),str(total_size_downloaded_from_neighborhood))

