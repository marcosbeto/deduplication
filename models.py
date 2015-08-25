#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pymongo
from pymongo import MongoClient

import json
from json import loads
import simplejson
import utils
import time
import zlib
import bz2
import numpy
import MySQLdb

import cv2

from bson.objectid import ObjectId
from bson import json_util
from bson.json_util import dumps

from constants import Constants

class Models(object):

	def __init__(self):
		self.con_mongo = self.__db_mongo()
		self.con_mysql = self.__db_mysql()

	def __db_mongo(self):		
		utils.print_inline("\n[db] Connecting tos MongoDB... \n")
		connection = MongoClient('localhost', 27017)
		db = connection['deduplication']
		print "MongoDB - Connected [OK]"
		return db


	def __db_mysql(self):
		utils.print_inline("\n[db] Connecting to MySQLDB... \n")
		connection = MySQLdb.connect(host = "192.168.22.78",
									  user = "imovelro",
									  passwd = "1m0v3lr0",
									  db = "navplat_realestate_imovelweb")
		db = connection.cursor(MySQLdb.cursors.DictCursor)
		print "MySQLDB - Connected [OK]"
		return db

	def create_detailed_repeated_ads_filters(self):

		skip_compare = 0
		done_compare = False
		number_of_similar_aviso_analyzed = 0

		while not done_compare:

			equals_avisos = self.con_mongo.ads_equals_grouped.find().sort([("rea", 1)]).skip(skip_compare)

			for equal_aviso in equals_avisos:

				number_of_similar_aviso_analyzed += 1

				if number_of_similar_aviso_analyzed%10==0:
					print str(number_of_similar_aviso_analyzed)

				skip_compare += 1

				rea_json = {"rea":[]}
				array_rea = equal_aviso.get("rea")

				for id_aviso in array_rea:

					

					# Prepare SQL query
					sql = "SELECT * FROM avisos where idaviso = " + str(id_aviso)

					try:
						# Execute the SQL command
						self.con_mysql.execute(sql)
						# Fetch all the rows in a list of lists.
						results = self.con_mysql.fetchall()

						for row in results:

							titulo = ""
							direccion = ""

							if row["titulo"]!=None:
								titulo = unicode(row["titulo"], "utf-8", errors='ignore')

							if row["direccion"]!=None:
								direccion = unicode(row["direccion"], "utf-8", errors='ignore')
							
							similar_aviso_json = {
								"titulo":titulo,
								"idzona":row["idzona"],
								"idempresa":row["idempresa"],
								"idtipodepropiedad":row["idtipodepropiedad"],
								"idsubtipodepropiedad":row["idsubtipodepropiedad"],
								"idavisopadre":row["idavisopadre"],
								"idciudad":row["idciudad"],
								"precio":row["precio"],
								"direccion":direccion,
								"codigopostal":row["codigopostal"],
								"habitaciones":row["habitaciones"],
								"garages":row["garages"],
								"banos":row["banos"],
								"mediosbanos":row["mediosbanos"],
								"metroscubiertos":row["metroscubiertos"],
								"metrostotales":row["metrostotales"],
								"idtipodeoperacion":row["idtipodeoperacion"],
							}

							aviso_json = {"id_aviso":id_aviso,"data":similar_aviso_json}
							rea_json["rea"].append(aviso_json)

					except:
					   print "Error: unable to fecth data"
				
				self.con_mongo.ads_equals_filtered.insert(rea_json)

			done_compare = True

		# disconnect from server
		self.con_mysql.close()

	def group_repeated_ads_filters(self):

		skip_compare = 0
		done_compare = False
		number_of_similar_aviso_analyzed = 0

		while not done_compare:

			equals_avisos = self.con_mongo.ads_equals_filtered.find().sort([("rea", 1)]).skip(skip_compare)

			for equal_aviso in equals_avisos:

				number_of_similar_aviso_analyzed += 1

				if number_of_similar_aviso_analyzed%10==0:
					print str(number_of_similar_aviso_analyzed)

				skip_compare += 1

				array_rea = equal_aviso.get("rea")

				equals_avisos_filtered = {
					"reas":[],
					"precio":[],
					"idtipodeoperacion":[],
					"idzona":[],
					"idtipodepropiedad":[],
					"titulo":[],
					"direccion":[],
					"idavisopadre":[],
					"idempresa":[],
					"idcentralvenda":[],
					"equal_filters":0
				} #equal_avisos

				for aviso in array_rea:

					equals_avisos_filtered["reas"].append(int(aviso.get("id_aviso")))

					for key in equals_avisos_filtered.keys(): 
						if not key == "reas" and not key == "equal_filters":
							self.add_equal_filtered(key, aviso, equals_avisos_filtered)

				is_all_equal = True

				for key in equals_avisos_filtered.keys(): 
					if not key == "reas" and not key == "equal_filters":
						if len(equals_avisos_filtered[key])==1:
							equals_avisos_filtered["equal_filters"] = equals_avisos_filtered["equal_filters"] + 1

				self.con_mongo.snippets_ads_equals_filtered_grouped.insert(equals_avisos_filtered)

			done_compare = True

	def add_equal_filtered(self, filter_option, aviso, equals_avisos_filtered):

		# all_idtipodepropiedad = equals_avisos_filtered["idtipodepropiedad"]
		all_filters_data = equals_avisos_filtered[filter_option]

		# idtipodepropiedad_added = False
		aviso_added = False
		
		# for idtipodepropiedad in all_idtipodepropiedad:
		for filter_data in all_filters_data:
			
			if not filter_option == "idcentralvenda":
				if aviso.get("data").get(filter_option) == filter_data["value"]:
					aviso_added = True
					filter_data["ida"].append(int(aviso.get("id_aviso")))
			else:
				idempresa = aviso.get("data").get("idempresa")
				idaviso = aviso.get("id_aviso")

				sql = "SELECT * FROM empresas where idempresa = " + str(idempresa)

				try:
					# Execute the SQL command
					self.con_mysql.execute(sql)
					# Fetch all the rows in a list of lists.
					results = self.con_mysql.fetchall()

					for row in results:

						idcentralvenda = None

						if row["idempresapadre"] != None and row["idempresapadre"] == filter_data["value"]:
							aviso_added = True
							filter_data["ida"].append(int(aviso.get("id_aviso")))
				
		if len(all_filters_data) == 0 or not aviso_added:
			
			if not filter_option == "idcentralvenda":
				filter_data_json = {"value":aviso.get("data").get(filter_option),"ida":[int(aviso.get("id_aviso"))]}
				equals_avisos_filtered[filter_option].append(filter_data_json)
			else:
				idempresa = aviso.get("data").get("idempresa")
				idaviso = aviso.get("id_aviso")

				sql = "SELECT * FROM empresas where idempresa = " + str(idempresa)

				try:
					# Execute the SQL command
					self.con_mysql.execute(sql)
					# Fetch all the rows in a list of lists.
					results = self.con_mysql.fetchall()

					for row in results:

						idcentralvenda = None

						if row["idempresapadre"] != None:
						idcentralvenda = row["idempresapadre"]
						filter_data_json = {"value":idcentralvenda,"ida":[int(aviso.get("id_aviso"))]}
						equals_avisos_filtered["idcentralvenda"].append(filter_data_json)
							
						

				except: 
					print "Error: unable to fecth data"


	def add_image_histogram(self, aviso_json):
		self.con_mongo.ads_histograms_online.insert(aviso_json)

	def get_all_avisos_online(self):
		
		array_all_avisos_online = []		
		all_avisos_online = self.con_mongo.avisosonline_2.find().sort([("idaviso", 1)])

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

	def save_compressed_histogram_online(self):

		number_of_avisos = 0

		array_all_avisos_online = []		
		all_avisos_online = self.con_mongo.ads_histograms_online.find().sort([("id_aviso", 1)])

		#iterate in all avisos that have some photo with the same histogram
		for aviso_online in all_avisos_online:

			#getting all photos of the aviso that is being compared
			id_aviso_online = aviso_online.get("id_aviso")
			photos = aviso_online.get("photos")
			aviso_json = {"id_aviso":id_aviso_online,"photos":[]}

			for photo in photos:
				histogram = photo.get("histogram")
				histrogram_compressed = zlib.compress(histogram)
				histrogram_compressed = histrogram_compressed.decode('utf-8', 'ignore')
				if not histrogram_compressed in aviso_json["photos"]:
					aviso_json["photos"].append(histrogram_compressed)
			
			# array_all_avisos_online.append(aviso_json)

			if number_of_avisos%1000==0:
				print str(number_of_avisos)
			
			number_of_avisos += 1

			self.con_mongo.ads_histograms_online_compressed.insert(aviso_json)

		return array_all_avisos_online

	def save_id_aviso_not_histogram_table(self, aviso_json):

		self.con_mongo.ads_similar.insert(aviso_json)


	def comptest(self, s):
		print 'original length:', len(s)
		print 'zlib compressed length:', len(zlib.compress(s))
		print 'bz2 compressed length:', len(bz2.compress(s))
		print 'zlib decompressed length:', len(zlib.decompress(s))
		print 'bz2 decompressed length:', len(bz2.decompress(s))

	# this method is responsible for selecting each photo of all avisos from ads_histograms collection
	# and find if it has any other equal histogram in that collection. The result will be a collection that
	# has all the ads that has at least one duplicated photo 
	def create_similar_photos_collection(self):

		start = time.time()

		number_of_avisos = 0
		
		#getting all avisos from histogram table in mongo 
		print "Retrieving all online avisos. Please, wait..."
		all_avisos = self.con_mongo.ads_histograms_online_compressed.find().sort([("id_aviso", 1)])
		print "[Ok]"

		for aviso in all_avisos:

			now = time.time()
			if number_of_avisos%1000==0:
				print str(number_of_avisos)
			
			number_of_avisos += 1
			aviso_has_similar_photos = False

			#json that will save the aviso that has duplicated photos
			id_aviso = aviso.get("id_aviso")
			photos = aviso.get("photos")  

			number_of_photos = len(photos)          
			aviso_json = {"id": id_aviso, "ph":[], "np":number_of_photos}

			#iterating in all photos of the ad
			for photo in photos:

				# print 'photo\n\n'
				# print photo

				is_photo_similar = False                
				
				#json that will save the data of the main photo that is being compared
				main_photo_json = {"sp":[]}

				#finding photos with the same histogram
				formated_id_aviso = format(int(id_aviso), "010")

				#improve this query: 1. remove $ne 2. Create Index for histogram field
				# self.comptest(photo.get("histogram"))
				equals_avisos = self.con_mongo.ads_histograms_online_compressed.find({"photos":photo,"id_aviso":{"$ne":id_aviso}}).sort([("photos", 1)])
				#iterate in all avisos that have some photo with the same histogram

				for other_aviso in equals_avisos:

					#getting all photos of the aviso that is being compared
					photos_compare = other_aviso.get("photos")

					#iterating in all photos to verify which one has the same histogram
					for photo_compare in photos_compare:

						# print 'photo_compare\n\n'
						# print photo_compare
						
						#verifying if the photo has the same histogram, excluding photos of the same aviso
						if photo==photo_compare:
							#json that saves the data of the similar photo that will be saved in similar_photos[] of main_photo_json
							similar_photo_json = {"s":other_aviso.get("id_aviso")}
							main_photo_json["sp"].append(similar_photo_json)
							aviso_has_similar_photos = True
							is_photo_similar = True

				
				#saves main_photo_json if exists a photo inside the other aviso that is equal to the aviso main photo

				if is_photo_similar:
					aviso_json["ph"].append(main_photo_json);		

			#saves in mongo the aviso json if there is any photo that has others equal photos 
			if aviso_has_similar_photos:
				try:
					self.con_mongo.ads_similar.insert(aviso_json)
				except:
					print aviso_json
					pass

		print "[OK] Analized " + str(number_of_avisos) + " avisos and 'ads_similar' collection created."
	

	def is_aviso_online(self,aviso_id):

		aviso_online = self.con_mongo.avisosonline_2.find({"idaviso":int(aviso_id)}).count()

		if aviso_online > 0:
			return True

		return False

	def create_equals_avisos_collection(self):

		start = time.time()
		number_of_similar_aviso_analyzed = 0

		done = False
		skip = 0

		while not done:
			
			try: 
				print "Searching in ads_similar collection..."
				all_similar_avisos = self.con_mongo.ads_similar.find().sort([("id", 1)]).skip(skip)
				print "[Ok]" 

				#iterating in all avisos that has duplicated images
			
				for similar_aviso in all_similar_avisos:
					skip += 1
					
					photos = similar_aviso.get("ph")
					number_of_photos_similar_aviso = similar_aviso.get("np")

					unique_similar_avisos = []

					#jsoin that will save all equal avisos, where "equal avisos" represents avisos where the group of its photos is 90% equal
					aviso_json = {"id":similar_aviso.get("id"),"eq":[]} #equal_avisos

					number_of_similar_aviso_analyzed += 1

					# if number_of_similar_aviso_analyzed%1==0:
					now = time.time()
					print str(number_of_similar_aviso_analyzed) + " - " + str(now-start) + " - " + str(similar_aviso.get("id"))

					for photo in photos:

						#getting all similar photos
						similar_photos = photo.get("sp")

						for similar_photo in similar_photos:

							similar_id_aviso = similar_photo.get("s")
							similar_aviso_already_on_array = False
							
							#iterating all unique similar_avisos
							for index, unique_similar_aviso in enumerate(unique_similar_avisos, start=0):
								
								#if similar_id_aviso already exists in json
								if unique_similar_aviso.get("id")==similar_id_aviso:
									similar_aviso_already_on_array = True
									unique_similar_avisos[index]['npe'] += 1
									number_total_photos_parent = unique_similar_avisos[index]['npp']

									#calculating the % of similarity of the group of photos between the aviso and the aviso that has similar photos
									percentage_of_similar = utils.percentage(unique_similar_avisos[index]['npe'],number_total_photos_parent)

									unique_similar_avisos[index]['pssp'] = int(percentage_of_similar) #ppercentage_similar_self_parent
									
							#did not find any similar id_aviso or the array is empty
							if not similar_aviso_already_on_array:      

								try:

									skip_compare = 0
									done_compare = False

									while not done_compare:
										similar_avisos_support = self.con_mongo.ads_similar.find({"id":similar_id_aviso}, {"np": 1}, no_cursor_timeout=False).sort([("np", 1)]).batch_size(100).skip(skip_compare)

										for similar_aviso_support in similar_avisos_support:

											skip_compare += 1

											number_of_ads_similar = similar_aviso_support.get("np")
											percentage_of_similar = utils.percentage(1,number_of_ads_similar)

											similar_aviso_json = {"id":similar_id_aviso,
											"npe":1, #"num_photos_equal":1,
											"npt": number_of_ads_similar, #"num_photos_total": number_of_ads_similar,
											"npp":number_of_photos_similar_aviso, #"num_photos_parent":number_of_ads_similar,
											"pssp": int(percentage_of_similar), #"percentage_similar_self_parent": int(percentage_of_similar),
											}
											
											#adding the similar aviso with the percentage of the similarity between the photos of both avisos
											unique_similar_avisos.append(similar_aviso_json)
										done_compare = True
									
								except:
									pass


					only_equal_avisos = []

					# print 'unique_similar_avisos: ' + str(similar_aviso.get("id"))
					# print unique_similar_avisos

					# adding to json only ads that have more than 90% of similarity in the group of both photos
					for unique_similar_aviso in unique_similar_avisos:

						percentage_number_of_photos = utils.percentage(unique_similar_aviso['npp'],unique_similar_aviso['npt'])
						
						#checkinf if the aviso being compared to main_aviso has similar number of photos
						if percentage_number_of_photos>=90 and percentage_number_of_photos<=100:
							if unique_similar_aviso['pssp']>90:
								aviso_json["eq"].append(unique_similar_aviso) #equal_avisos
							
					#inserting in mongo the collection of equals avisos
					if len(aviso_json["eq"]) > 0:
						self.con_mongo.ads_pre_equals.insert(aviso_json)


				done = True
			except:
				print "First exception"
				pass

		print "[OK] Analized " + str(number_of_similar_aviso_analyzed) + " avisos and 'ads_equals' collection created."

	def create_raw_equal_avisos(self):
		
		start = time.time()

		all_duplicated_avisos = self.con_mongo.ads_pre_equals.find().sort([("id", 1)])

		number_of_similar_aviso_analyzed = 0

		for duplicated_aviso in all_duplicated_avisos:
				
			raw_equal_avisos = []

			# raw_equal_avisos.append(duplicated_aviso.get("id"))
			# set(x) == set(y)

			equal_avisos = duplicated_aviso.get("eq")

			for equal_aviso in equal_avisos:

				raw_equal_avisos.append(equal_aviso.get("id"))

			number_of_similar_aviso_analyzed += 1

			if number_of_similar_aviso_analyzed%100==0:
				print str(number_of_similar_aviso_analyzed)

			rea = list(raw_equal_avisos)
			rea.append(duplicated_aviso.get("id"))


			self.con_mongo.ads_pre_equals.update({"id" :duplicated_aviso.get("id")},{'$set' : {"ree":raw_equal_avisos, "rea":rea}}) #raw_equal_avisos

		print "[OK] Created the raw fields of duplicated ads."


	def create_duplicateds_group_collection_new(self):

		done = False
		skip = 0
		number_of_similar_aviso_analyzed = 0
		all_failed_ids = []

		while not done:
			
			print "Searching..."
			
			all_duplicated_avisos = self.con_mongo.ads_pre_equals.find(no_cursor_timeout=False).sort([("id", 1)]).skip(skip)
			print "[Ok]"

			all_equals_json = []

			all_avisos = 0

			printer = False

			avisos_added = []

			try:

				for duplicated_aviso in all_duplicated_avisos:

					skip += 1

					number_of_similar_aviso_analyzed += 1
					
					if number_of_similar_aviso_analyzed%1==0:
						utils.print_inline(str(number_of_similar_aviso_analyzed) + "-")


					aviso_already_analized = False
					some_equal = False

					number_of_grouped = 0;

					rea = duplicated_aviso.get("rea")

					#json that saves the raw_equal_avisos and the avisos[] that have this respective raw
					

					#adding the aviso that is being analized aviso to avisos[] array
					# grouped_equal_avisos["avisos"].append(duplicated_aviso.get("id_aviso"))

					already_added = False

					for aviso_id in rea:
						if aviso_id in avisos_added:
							already_added = True
							break
					
					if not already_added:
						grouped_equal_avisos = {"rea":rea} #raw_equal_avisos
						self.con_mongo.ads_equals_grouped.insert(grouped_equal_avisos)
						for aviso_id in rea:
							avisos_added.append(aviso_id)
					
					
				done = True
			except pymongo.errors.OperationFailure, e:
				msg = e.message
				print msg
				print "first except: " + str(duplicated_aviso.get("id"))
				all_failed_ids.append(str(duplicated_aviso.get("id")))
				pass

		print "[OK] Created final collection for duplicated avisos."
		print 'all_failed_ids: '
		print all_failed_ids

	def validate_grouped_equals(self):

		skip_compare = 0
		done_compare = False
		number_of_similar_aviso_analyzed = 0

		while not done_compare:

			equals_avisos = self.con_mongo.ads_rea.find().sort([("rea", 1)]).skip(skip_compare)

		
			for equal_aviso in equals_avisos:

				number_of_similar_aviso_analyzed += 1

				if number_of_similar_aviso_analyzed%10==0:
					print str(number_of_similar_aviso_analyzed)

				skip_compare += 1

				array_rea = equal_aviso.get("rea")

				for aviso_id in array_rea:

				
					equals_avisos_grouped = self.con_mongo.ads_rea.find({"rea":{"$in":[aviso_id]}}).sort([("rea", 1)]).count()

					# print "== " + str(equals_avisos_grouped)
				
					if int(equals_avisos_grouped) > 1:
						print equal_aviso.get("id")


			done_compare = True
		print "[ok]"

	def check_differents(self):

		skip_compare = 0
		done_compare = False
		number_of_similar_aviso_analyzed = 0

		while not done_compare:

			equals_avisos = self.con_mongo.snippets_snippet.find().sort([("rea", 1)]).skip(skip_compare)

		
			for equal_aviso in equals_avisos:

				number_of_similar_aviso_analyzed += 1

				if number_of_similar_aviso_analyzed%10==0:
					print str(number_of_similar_aviso_analyzed)

				skip_compare += 1

				array_rea = equal_aviso.get("rea")

				equals_avisos_grouped = self.con_mongo.ads_rea.find({"rea":{"$in":array_rea}}).sort([("rea", 1)]).count()
				
				if int(equals_avisos_grouped) < 1:
					print array_rea
				
				# for aviso_id in array_rea:

				
				# 	equals_avisos_grouped = self.con_mongo.ads_rea.find({"rea":{"$in":[aviso_id]}}).sort([("rea", 1)]).count()

				# 	# print "== " + str(equals_avisos_grouped)
				
				# 	if int(equals_avisos_grouped) > 1:
				# 		print equal_aviso.get("id")

			done_compare = True
		print "[ok]"
								


