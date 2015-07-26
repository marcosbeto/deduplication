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

	def save_compressed_histogram_online(self):

		number_of_avisos = 0

		array_all_avisos_online = []		
		all_avisos_online = self.con_mongo.ads_histograms_online.find()

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

			self.con_mongo.ads_histograms_online_compressed_new.insert(aviso_json)

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
		all_avisos = self.con_mongo.ads_histograms_online_compressed_new.find()
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
				equals_avisos = self.con_mongo.ads_histograms_online_compressed_new.find({"photos":photo,"id_aviso":{"$ne":id_aviso}}).sort([("photos", 1)])
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
					self.con_mongo.ads_similar_new.insert(aviso_json)
				except:
					print aviso_json
					pass

		print "[OK] Analized " + str(number_of_avisos) + " avisos and 'ads_similar' collection created."
	

	def is_aviso_online(self,aviso_id):

		aviso_online = self.con_mongo.avisosonline.find({"idaviso":int(aviso_id)}).count()

		if aviso_online > 0:
			return True

		return False

	def create_equals_avisos_collection(self):

		start = time.time()
		number_of_similar_aviso_analyzed = 0

		done = False
		skip = 0

		while not done:
		
			print "Searching in ads_similar collection..."
			all_similar_avisos = self.con_mongo.ads_similar_new.find().sort([("id", 1)]).skip(skip)
			print "[Ok]"

			#iterating in all avisos that has duplicated images
			for similar_aviso in all_similar_avisos:
				skip += 1
				
				photos = similar_aviso.get("ph")
				number_of_photos_similar_aviso = similar_aviso.get("np")

				# number_of_photos_similar_aviso_lt = 0
				# number_of_photos_similar_aviso_gt = 0

				# if number_of_photos_similar_aviso > 3:
				# 	number_of_photos_similar_aviso_lt = (90*number_of_photos_similar_aviso)/100
				# 	number_of_photos_similar_aviso_gt = (100*number_of_photos_similar_aviso)/100
				# 	print 'number_of_photos_similar_aviso_lt: ' + str(number_of_photos_similar_aviso_lt)
				# 	print 'number_of_photos_similar_aviso_gt: ' + str(number_of_photos_similar_aviso_gt)


				unique_similar_avisos = []

				#jsoin that will save all equal avisos, where "equal avisos" represents avisos where the group of its photos is 90% equal
				aviso_json = {"id":similar_aviso.get("id"),"eq":[]} #equal_avisos

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

								#searching for a similar avisos inside similar photos that have the same number of photo of the main aviso that is being searched
								# if number_of_photos_similar_aviso_lt == 0 or number_of_photos_similar_aviso_gt == 0:
								# 	similar_avisos_support = self.con_mongo.ads_similar_new.find({"id":similar_id_aviso, "np":number_of_photos_similar_aviso},no_cursor_timeout=False).sort([("id", 1)]).batch_size(100)
								# else:
								# 	similar_avisos_support = self.con_mongo.ads_similar_new.find({"id":similar_id_aviso, "np" : { "$gt" :  number_of_photos_similar_aviso_lt, "$lt" : number_of_photos_similar_aviso_gt}},no_cursor_timeout=False).sort([("id", 1)]).batch_size(100)
							
								skip_compare = 0
								done_compare = False

								while not done_compare:
									similar_avisos_support = self.con_mongo.ads_similar_new.find({"id":similar_id_aviso},no_cursor_timeout=False).sort([("id", 1)]).batch_size(100).skip(skip_compare)

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
								print "passou"
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
					self.con_mongo.ads_pre_equals_new.insert(aviso_json)

				number_of_similar_aviso_analyzed += 1

				if number_of_similar_aviso_analyzed%100==0:
					now = time.time()
					print str(number_of_similar_aviso_analyzed) + " - " + str(now-start)

			done = True

		print "[OK] Analized " + str(number_of_similar_aviso_analyzed) + " avisos and 'ads_equals' collection created."

	def create_raw_equal_avisos(self):
		
		start = time.time()

		all_duplicated_avisos = self.con_mongo.ads_pre_equals_new_copy.find().sort([("id", 1)])

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


			self.con_mongo.ads_pre_equals_new_copy.update({"id" :duplicated_aviso.get("id")},{'$set' : {"ree":raw_equal_avisos}}) #raw_equal_avisos

		print "[OK] Created the raw fields of duplicated ads."


	def create_duplicateds_group_collection(self):


		done = False
		skip = 0
		number_of_similar_aviso_analyzed = 0
		all_failed_ids = []

		while not done:
			
			print "Searching..."
			
			all_duplicated_avisos = self.con_mongo.ads_pre_equals_new_copy.find(no_cursor_timeout=False).sort([("id", 1)]).skip(skip)
			print "[Ok]"

			all_equals_json = []

			all_avisos = 0

			printer = False

			try:

				for duplicated_aviso in all_duplicated_avisos:

					skip += 1

					number_of_similar_aviso_analyzed += 1
					
					if number_of_similar_aviso_analyzed%1==0:
						utils.print_inline(str(number_of_similar_aviso_analyzed) + "-")


					aviso_already_analized = False
					some_equal = False

					number_of_grouped = 0;

					#json that saves the raw_equal_avisos and the avisos[] that have this respective raw
					grouped_equal_avisos = {"avisos":[],"rea":duplicated_aviso.get("rea")} #raw_equal_avisos

					#adding the aviso that is being analized aviso to avisos[] array
					# grouped_equal_avisos["avisos"].append(duplicated_aviso.get("id_aviso"))
					
					for compared_aviso in all_equals_json:

						group_avisos_duplicated = compared_aviso.get("avisos")
						
						for aviso_duplicated in group_avisos_duplicated:
							
							if duplicated_aviso.get("id") == aviso_duplicated.get("id"):
								aviso_already_analized = True
								# print "aviso_already_analized = TRUE"


					if not aviso_already_analized:

						skip_compare = 0
						done_compare = False

						while not done_compare:

							all_duplicated_avisos_compare = self.con_mongo.ads_pre_equals_new_copy.find().sort([("id", 1)]).skip(skip_compare)

							#iterating in other avisos to see if there is a raw avisos equal to group them
							try:
								for duplicated_aviso_compare in all_duplicated_avisos_compare:

									skip_compare += 1

									#checking if they have the same raw
									if duplicated_aviso_compare.get("rea")!=None and duplicated_aviso.get("rea")!=None and set(duplicated_aviso_compare.get("rea")) == set(duplicated_aviso.get("rea")):
										some_equal = True
										#if they are different ads add to avisos[] array of avisos with the same raw
										#if duplicated_aviso.get("id_aviso") != duplicated_aviso_compare.get("id_aviso"):
										grouped_equal_avisos["avisos"].append({"id":duplicated_aviso_compare.get("id"),"url":""})
								done_compare = True
							except pymongo.errors.OperationFailure, e:
								msg = e.message
								print msg
								print "first except: " + str(duplicated_aviso.get("id"))
								all_failed_ids.append(str(duplicated_aviso.get("id")))
								pass

					all_avisos += 1
					
					if some_equal:
						try:
							all_equals_json.append(grouped_equal_avisos)
							self.con_mongo.ads_equals_grouped_new.insert(grouped_equal_avisos)
						except:
							print "second except: " + str(duplicated_aviso.get("id"))
							all_failed_ids.append(str(duplicated_aviso.get("id")))
							pass
				done = True
			except pymongo.errors.OperationFailure, e:
				msg = e.message
				print msg
				print "thirdr except: " + str(duplicated_aviso.get("id"))
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

			equals_avisos = self.con_mongo.ads_pre_equals_new_copy.find().sort([("id", 1)]).skip(skip_compare)

		
			for equal_aviso in equals_avisos:

				number_of_similar_aviso_analyzed += 1

				if number_of_similar_aviso_analyzed%10==0:
					print str(number_of_similar_aviso_analyzed)

				skip_compare += 1

				array_rea = equal_aviso.get("rea")

				# for aviso_id in array_rea:

				
				equals_avisos_grouped = self.con_mongo.ads_equals_grouped_new.find({"rea":{"$in":array_rea}}).sort([("id", 1)]).count()

				print "== " + str(equals_avisos_grouped)
				
				if int(equals_avisos_grouped) != 1:
					print equal_aviso.get("id")


			done_compare = True

		
	def validate_arr(self):
		ar1 = [
		    918534431,
		    918537294,
		    918645061,
		    918658071,
		    918696681,
		    918823531,
		    918974111,
		    919007271,
		    919380414,
		    919439551,
		    919838021,
		    920115661,
		    920115671,
		    920317771,
		    920317781,
		    920537231,
		    920594971,
		    1000027018,
		    1000093744,
		    1000098845,
		    1000107142,
		    1000107144,
		    1000107145,
		    1000111672,
		    1000122757,
		    1000124388,
		    1000144770,
		    1000152367,
		    1000152368,
		    1000152459,
		    1000154049,
		    1000159669,
		    1000161495,
		    1000163013,
		    1000168551,
		    1000169462,
		    1000169628,
		    1000169727,
		    1000169858,
		    1000170425,
		    1000175785,
		    1000177757,
		    1000181654,
		    1000182022,
		    1000182352,
		    1000185636,
		    1000185641,
		    1000185642,
		    1000195046,
		    1000195077,
		    1000199358,
		    1000199671,
		    1000200423,
		    1000200863,
		    1000201023,
		    1000203626,
		    1000205003,
		    1000205712,
		    1000205749,
		    1000207348,
		    1000207386,
		    1000207491,
		    1000207549,
		    1000214952,
		    1000215424,
		    1000216028,
		    1000216367,
		    1000226642,
		    1000227011,
		    1000227143,
		    1000227347,
		    1000227402,
		    1000227868,
		    1000228089,
		    1000228709,
		    1000231652,
		    1000231653,
		    1000231671,
		    1000231689,
		    1000232434,
		    1000232452,
		    1000233569,
		    1000234023,
		    1000234614,
		    1000235611,
		    1000236126,
		    1000236201,
		    1000236418,
		    1000236477,
		    1000236586,
		    1000236587,
		    1000236892,
		    1000236899,
		    1000245417,
		    1000245716,
		    1000245885,
		    1000246130,
		    1000247363,
		    1000247909,
		    1000248475,
		    1000249344,
		    1000251289,
		    1000252146,
		    1000255576,
		    1000255675,
		    1000256691,
		    1000256817,
		    1000256981,
		    1000257269,
		    1000257277,
		    1000257380,
		    1000257478,
		    1000257917,
		    1000257925,
		    1000257955,
		    1000257958,
		    1000257967,
		    1000257979,
		    1000257995,
		    1000258048,
		    1000258069,
		    1000258153,
		    1000258186,
		    1000258242,
		    1000260386,
		    1000260526,
		    1000260553,
		    1000264220,
		    1000264310,
		    1000264591,
		    1000265242,
		    1000265560,
		    1000265755,
		    1000266079,
		    1000266106,
		    1000267182,
		    1000268273,
		    1000269715,
		    1000271649,
		    1000271756,
		    1000272850,
		    1000274401,
		    1000274463,
		    1000274553,
		    1000274683,
		    1000274858,
		    1000275729,
		    1000282897,
		    1000288370,
		    1000288371,
		    1000288374,
		    1000288375,
		    1000288376,
		    1000288391,
		    1000288392,
		    1000288393,
		    1000288395,
		    1000288396,
		    1000288398,
		    1000288404,
		    1000288405,
		    1000288408,
		    1000288410,
		    1000288412,
		    1000288414,
		    1000288418,
		    1000288420,
		    1000288421,
		    1000288422,
		    1000288423,
		    1000288424,
		    1000288425,
		    1000288429,
		    1000288430,
		    1000288433,
		    1000288435,
		    1000288436,
		    1000288439,
		    1000288442,
		    1000288443,
		    1000288444,
		    1000288446,
		    1000288447,
		    1000288449,
		    1000288453,
		    1000288454,
		    1000288466,
		    1000288472,
		    1000288474,
		    1000288475,
		    1000288477,
		    1000288482,
		    1000288483,
		    1000288484,
		    1000288494,
		    1000288496,
		    1000288499,
		    1000288501,
		    1000288502,
		    1000288503,
		    1000288504,
		    1000288505,
		    1000288507,
		    1000288508,
		    1000288511,
		    1000288512,
		    1000288513,
		    1000288515,
		    1000288516,
		    1000288517,
		    1000289624,
		    1000289735,
		    1000290124,
		    1000290133,
		    1000290160,
		    1000291224,
		    1000291398,
		    1000291466,
		    1000291489,
		    1000291626,
		    1000291689,
		    1000293111,
		    1000293114,
		    1000293115,
		    1000294892,
		    1000294893,
		    1000294980,
		    1000295689,
		    1000297377,
		    1000297453,
		    1000297904,
		    1000297982,
		    1000300098,
		    1000300590,
		    1000300752,
		    1000300832,
		    1000301167,
		    1000301474,
		    1000302531,
		    1000302940,
		    1000303884,
		    1000303999,
		    1000304637,
		    1000305204,
		    1000306556,
		    1000306909,
		    1000308291,
		    1000308292,
		    1000308716,
		    1000309716,
		    1000311075,
		    1000311086,
		    1000311093,
		    1000311118,
		    1000311132,
		    1000311149,
		    1000311154,
		    1000311301,
		    1000311322,
		    1000311339,
		    1000311374,
		    1000311697,
		    1000315616,
		    1000315793,
		    1000317954,
		    1000318592,
		    1000318629,
		    1000321750,
		    1000322471,
		    1000322551,
		    1000322592,
		    1000322786,
		    1000323439,
		    1000326035,
		    1000326562,
		    1000327302,
		    1000327869,
		    1000331324,
		    1000334680,
		    1000334866,
		    1000334885,
		    1000335346,
		    1000337837,
		    1000338037,
		    1000338365,
		    1000338711,
		    1000339258,
		    1000339353,
		    1000339661,
		    1000340351,
		    1000342604,
		    1000344409,
		    1000344991,
		    1000346143,
		    1000346863,
		    1000347978,
		    1000349168,
		    1000353176,
		    1000353188,
		    1000353380,
		    1000353557,
		    1000354665,
		    1000368935,
		    1000369292,
		    1000369780,
		    1000370113,
		    1000377682,
		    1000377683,
		    1000381406,
		    1000382028,
		    1000385550,
		    1000393794,
		    1000394169,
		    1000397018,
		    1000397645,
		    1000397739,
		    1000403531,
		    1000407517,
		    1000407519,
		    1000407619,
		    1000408983,
		    1000409446,
		    1000409494,
		    1000409850,
		    1000417977,
		    1000423311,
		    1000426581,
		    1000426812,
		    1000427478,
		    1000427577,
		    1000428571,
		    1000432277,
		    1000433401,
		    1000441301,
		    1000442447,
		    1000442472,
		    1000465890,
		    1000465893,
		    1000468485,
		    1000468489,
		    1000468500,
		    1000483656,
		    1000506218,
		    1000506288,
		    1000506289,
		    1000506291,
		    1000506298,
		    1000506305,
		    1000559835,
		    1000606794,
		    1000606798,
		    1000606802,
		    1000606803,
		    1000606810,
		    1000616420,
		    1000623240,
		    1000625558,
		    1000627287,
		    1000629583,
		    1000629586,
		    1000629793,
		    1000629823,
		    1000629842,
		    1000637956,
		    1000644961,
		    1000654426,
		    1000654984,
		    1000654987,
		    1000663092,
		    1000667484,
		    1000668306,
		    1000672895,
		    1000674472,
		    1000675485,
		    1000675902,
		    1000680827,
		    1000680828,
		    1000680829,
		    1000682315,
		    1000684821,
		    1000685518,
		    1000686100,
		    1000686485,
		    1000686991,
		    1000688390,
		    1000688691,
		    1000689583,
		    1000691536,
		    1000691537,
		    1000691539,
		    1000692854,
		    1000693686,
		    1000694673,
		    1000696919,
		    1000697507,
		    1000703013,
		    1000706925,
		    1000712420,
		    1000721901,
		    1000725119,
		    1000730319,
		    1000731653,
		    1000732422,
		    1000739178,
		    1000740536,
		    1000742430,
		    1000742846,
		    1000746555,
		    1000747817,
		    1000754584,
		    1000754652,
		    1000756679,
		    1000756736,
		    1000758127,
		    1000758496,
		    1000758563,
		    1000764442,
		    1000768069,
		    1000768098,
		    1000783910,
		    1000784125,
		    1000784185,
		    1000784479,
		    1000785869,
		    1000785938,
		    1000789661,
		    1000792904,
		    1000792981,
		    1000793097,
		    1000793284,
		    1000809224,
		    1000809311,
		    1000809645,
		    1000809943,
		    1000810171,
		    1000810844,
		    1000810884,
		    1000810935,
		    1000819398,
		    1000821798,
		    1000822754,
		    1000825847,
		    1000825857,
		    1000826940,
		    1000831239,
		    1000862108,
		    1000864328,
		    1000864335,
		    1000864340,
		    1000885774,
		    1000885959,
		    1000886181,
		    1000895173,
		    1000945510,
		    1000968375,
		    1001003565,
		    1001006550,
		    1001006553,
		    1001006561,
		    1001006562,
		    1001097749,
		    1001151607,
		    1001152457,
		    1001158302,
		    1001239367,
		    1001350125,
		    1001353479,
		    1001368043,
		    1001408723,
		    1001408746,
		    1001425003,
		    1001425019,
		    1001425104,
		    1001425141,
		    1001425155,
		    1001425297,
		    1001425487,
		    1001425775,
		    1001473325,
		    1001473338,
		    1001491957,
		    1001523771,
		    1001531536,
		    1001537894,
		    1001538021,
		    1001538227,
		    1001539600,
		    1001671288,
		    1001671466,
		    1001679217,
		    1001679550,
		    1001699707,
		    1001719918,
		    1001745835,
		    1001745846,
		    1001745851,
		    1001745853,
		    1001745863,
		    1001745867,
		    1001745877,
		    1001745881,
		    1001748018,
		    43115253,
		    47112690,
		    48112886,
		    53099379,
		    53099397,
		    53116713,
		    55105904,
		    57106823,
		    59111236,
		    59111237,
		    59113476,
		    60113529,
		    62117598,
		    64116245,
		    64116264,
		    65095984,
		    65121568,
		    69113655,
		    82358215,
		    82358218,
		    84281476,
		    84292406,
		    95980104,
		    900380384,
		    900810911,
		    913627931,
		    913718154,
		    913838261,
		    914113701,
		    914116381,
		    914196731,
		    914220571,
		    914220901,
		    914229721,
		    914229801,
		    914229821,
		    914229941,
		    914230011,
		    914230161,
		    914300851,
		    914301001,
		    914414431,
		    914415321,
		    914415411,
		    914416111,
		    914416281,
		    914416591,
		    914416851,
		    914530841,
		    914596761,
		    914596791,
		    914596801,
		    914673451,
		    914673461,
		    914865621,
		    914865641,
		    914868911,
		    914961451,
		    915238961,
		    915262581,
		    915597521,
		    915996571,
		    916016071,
		    916368151,
		    916386041,
		    916485731,
		    916544801,
		    916793081,
		    917090061,
		    917090151,
		    917591831,
		    917939031,
		    917939041,
		    917939071,
		    917939121,
		    1001756184,
		    1001757131,
		    1001758764,
		    1001758766,
		    1001758767,
		    1001758770,
		    1001758785,
		    1001758787,
		    1001829619,
		    1001850932,
		    1001852806,
		    1001852808,
		    1001853085,
		    1001855742,
		    1001862109,
		    1001864655,
		    1001871148,
		    1001873419,
		    1001873567,
		    1001873595,
		    1001873612,
		    1001873675,
		    1001873682,
		    1001873909,
		    1001874238,
		    1001874369,
		    1001874374,
		    1001874475,
		    1001877154,
		    1001899573,
		    1001900857,
		    1001922228,
		    1001928925,
		    1001956453,
		    1001960324,
		    1001960327,
		    1001960329,
		    1002039363,
		    1002069749,
		    1002071644,
		    1002083532,
		    1002091303,
		    1002093023,
		    1002093907,
		    1002114167,
		    1002114170,
		    1002121686,
		    1002132337,
		    1002134818,
		    1002134825,
		    1002142487,
		    1002143536,
		    1002146329,
		    1002146391,
		    1002161786,
		    1002228179,
		    1002228184,
		    1002228212,
		    1002228232,
		    1002237628,
		    1002260320,
		    1002260324,
		    1002264677,
		    1002266667,
		    1002266722,
		    1002267464,
		    1002306195,
		    1002306232,
		    1002308604,
		    1002314819,
		    1002314888,
		    1002314889,
		    1002314905,
		    1002314906,
		    1002314912,
		    1002314924,
		    1002314929,
		    1002314938,
		    1002314955,
		    1002314959,
		    1002314961,
		    1002314962,
		    1002314974,
		    1002314976,
		    1002314977,
		    1002314979,
		    1002336260,
		    1002336262,
		    1002336264,
		    1002337787,
		    1002337803,
		    1002337864,
		    1002337872,
		    1002357677,
		    1002357690,
		    1002399433,
		    1002405373,
		    1002416847,
		    1002417135,
		    1002417138,
		    1002425337,
		    1002425483,
		    1002431042,
		    1002432177,
		    1002432184,
		    1002437275,
		    1002438208,
		    1002440044,
		    1002441523,
		    1002441547,
		    1002450456,
		    1002451614,
		    1002452192,
		    1002452205,
		    1002452212,
		    1002453800,
		    1002455988,
		    1002462595,
		    1002468082,
		    1002470417,
		    1002476963,
		    1002478999,
		    1002482579,
		    1002482580,
		    1002482581,
		    1002482588,
		    1002482589,
		    1002515551,
		    1002584210,
		    1002592907,
		    1002592909,
		    1002592910,
		    1002592911,
		    1002592912,
		    1002592913,
		    1002592914,
		    1002592915,
		    1002592916,
		    1002592917,
		    1002592918,
		    1002592919,
		    1002601441,
		    1002601442,
		    1002608276,
		    1002608312,
		    1002614444,
		    1002614445,
		    1002614446,
		    1002614447,
		    1002614452,
		    1002614453,
		    1002614454,
		    1002614456,
		    1002625926,
		    1002631053,
		    1002654641,
		    1002688342,
		    1002689488,
		    1002721479,
		    1002724256,
		    1002727179,
		    1002729331,
		    1002731964,
		    1002731970,
		    1002747762,
		    1002750073,
		    1002753517,
		    1002789099,
		    1002801476,
		    1002801522,
		    1002809163,
		    1002815694,
		    1002815696,
		    1002815698,
		    1002815705,
		    1002815708,
		    1002815719,
		    1002815727,
		    1002815737,
		    1002815755,
		    1002815763,
		    1002815769,
		    1002815785,
		    1002815793,
		    1002815802,
		    1002815816,
		    1002815828,
		    1002815832,
		    1002815834,
		    1002815835,
		    1002815870,
		    1002815879,
		    1002815921,
		    1002815928,
		    1002818888,
		    1002829893,
		    1002831505,
		    1002844261,
		    1002844471,
		    1002845578,
		    1002845674,
		    1002847314,
		    1002847420,
		    1002847937,
		    1002847958,
		    1002849753,
		    1002852494,
		    1002852501,
		    1002852506,
		    1002852511,
		    1002852529,
		    1002852811,
		    1002860077,
		    1002862975,
		    1002862994,
		    1002863047,
		    1002863121,
		    1002863156,
		    1002868226,
		    1002868339,
		    1002868439,
		    1002868507,
		    1002868629,
		    1002868631,
		    1002868642,
		    1002868662,
		    1002868756,
		    1002868778,
		    1002879712,
		    1002898523,
		    1002902687,
		    1002911520,
		    1002914116,
		    1002920359,
		    1002943877,
		    1002943943,
		    1002947118,
		    1002956565,
		    1002959241,
		    1002959255,
		    1002959407,
		    1002959441,
		    1002959450,
		    1002959610,
		    1002963065,
		    1002963075,
		    1002969448,
		    1002969461,
		    1002969486,
		    1002971793,
		    1002971820,
		    1002971822,
		    1002977730,
		    1002984714,
		    1002985245,
		    1002986231,
		    1002987697,
		    1002993808,
		    1002993812,
		    1002993813,
		    1002993816,
		    1003005543,
		    1003005625,
		    1003016445,
		    1003020787,
		    1003020790,
		    1003022821,
		    1003042431,
		    1003042435,
		    1003042437,
		    1003045383,
		    1003049440,
		    1003053946,
		    1003054267,
		    1003054271,
		    1003062366,
		    1003062468,
		    1003062479,
		    1003066703,
		    1003066704,
		    1003066705,
		    1003080789,
		    1003098408,
		    1003098413,
		    1003100326,
		    1003100398,
		    1003100404,
		    1003100405,
		    1003100408,
		    1003100410,
		    1003100412,
		    1003100417,
		    1003106459,
		    1003106461,
		    1003165864,
		    1003165868,
		    1003165870,
		    1003165920,
		    1003172416,
		    1003185017,
		    1003185018,
		    1003185021,
		    1003185025,
		    1003185032,
		    1003185034,
		    1003185048,
		    1003185050,
		    1003185051,
		    1003185052,
		    1003185055,
		    1003185056,
		    1003185058,
		    1003185059,
		    1003185060,
		    1003185061,
		    1003185062,
		    1003185063,
		    1003185064,
		    1003185108,
		    1003185110,
		    1003185111,
		    1003197782,
		    1003198028,
		    1003198056,
		    1003226862,
		    1003226869,
		    1003227628,
		    1003227889,
		    1003229284,
		    1003229320,
		    1003229335,
		    1003244626,
		    1003474618,
		    NumberLong(2920833648),
		    NumberLong(2920833652),
		    NumberLong(2920833657),
		    NumberLong(2920833663),
		    NumberLong(2920833665),
		    NumberLong(2920833670),
		    NumberLong(2920833674),
		    NumberLong(2921390555)
		]

		ar2 = [
		    918534431,
		    918537294,
		    918645061,
		    918658071,
		    918696681,
		    918823531,
		    918974111,
		    919007271,
		    919380414,
		    919439551,
		    919838021,
		    920115661,
		    920115671,
		    920317771,
		    920317781,
		    920537231,
		    920594971,
		    1000027018,
		    1000093744,
		    1000098845,
		    1000107142,
		    1000107144,
		    1000107145,
		    1000111672,
		    1000122757,
		    1000124388,
		    1000144770,
		    1000152367,
		    1000152368,
		    1000152459,
		    1000154049,
		    1000159669,
		    1000161495,
		    1000163013,
		    1000168551,
		    1000169462,
		    1000169628,
		    1000169727,
		    1000169858,
		    1000170425,
		    1000175785,
		    1000177757,
		    1000181654,
		    1000182022,
		    1000182352,
		    1000185636,
		    1000185641,
		    1000185642,
		    1000195046,
		    1000195077,
		    1000199358,
		    1000199671,
		    1000200423,
		    1000200863,
		    1000201023,
		    1000203626,
		    1000205003,
		    1000205712,
		    1000205749,
		    1000207348,
		    1000207386,
		    1000207491,
		    1000207549,
		    1000214952,
		    1000215424,
		    1000216028,
		    1000216367,
		    1000226642,
		    1000227011,
		    1000227143,
		    1000227347,
		    1000227402,
		    1000227868,
		    1000228089,
		    1000228709,
		    1000231652,
		    1000231653,
		    1000231671,
		    1000231689,
		    1000232434,
		    1000232452,
		    1000233569,
		    1000234023,
		    1000234614,
		    1000235611,
		    1000236126,
		    1000236201,
		    1000236418,
		    1000236477,
		    1000236586,
		    1000236587,
		    1000236892,
		    1000236899,
		    1000245417,
		    1000245716,
		    1000245885,
		    1000246130,
		    1000247363,
		    1000247909,
		    1000248475,
		    1000249344,
		    1000251289,
		    1000252146,
		    1000255576,
		    1000255675,
		    1000256691,
		    1000256817,
		    1000256981,
		    1000257269,
		    1000257277,
		    1000257380,
		    1000257478,
		    1000257917,
		    1000257925,
		    1000257955,
		    1000257958,
		    1000257967,
		    1000257979,
		    1000257995,
		    1000258048,
		    1000258069,
		    1000258153,
		    1000258186,
		    1000258242,
		    1000260386,
		    1000260526,
		    1000260553,
		    1000264220,
		    1000264310,
		    1000264591,
		    1000265242,
		    1000265560,
		    1000265755,
		    1000266079,
		    1000266106,
		    1000267182,
		    1000268273,
		    1000269715,
		    1000271649,
		    1000271756,
		    1000272850,
		    1000274401,
		    1000274463,
		    1000274553,
		    1000274683,
		    1000274858,
		    1000275729,
		    1000282897,
		    1000288370,
		    1000288371,
		    1000288374,
		    1000288375,
		    1000288376,
		    1000288391,
		    1000288392,
		    1000288393,
		    1000288395,
		    1000288396,
		    1000288398,
		    1000288404,
		    1000288405,
		    1000288408,
		    1000288410,
		    1000288412,
		    1000288414,
		    1000288418,
		    1000288420,
		    1000288421,
		    1000288422,
		    1000288423,
		    1000288424,
		    1000288425,
		    1000288429,
		    1000288430,
		    1000288433,
		    1000288435,
		    1000288436,
		    1000288439,
		    1000288442,
		    1000288443,
		    1000288444,
		    1000288446,
		    1000288447,
		    1000288449,
		    1000288453,
		    1000288454,
		    1000288466,
		    1000288472,
		    1000288474,
		    1000288475,
		    1000288477,
		    1000288482,
		    1000288483,
		    1000288484,
		    1000288494,
		    1000288496,
		    1000288499,
		    1000288501,
		    1000288502,
		    1000288503,
		    1000288504,
		    1000288505,
		    1000288507,
		    1000288508,
		    1000288511,
		    1000288512,
		    1000288513,
		    1000288515,
		    1000288516,
		    1000288517,
		    1000289624,
		    1000289735,
		    1000290124,
		    1000290133,
		    1000290160,
		    1000291224,
		    1000291398,
		    1000291466,
		    1000291489,
		    1000291626,
		    1000291689,
		    1000293111,
		    1000293114,
		    1000293115,
		    1000294892,
		    1000294893,
		    1000294980,
		    1000295689,
		    1000297377,
		    1000297453,
		    1000297904,
		    1000297982,
		    1000300098,
		    1000300590,
		    1000300752,
		    1000300832,
		    1000301167,
		    1000301474,
		    1000302531,
		    1000302940,
		    1000303884,
		    1000303999,
		    1000304637,
		    1000305204,
		    1000306556,
		    1000306909,
		    1000308291,
		    1000308292,
		    1000308716,
		    1000309716,
		    1000311075,
		    1000311086,
		    1000311093,
		    1000311118,
		    1000311132,
		    1000311149,
		    1000311154,
		    1000311301,
		    1000311322,
		    1000311339,
		    1000311374,
		    1000311697,
		    1000315616,
		    1000315793,
		    1000317954,
		    1000318592,
		    1000318629,
		    1000321750,
		    1000322471,
		    1000322551,
		    1000322592,
		    1000322786,
		    1000323439,
		    1000326035,
		    1000326562,
		    1000327302,
		    1000327869,
		    1000331324,
		    1000334680,
		    1000334866,
		    1000334885,
		    1000335346,
		    1000337837,
		    1000338037,
		    1000338365,
		    1000338711,
		    1000339258,
		    1000339353,
		    1000339661,
		    1000340351,
		    1000342604,
		    1000344409,
		    1000344991,
		    1000346143,
		    1000346863,
		    1000347978,
		    1000349168,
		    1000353176,
		    1000353188,
		    1000353380,
		    1000353557,
		    1000354665,
		    1000368935,
		    1000369292,
		    1000369780,
		    1000370113,
		    1000377682,
		    1000377683,
		    1000381406,
		    1000382028,
		    1000385550,
		    1000393794,
		    1000394169,
		    1000397018,
		    1000397645,
		    1000397739,
		    1000403531,
		    1000407517,
		    1000407519,
		    1000407619,
		    1000408983,
		    1000409446,
		    1000409494,
		    1000409850,
		    1000417977,
		    1000423311,
		    1000426581,
		    1000426812,
		    1000427478,
		    1000427577,
		    1000428571,
		    1000432277,
		    1000433401,
		    1000441301,
		    1000442447,
		    1000442472,
		    1000465890,
		    1000465893,
		    1000468485,
		    1000468489,
		    1000468500,
		    1000483656,
		    1000506218,
		    1000506288,
		    1000506289,
		    1000506291,
		    1000506298,
		    1000506305,
		    1000559835,
		    1000606794,
		    1000606798,
		    1000606802,
		    1000606803,
		    1000606810,
		    1000616420,
		    1000623240,
		    1000625558,
		    1000627287,
		    1000629583,
		    1000629586,
		    1000629793,
		    1000629823,
		    1000629842,
		    1000637956,
		    1000644961,
		    1000654426,
		    1000654984,
		    1000654987,
		    1000663092,
		    1000667484,
		    1000668306,
		    1000672895,
		    1000674472,
		    1000675485,
		    1000675902,
		    1000680827,
		    1000680828,
		    1000680829,
		    1000682315,
		    1000684821,
		    1000685518,
		    1000686100,
		    1000686485,
		    1000686991,
		    1000688390,
		    1000688691,
		    1000689583,
		    1000691536,
		    1000691537,
		    1000691539,
		    1000692854,
		    1000693686,
		    1000694673,
		    1000696919,
		    1000697507,
		    1000703013,
		    1000706925,
		    1000712420,
		    1000721901,
		    1000725119,
		    1000730319,
		    1000731653,
		    1000732422,
		    1000739178,
		    1000740536,
		    1000742430,
		    1000742846,
		    1000746555,
		    1000747817,
		    1000754584,
		    1000754652,
		    1000756679,
		    1000756736,
		    1000758127,
		    1000758496,
		    1000758563,
		    1000764442,
		    1000768069,
		    1000768098,
		    1000783910,
		    1000784125,
		    1000784185,
		    1000784479,
		    1000785869,
		    1000785938,
		    1000789661,
		    1000792904,
		    1000792981,
		    1000793097,
		    1000793284,
		    1000809224,
		    1000809311,
		    1000809645,
		    1000809943,
		    1000810171,
		    1000810844,
		    1000810884,
		    1000810935,
		    1000819398,
		    1000821798,
		    1000822754,
		    1000825847,
		    1000825857,
		    1000826940,
		    1000831239,
		    1000862108,
		    1000864328,
		    1000864335,
		    1000864340,
		    1000885774,
		    1000885959,
		    1000886181,
		    1000895173,
		    1000945510,
		    1000968375,
		    1001003565,
		    1001006550,
		    1001006553,
		    1001006561,
		    1001006562,
		    1001097749,
		    1001151607,
		    1001152457,
		    1001158302,
		    1001239367,
		    1001350125,
		    1001353479,
		    1001368043,
		    1001408723,
		    1001408746,
		    1001425003,
		    1001425019,
		    1001425104,
		    1001425141,
		    1001425155,
		    1001425297,
		    1001425487,
		    1001425775,
		    1001473325,
		    1001473338,
		    1001491957,
		    1001523771,
		    1001531536,
		    1001537894,
		    1001538021,
		    1001538227,
		    1001539600,
		    1001671288,
		    1001671466,
		    1001679217,
		    1001679550,
		    1001699707,
		    1001719918,
		    1001745835,
		    1001745846,
		    1001745851,
		    1001745853,
		    1001745863,
		    1001745867,
		    1001745877,
		    1001745881,
		    1001748018,
		    43115253,
		    47112690,
		    48112886,
		    53099379,
		    53099397,
		    53116713,
		    55105904,
		    57106823,
		    59111236,
		    59111237,
		    59113476,
		    60113529,
		    62117598,
		    64116245,
		    64116264,
		    65095984,
		    65121568,
		    69113655,
		    82358215,
		    82358218,
		    84281476,
		    84292406,
		    95980104,
		    900380384,
		    900810911,
		    913627931,
		    913718154,
		    913838261,
		    914113701,
		    914116381,
		    914196731,
		    914220861,
		    914220901,
		    914229721,
		    914229801,
		    914229821,
		    914229941,
		    914230011,
		    914230161,
		    914300851,
		    914301001,
		    914414431,
		    914415321,
		    914415411,
		    914416111,
		    914416281,
		    914416591,
		    914416851,
		    914530841,
		    914596761,
		    914596791,
		    914596801,
		    914673451,
		    914673461,
		    914865621,
		    914865641,
		    914868911,
		    914961451,
		    915238961,
		    915262581,
		    915597521,
		    915996571,
		    916016071,
		    916368151,
		    916386041,
		    916485731,
		    916544801,
		    916793081,
		    917090061,
		    917090151,
		    917591831,
		    917939031,
		    917939041,
		    917939071,
		    917939121,
		    1001756184,
		    1001757131,
		    1001758764,
		    1001758766,
		    1001758767,
		    1001758770,
		    1001758785,
		    1001758787,
		    1001829619,
		    1001850932,
		    1001852806,
		    1001852808,
		    1001853085,
		    1001855742,
		    1001862109,
		    1001864655,
		    1001871148,
		    1001873419,
		    1001873567,
		    1001873595,
		    1001873612,
		    1001873675,
		    1001873682,
		    1001873909,
		    1001874238,
		    1001874369,
		    1001874374,
		    1001874475,
		    1001877154,
		    1001899573,
		    1001900857,
		    1001922228,
		    1001928925,
		    1001956453,
		    1001960324,
		    1001960327,
		    1001960329,
		    1002039363,
		    1002069749,
		    1002071644,
		    1002083532,
		    1002091303,
		    1002093023,
		    1002093907,
		    1002114167,
		    1002114170,
		    1002121686,
		    1002132337,
		    1002134818,
		    1002134825,
		    1002142487,
		    1002143536,
		    1002146329,
		    1002146391,
		    1002161786,
		    1002228179,
		    1002228184,
		    1002228212,
		    1002228232,
		    1002237628,
		    1002260320,
		    1002260324,
		    1002264677,
		    1002266667,
		    1002266722,
		    1002267464,
		    1002306195,
		    1002306232,
		    1002308604,
		    1002314819,
		    1002314888,
		    1002314889,
		    1002314905,
		    1002314906,
		    1002314912,
		    1002314924,
		    1002314929,
		    1002314938,
		    1002314955,
		    1002314959,
		    1002314961,
		    1002314962,
		    1002314974,
		    1002314976,
		    1002314977,
		    1002314979,
		    1002336260,
		    1002336262,
		    1002336264,
		    1002337787,
		    1002337803,
		    1002337864,
		    1002337872,
		    1002357677,
		    1002357690,
		    1002399433,
		    1002405373,
		    1002416847,
		    1002417135,
		    1002417138,
		    1002425337,
		    1002425483,
		    1002431042,
		    1002432177,
		    1002432184,
		    1002437275,
		    1002438208,
		    1002440044,
		    1002441523,
		    1002441547,
		    1002450456,
		    1002451614,
		    1002452192,
		    1002452205,
		    1002452212,
		    1002453800,
		    1002455988,
		    1002462595,
		    1002468082,
		    1002470417,
		    1002476963,
		    1002478999,
		    1002482579,
		    1002482580,
		    1002482581,
		    1002482588,
		    1002482589,
		    1002515551,
		    1002584210,
		    1002592907,
		    1002592909,
		    1002592910,
		    1002592911,
		    1002592912,
		    1002592913,
		    1002592914,
		    1002592915,
		    1002592916,
		    1002592917,
		    1002592918,
		    1002592919,
		    1002601441,
		    1002601442,
		    1002608276,
		    1002608312,
		    1002614444,
		    1002614445,
		    1002614446,
		    1002614447,
		    1002614452,
		    1002614453,
		    1002614454,
		    1002614456,
		    1002625926,
		    1002631053,
		    1002654641,
		    1002688342,
		    1002689488,
		    1002721479,
		    1002724256,
		    1002727179,
		    1002729331,
		    1002731964,
		    1002731970,
		    1002747762,
		    1002750073,
		    1002753517,
		    1002789099,
		    1002801476,
		    1002801522,
		    1002809163,
		    1002815694,
		    1002815696,
		    1002815698,
		    1002815705,
		    1002815708,
		    1002815719,
		    1002815727,
		    1002815737,
		    1002815755,
		    1002815763,
		    1002815769,
		    1002815785,
		    1002815793,
		    1002815802,
		    1002815816,
		    1002815828,
		    1002815832,
		    1002815834,
		    1002815835,
		    1002815870,
		    1002815879,
		    1002815921,
		    1002815928,
		    1002818888,
		    1002829893,
		    1002831505,
		    1002844261,
		    1002844471,
		    1002845578,
		    1002845674,
		    1002847314,
		    1002847420,
		    1002847937,
		    1002847958,
		    1002849753,
		    1002852494,
		    1002852501,
		    1002852506,
		    1002852511,
		    1002852529,
		    1002852811,
		    1002860077,
		    1002862975,
		    1002862994,
		    1002863047,
		    1002863121,
		    1002863156,
		    1002868226,
		    1002868339,
		    1002868439,
		    1002868507,
		    1002868629,
		    1002868631,
		    1002868642,
		    1002868662,
		    1002868756,
		    1002868778,
		    1002879712,
		    1002898523,
		    1002902687,
		    1002911520,
		    1002914116,
		    1002920359,
		    1002943877,
		    1002943943,
		    1002947118,
		    1002956565,
		    1002959241,
		    1002959255,
		    1002959407,
		    1002959441,
		    1002959450,
		    1002959610,
		    1002963065,
		    1002963075,
		    1002969448,
		    1002969461,
		    1002969486,
		    1002971793,
		    1002971820,
		    1002971822,
		    1002977730,
		    1002984714,
		    1002985245,
		    1002986231,
		    1002987697,
		    1002993808,
		    1002993812,
		    1002993813,
		    1002993816,
		    1003005543,
		    1003005625,
		    1003016445,
		    1003020787,
		    1003020790,
		    1003022821,
		    1003042431,
		    1003042435,
		    1003042437,
		    1003045383,
		    1003049440,
		    1003053946,
		    1003054267,
		    1003054271,
		    1003062366,
		    1003062468,
		    1003062479,
		    1003066703,
		    1003066704,
		    1003066705,
		    1003080789,
		    1003098408,
		    1003098413,
		    1003100326,
		    1003100398,
		    1003100404,
		    1003100405,
		    1003100408,
		    1003100410,
		    1003100412,
		    1003100417,
		    1003106459,
		    1003106461,
		    1003165864,
		    1003165868,
		    1003165870,
		    1003165920,
		    1003172416,
		    1003185017,
		    1003185018,
		    1003185021,
		    1003185025,
		    1003185032,
		    1003185034,
		    1003185048,
		    1003185050,
		    1003185051,
		    1003185052,
		    1003185055,
		    1003185056,
		    1003185058,
		    1003185059,
		    1003185060,
		    1003185061,
		    1003185062,
		    1003185063,
		    1003185064,
		    1003185108,
		    1003185110,
		    1003185111,
		    1003197782,
		    1003198028,
		    1003198056,
		    1003226862,
		    1003226869,
		    1003227628,
		    1003227889,
		    1003229284,
		    1003229320,
		    1003229335,
		    1003244626,
		    1003474618,
		    NumberLong(2920833648),
		    NumberLong(2920833652),
		    NumberLong(2920833657),
		    NumberLong(2920833663),
		    NumberLong(2920833665),
		    NumberLong(2920833670),
		    NumberLong(2920833674),
		    NumberLong(2921390555)
		]
								


