#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

class Filters(object):	

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


	def create_detailed_repeated_ads_filters(self):
		models = Models()
		models.create_detailed_repeated_ads_filters()