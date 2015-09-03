import json
import os
import cv2
import time
import pymongo
import re
from os import walk
from os import path
import utils

from models import Models
from constants import Constants

class Image_Processor(object):	

	def outside_images(self):

		models = Models()

		number_of_files = 0

		print "Retrieving all online avisos. Please, wait..."
		array_avisos_online = models.get_all_avisos_online()
		print '[Ok]'
		print "Retrieving all histogramed avisos. Please, wait..."
		array_avisos_with_hist = models.get_all_avisos_with_histogram()
		print '[Ok]'

		for aviso_online_id in array_avisos_online:

			is_on_hist_table = False

			for aviso_online_with_hist_id in array_avisos_with_hist:

				if aviso_online_id == aviso_online_with_hist_id:
					is_on_hist_table = True
					break

			if not is_on_hist_table:
				aviso_json = {"id_aviso":aviso_online_id}
				models.save_id_aviso_not_histogram_table(aviso_json)

			if number_of_files%100==0:
				print number_of_files

			number_of_files +=1


	def create_images_histogram_from_online_ads(self):	
		models = Models()

		number_of_files = 0

		print "Retrieving all online avisos. Please, wait..."
		self.array_avisos_online = models.get_all_avisos_online()
		print "[Ok]"		

		for aviso_id in self.array_avisos_online:

			if number_of_files%100==0:
				print number_of_files

			number_of_files +=1

			aviso_json = {"id_aviso":aviso_id, "photos":[], "date":time.strftime("%d/%m/%Y")}

			# print os.walk(Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder)
			# try:

			if len(str(aviso_id))<10:
				aviso_id = format(int(aviso_id), "010")

			aviso_id_splitted = re.findall(r'.{1,2}',str(aviso_id),re.DOTALL)

			complete_folder = ""

			for folder_name in aviso_id_splitted:
				complete_folder +=  folder_name + "/"

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

						print folder_name

						hist = self.get_histogram(self, os.path.join(folder_name, file))
						hist_json = {"photo_path":folder_name + "/" + file, "histogram":json.dumps(hist.tolist())}
						aviso_json["photos"].append(hist_json)

				if len(os.listdir(folder_name))>0:
					models.add_image_histogram(aviso_json)

				break

			# except:
			# 	pass


					# print files

				# for file in os.listdir(Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder):
				#     if file.endswith(".jpg"):
				#         print(file)

				

				# print files

	def create_images_histogram_from_online_ads_sql(self):	
		

		models = Models()


		sql = "SELECT idaviso FROM avisosonline"

		# try:
		all_avisos_sql = models.get_all_avisosonline_sql()

		number_avisos_sql_avisos_online = 0

		for aviso in all_avisos_sql:

			number_avisos_sql_avisos_online += 1

			if number_avisos_sql_avisos_online%10==0:
				print str(number_avisos_sql_avisos_online)

			number_of_photos_from_ad = 0
			total_size_downloaded_from_ad = 0

			aviso_id = aviso["idaviso"]


			aviso_json = {"id_aviso":aviso_id, "photos":[], "date":time.strftime("%d/%m/%Y")}

			# print os.walk(Constants.LOCAL_DIR_SAVE_PHOTO + complete_folder)
			# try:

			if len(str(aviso_id))<10:
				aviso_id = format(int(aviso_id), "010")

			aviso_id_splitted = re.findall(r'.{1,2}',str(aviso_id),re.DOTALL)

			complete_folder = ""

			for folder_name in aviso_id_splitted:
				complete_folder +=  folder_name + "/"

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

						print folder_name + "/" + file

						hist = self.get_histogram(self, os.path.join(folder_name, file))
						hist_json = {"photo_path":folder_name + "/" + file, "histogram":json.dumps(hist.tolist())}
						aviso_json["photos"].append(hist_json)

				if len(os.listdir(folder_name))>0:
					models.add_image_histogram(aviso_json)

				break

			# except:
			# 	pass


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
							# #generating the histogram and adding it to the json to be added to mongo
							hist = self.get_histogram(self, os.path.join(dir_name, subdir_name, file_name_)) 
							
							if hist!=None:
								hist_json = {"photo_path":subdir_name + "/" + file_name_, "histogram":json.dumps(hist.tolist())}
								aviso_json["photos"].append(hist_json)                                
						
						except:
							pass

						if number_of_files%100==0:
							print number_of_files

						number_of_files +=1

					#calling model to add item to mongo
					models.add_image_histogram(aviso_json)

		print "[OK] Created histograms for " + str(number_of_files) + " photos."

	#method responsible to calculate the histogram of a photo
	@staticmethod
	def get_histogram(self, image_path):
		image = cv2.imread(image_path)
		if image!=None:
			image = self.crop_image(image)
			hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8],
				[0, 256, 0, 256, 0, 256])
			hist = cv2.normalize(hist).flatten()
			return hist
		return None

	@staticmethod
	def crop_image(original_image):

		height, width, channels = original_image.shape

		pixels_offset_y = int(utils.from_percentage(21,height))
		pixels_offset_x = int(utils.from_percentage(28,width))

		# print 'height: ' + str(height) + ', offset_h: ' + str(pixels_offset_y) + ', width: ' + str(width) + ', offset_w: ' + str(pixels_offset_x)

		cropped_image = original_image[pixels_offset_y:int(height)-pixels_offset_y, pixels_offset_x:int(width)-pixels_offset_x] # Crop from x, y, w, h -> 100, 200, 300, 400
		return cropped_image

	
	def get_new_online_avisos(self):
		models = Models()
		models.get_new_online_avisos()

	def save_compressed_histogram_online(self):
		models = Models()
		models.save_compressed_histogram_online()

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

	def validate_grouped_equals(self):
		models = Models()
		models.validate_grouped_equals()

	def validate_arr(self):
		models = Models()
		models.validate_arr()

	def check_differents(self):
		models = Models()
		models.check_differents()

	def create_duplicateds_group_collection_new(self):
		models = Models()
		models.create_duplicateds_group_collection_new()