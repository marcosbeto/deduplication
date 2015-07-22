import sys
import pymongo
from pymongo import MongoClient
import json
from json import loads
import simplejson
import utils
import time


from bson.objectid import ObjectId
from bson import json_util
from bson.json_util import dumps

from constants import Constants

class Models(object):

	def __init__(self):
		self.con_mongo = self.__db_mongo()

	def __db_mongo(self):		
		utils.print_inline("\n[db] Connecting MongoDB... \n")
		connection = MongoClient('localhost', 27017)
		db = connection['deduplication']

		print "MongoDB - Connected [OK]"
		return db

	def add_image_histogram(self, aviso_json):
		self.con_mongo.ads_histograms_online.insert(aviso_json)

	def get_all_avisos_online(self):
		
		array_all_avisos_online = []		
		all_avisos_online = self.con_mongo.avisosonline.find()

		#iterate in all avisos that have some photo with the same histogram
		for aviso_online in all_avisos_online:

			#getting all photos of the aviso that is being compared
			id_aviso_online = aviso_online.get("idaviso")
			array_all_avisos_online.append(int(id_aviso_online))

		return array_all_avisos_online

	def get_all_avisos_with_histogram(self):
		
		array_all_avisos_online = []		
		all_avisos_online = self.con_mongo.ads_histograms_online.find({},{"photos":0})

		#iterate in all avisos that have some photo with the same histogram
		for aviso_online in all_avisos_online:

			#getting all photos of the aviso that is being compared
			id_aviso_online = aviso_online.get("id_aviso")
			array_all_avisos_online.append(int(id_aviso_online))

		return array_all_avisos_online

	def save_id_aviso_not_histogram_table(self, aviso_json):

		self.con_mongo.ads_similar.insert(aviso_json)


	# this method is responsible for selecting each photo of all avisos from ads_histograms collection
	# and find if it has any other equal histogram in that collection. The result will be a collection that
	# has all the ads that has at least one duplicated photo 
	def create_similar_photos_collection(self):

		start = time.time()

		number_of_avisos = 0
		
		#getting all avisos from histogram table in mongo 
		print "Retrieving all online avisos. Please, wait..."
		all_avisos = self.con_mongo.ads_histograms_online.find()
		print "[Ok]"

		for aviso in all_avisos:

			now = time.time()
			if number_of_avisos%100==0:
				print str(number_of_avisos) + " - " + str(now-start)
			
			number_of_avisos += 1
			aviso_has_similar_photos = False

			#json that will save the aviso that has duplicated photos
			id_aviso = aviso.get("id_aviso")
			photos = aviso.get("photos")  

			number_of_ads = len(photos)          
			aviso_json = {"id_aviso": id_aviso, "photos":[], "number_of_ads":number_of_ads}

			#iterating in all photos of the ad
			for photo in photos:

				print "aqui0"
				is_photo_similar = False                
				
				#json that will save the data of the main photo that is being compared
				main_photo_json = {"main_photo": photo.get("photo_path"), "similar_photos":[]}

				#finding photos with the same histogram
				print "Searching..."
				equals_avisos = self.con_mongo.ads_histograms.find({"photos.histogram":photo.get("histogram"),"id_aviso":{"$ne":id_aviso}})
				print "[OK]" + str(len(photos))
				#iterate in all avisos that have some photo with the same histogram
				for other_aviso in equals_avisos:

					print "aqui"

					#getting all photos of the aviso that is being compared
					photos_compare = other_aviso.get("photos")

					#iterating in all photos to verify which one has the same histogram
					for photo_compare in photos_compare:
						
						#verifying if the photo has the same histogram, excluding photos of the same aviso
						if photo.get("histogram")==photo_compare.get("histogram"):
							#json that saves the data of the similar photo that will be saved in similar_photos[] of main_photo_json
							similar_photo_json = {"similar_id_aviso":other_aviso.get("id_aviso"), "similar_photo":photo_compare.get("photo_path")}
							main_photo_json["similar_photos"].append(similar_photo_json)
							aviso_has_similar_photos = True
							is_photo_similar = True

					print "aqui2"
				
				#saves main_photo_json if exists a photo inside the other aviso that is equal to the aviso main photo
				if is_photo_similar:
					aviso_json["photos"].append(main_photo_json);
			
			
			

			#saves in mongo the aviso json if there is any photo that has others equal photos 
			if aviso_has_similar_photos:
				self.con_mongo.ads_similar.insert(aviso_json)

		print "[OK] Analized " + str(number_of_avisos) + " avisos and 'ads_similar' collection created."
	

	def is_aviso_online(self,aviso_id):

		aviso_online = self.con_mongo.avisosonline.find({"idaviso":int(aviso_id)}).count()

		if aviso_online > 0:
			return True

		return False

	def create_equals_avisos_collection(self):

		start = time.time()
		number_of_similar_aviso_analyzed = 0


		all_similar_avisos = self.con_mongo.ads_similar.find()

		#iterating in all avisos that has duplicated images
		for similar_aviso in all_similar_avisos:
			
			photos = similar_aviso.get("photos")
			unique_similar_avisos = []

			#jsoin that will save all equal avisos, where "equal avisos" represents avisos where the group of its photos is 90% equal
			aviso_json = {"id_aviso":similar_aviso.get("id_aviso"),"equal_avisos":[]}

			for photo in photos:

				#getting all similar photos
				similar_photos = photo.get("similar_photos")

				for similar_photo in similar_photos:

					invalid_images = False;

					#verifying if image is not one of the invalid images strings
					for image_to_delete in Constants.NOT_ALLOWED_IMAGES:
						if image_to_delete in similar_photo.get("similar_photo"):
							invalid_images = True
							break
					
					#getting the id of the aviso that has a image equal to the one being analized
					similar_id_aviso = similar_photo.get("similar_id_aviso")

					if not invalid_images:

						similar_aviso_already_on_array = False
						
						#iterating all unique similar_avisos
						for index, unique_similar_aviso in enumerate(unique_similar_avisos, start=0):
							
							#if similar_id_aviso already exists in json
							if unique_similar_aviso.get("id_aviso")==similar_id_aviso:
								similar_aviso_already_on_array = True
								unique_similar_avisos[index]['num_photos_equal'] += 1
								number_total_photos_parent = unique_similar_avisos[index]['num_photos_parent']
								# print str(unique_similar_avisos[index]['num_photos_equal'])  + " - " + str(number_total_photos)

								
								#calculating the % of similarity of the group of photos between the aviso and the aviso that has similar photos
								
								percentage_of_similar = utils.percentage(unique_similar_avisos[index]['num_photos_equal'],number_total_photos_parent)

								# print "Pai: " + str(similar_aviso.get("id_aviso")) + "Filho: " + str(unique_similar_avisos[index]['id_aviso']) + "Percentual:  " + str(percentage_of_similar) 
								
								unique_similar_avisos[index]['percentage_similar_self_parent'] = int(percentage_of_similar)
								
						#did not find any similar id_aviso or the array is empty
						if not similar_aviso_already_on_array:                            

							similar_aviso_support = self.con_mongo.ads_similar.find({"id_aviso":similar_id_aviso})
							similar_aviso_support = loads(dumps(similar_aviso_support))

							number_of_ads_similar = similar_aviso.get("number_of_ads")
							number_of_ads_similar = similar_aviso_support[0].get("number_of_ads")

							# print "number_of_ads_similar: " + str(number_of_ads_similar) + " | number_of_ads_similar: " + str(number_of_ads_similar)

							percentage_of_similar = utils.percentage(1,number_of_ads_similar)

							similar_aviso_json = {"id_aviso":similar_id_aviso,
							"num_photos_equal":1,
							"num_photos_total": number_of_ads_similar,
							"num_photos_parent":number_of_ads_similar,
							"percentage_similar_self_parent": int(percentage_of_similar),

							}
							
							#adding the similar aviso with the percentage of the similarity between the photos of both avisos
							unique_similar_avisos.append(similar_aviso_json)


			only_equal_avisos = []

			# adding to json only ads that have more than 85% of similarity in the group of both photos
			for unique_similar_aviso in unique_similar_avisos:

				percentage_number_of_photos = utils.percentage(unique_similar_aviso['num_photos_equal'],unique_similar_aviso['num_photos_total'])

				#checkinf if the aviso being compared to main_aviso has similar number of photos
				if percentage_number_of_photos>=90 and percentage_number_of_photos<=100:
					if unique_similar_aviso['percentage_similar_self_parent']>90:
						aviso_json["equal_avisos"].append(unique_similar_aviso)
					
			#inserting in mongo the collection of equals avisos
			if len(aviso_json["equal_avisos"]) > 0:
				self.con_mongo.ads_equals.insert(aviso_json)

			number_of_similar_aviso_analyzed += 1

			if number_of_similar_aviso_analyzed%100==0:
				now = time.time()
				print str(number_of_similar_aviso_analyzed) + " - " + str(now-start)

		print "[OK] Analized " + str(number_of_similar_aviso_analyzed) + " avisos and 'ads_equals' collection created."

	def create_raw_equal_avisos(self):
		
		start = time.time()

		all_duplicated_avisos = self.con_mongo.ads_equals.find()

		for duplicated_aviso in all_duplicated_avisos:
				
			raw_equal_avisos = []

			raw_equal_avisos.append(duplicated_aviso.get("id_aviso"))
			# set(x) == set(y)

			equal_avisos = duplicated_aviso.get("equal_avisos")

			for equal_aviso in equal_avisos:

				raw_equal_avisos.append(equal_aviso.get("id_aviso"))

			self.con_mongo.ads_equals.update({"id_aviso" :duplicated_aviso.get("id_aviso")},{'$set' : {"raw_equal_avisos":raw_equal_avisos}})

		print "[OK] Created the raw fields of duplicated ads."


	def create_duplicateds_group_collection(self):

		all_duplicated_avisos = self.con_mongo.ads_equals.find()
		

		all_equals_json = []

		all_avisos = 0

		for duplicated_aviso in all_duplicated_avisos:

			aviso_already_analized = False
			some_equal = False

			number_of_grouped = 0;

			#json that saves the raw_equal_avisos and the avisos[] that have this respective raw
			grouped_equal_avisos = {"avisos":[],"raw_equal_avisos":duplicated_aviso.get("raw_equal_avisos")}

			#adding the aviso that is being analized aviso to avisos[] array
			# grouped_equal_avisos["avisos"].append(duplicated_aviso.get("id_aviso"))
			
			for compared_aviso in all_equals_json:

				group_avisos_duplicated = compared_aviso.get("avisos")
				
				for aviso_duplicated in group_avisos_duplicated:
					
					if duplicated_aviso.get("id_aviso") == aviso_duplicated.get("id_aviso"):
						aviso_already_analized = True
						# print "aviso_already_analized = TRUE"


			if not aviso_already_analized:

				all_duplicated_avisos_compare = self.con_mongo.ads_equals.find()

				#iterating in other avisos to see if there is a raw avisos equal to group them
				for duplicated_aviso_compare in all_duplicated_avisos_compare:

					#checking if they have the same raw
					if duplicated_aviso_compare.get("raw_equal_avisos")!=None and duplicated_aviso.get("raw_equal_avisos")!=None and set(duplicated_aviso_compare.get("raw_equal_avisos")) == set(duplicated_aviso.get("raw_equal_avisos")):
						some_equal = True
						#if they are different ads add to avisos[] array of avisos with the same raw
						#if duplicated_aviso.get("id_aviso") != duplicated_aviso_compare.get("id_aviso"):
						grouped_equal_avisos["avisos"].append({"id_aviso":duplicated_aviso_compare.get("id_aviso"),"url":""})

			all_avisos += 1
			
			if some_equal:
				all_equals_json.append(grouped_equal_avisos)
				self.con_mongo.ads_equals_grouped.insert(grouped_equal_avisos)

		print "[OK] Created final collection for duplicated avisos."
