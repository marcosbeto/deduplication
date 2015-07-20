import json
import os
import cv2
import time
import pymongo
import re
from os import walk
from os import path

from models import Models
from constants import Constants

class Image_Processor(object):	


	def get_histogram(dir_name, file_name, self):
		try:
			#generating the histogram and adding it to the json to be added to mongo
			hist = self.get_histogram(os.path.join(dir_name, file_name)) 
			return hist
		except:
			pass

		return None


	def create_images_histogram_from_onlie_ads(self):	
		models = Models()

		self.number_of_files = 0

		print "Retrieving all online avisos. Please, wait..."
		self.array_avisos_online = models.get_all_avisos_online()
		print "[Ok]"		

		for aviso_online in self.array_avisos_online:

			if len(str(aviso_online))<10:
				aviso_id = format(int(aviso_online), "010")
				aviso_id_splitted = re.findall(r'.{1,2}',aviso_id,re.DOTALL)

				aviso_json = {"id_aviso":aviso_id, "photos":[]}

				complete_folder = ""

				for folder_name in aviso_id_splitted:
					complete_folder +=  folder_name + "/"

				# print os.walk(Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder)

				for root, dirs, files in os.walk(Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder):

					folder_to_download = ""
				    
				    for folder in dirs:

				    	if folder == "100x75":

				    		folder_to_download = "100x75"
							break

						elif folder == "1200x1200":

							folder_to_download = "1200x1200"
							break


				    folder_name = Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder + folder_to_download

		    		for file in os.listdir(folder_name):
					    if file.endswith(".jpg"):
					        hist = self.get_histogram(Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder + "100x75", file)
					        hist_json = {"photo_path":dir_name + "/" + file_name, "histogram":json.dumps(hist.tolist())}
							aviso_json["photos"].append(hist_json)
							print aviso_json

					# if len(os.listdir(folder_name))>0:
					# 	models.add_image_histogram(aviso_json)





				    break


				    # print files

				# for file in os.listdir(Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder):
				#     if file.endswith(".jpg"):
				#         print(file)

				

				# print files


	def create_images_histogram_from_images_backup_iw(self):

		models = Models()

		self.number_of_files = 0

		print "Retrieving all online avisos. Please, wait..."
		self.array_avisos_online = models.get_all_avisos_online()
		print "[Ok]"		

		def step((ext, self), dir_name, files):

			download_100x75 = True

			aviso_id = dir_name[dir_name.rfind("Constants.LOCAL_DIR_SAVE_PHOTO")+len(Constants.LOCAL_DIR_SAVE_PHOTO)+2:dir_name.rfind("/")]
			aviso_id = aviso_id.translate(None, "/")
			
			if "100x75" in dir_name or "1200x1200" in dir_name:
				dir100x75 = dir_name[:dir_name.rfind("/")] + "/100x75"
				dir1200x1200 = dir_name[:dir_name.rfind("/")] + "/1200x1200"

				try: 
					aviso_id_int = int(aviso_id)
				except ValueError:
					aviso_id_int = 0
				
				if aviso_id_int in self.array_avisos_online:
					
					if "1200x1200" in dir_name:
						if os.path.isdir(dir100x75):
							download_100x75 = False

					if download_100x75:

						aviso_json = {"id_aviso":aviso_id, "photos":[]}

						for file_name in files:

							if file_name.lower().endswith(ext):

								try:
									#generating the histogram and adding it to the json to be added to mongo
									hist = self.get_histogram(os.path.join(dir_name, file_name)) 
									hist_json = {"photo_path":dir_name + "/" + file_name, "histogram":json.dumps(hist.tolist())}
									aviso_json["photos"].append(hist_json)
								except:
									pass

						models.add_image_histogram(aviso_json)
				

				if self.number_of_files%100==0:
					print self.number_of_files

				self.number_of_files +=1
			else:
			
				if self.number_of_files%100==0:
					print self.number_of_files
			
				self.number_of_files +=1
			
				print aviso_id
		os.path.walk(Constants.LOCAL_DIR_SAVE_PHOTO, step, ('.jpg', self))


	def create_images_histogram_collection(self):

		models = Models()

		number_of_files = 0

		for dir_name, dir_names, file_names in os.walk(Constants.LOCAL_DIR_SAVE_PHOTO):

			#walking inside all ads
			for subdir_name in dir_names:

				aviso_json = {"id_aviso":subdir_name, "photos":[]}

				for dir_name_, dir_names_, file_names_ in os.walk(os.path.join(dir_name, subdir_name)):

					#walking inside all photos of the specific ad
					for file_name_ in file_names_:

						try:
							#generating the histogram and adding it to the json to be added to mongo
							hist = self.get_histogram(os.path.join(dir_name, subdir_name, file_name_)) 
							hist_json = {"photo_path":subdir_name + "/" + file_name_, "histogram":json.dumps(hist.tolist())}
							aviso_json["photos"].append(hist_json)                                
						except:
							pass

						if number_of_files%1000==0:
							print number_of_files

						number_of_files +=1

					#calling model to add item to mongo
					models.add_image_histogram(aviso_json)

		print "[OK] Created histograms for " + str(number_of_files) + " photos."

	#method responsible to calculate the histogram of a photo
	@staticmethod
	def get_histogram(image_path):
		image = cv2.imread(image_path)
		hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8],
			[0, 256, 0, 256, 0, 256])
		hist = cv2.normalize(hist).flatten()

		return hist

	
	def create_similar_photos_collection(self):
		models = Models()
		models.create_similar_photos_collection()

	def create_equals_avisos_collection(self):
		models = Models()
		models.create_equals_avisos_collection()

	def create_tuples_equals_avisos_collection(self):
		models = Models()
		models.create_tuples_equals_avisos_collection()

	def create_raw_equal_avisos(self):
		models = Models()
		models.create_raw_equal_avisos()

	def create_duplicateds_group_collection(self):
		models = Models()
		models.create_duplicateds_group_collection()