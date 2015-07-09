import requests
import urllib
import os
import compare
import decimal
from decimal import Decimal

import cv2
import time
import numpy
import array

import MySQLdb
from MySQLdb import cursors
import sys
import pymongo
import json
from json import loads
import simplejson
from bson.objectid import ObjectId
from bson import json_util
from bson.json_util import dumps

from multiprocessing import Pool
from multiprocessing import Process
import multiprocessing

from downloader import Downloader
from image_processor import Image_Processor



class DecimalEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, Decimal):
            return "%.2f" % obj
        return json.JSONEncoder.default(self, obj)

class IW_Main(object):


    # def download_photos(self):

    #     print 'get_properties_from_iw_api'

    #     IMOVELWEB_API_QUERY_URL = "http://apim01.imovelweb.com.br/interface/buscador/buscarmin"

    #     headers = {
    #         'username': "adonde",
    #         'password': "v1v1radonde",
    #         'User-Agent': "API_RELA",
    #         'uuid': "4788865e3938759052311306ca032077"
    #     }

    #     page = 1

    #     total_photos_from_neighborhood = 0
    #     total_size_downloaded_from_neighborhood = 0

    #     while (True):

    #         print "\n************ PAGINA: %s" % (str(page))

    #         total_photos_in_page = 0
    #         total_size_downloaded_in_page = 0

    #         url_params = {
    #         'idciudad': 109668, #Sao Paulo
    #         'idzona': 526281, #Morumbi
    #         'pagina': page, }

    #         request_response = requests.get(IMOVELWEB_API_QUERY_URL, params=url_params, headers=headers)
            
    #         json_response = request_response.json()

    #         ads_count = json_response['data']['total']
    #         ads = json_response['data']['avisos']


    #         for ad in ads:
                
    #             number_of_photos_from_ad = 0
    #             total_size_downloaded_from_ad = 0

    #             for attribute, value in ad.iteritems():
    #                 if attribute=='fotos':
    #                     for photo in value:
    #                         photo_url = photo.get('url').replace("580x465", "100x75"); # getting smaller images
                            
    #                         local_dir_saved_photo = "photos_avisos/" + str(ad.get('idpropiedad'))
    #                         local_path_to_save_photo = local_dir_saved_photo + "/" + photo_url.rpartition('/')[2]
                            
    #                         if not os.path.exists(local_dir_saved_photo): 
    #                             os.mkdir(local_dir_saved_photo) #creating aviso directory to save photo
                            
    #                         urllib.urlretrieve(photo_url, local_path_to_save_photo) #Downloading photo

    #                         size = format(bytesto(os.path.getsize(local_path_to_save_photo), 'm'),'.4f') #size in megabytes of each photo

    #                         number_of_photos_from_ad += 1
    #                         total_size_downloaded_from_ad = total_size_downloaded_from_ad + float(size)

    #             print "[#AD] Photos from:  %s: %s | Tamanho:%s\n" % (ad.get('idpropiedad'),str(number_of_photos_from_ad),str(total_size_downloaded_from_ad))
                
    #             total_photos_in_page = total_photos_in_page + number_of_photos_from_ad
    #             total_size_downloaded_in_page = total_size_downloaded_in_page + total_size_downloaded_from_ad
            
    #         print "[#PAGE] Photos from page %s: %s | Tamanho:%s\n" % (page,str(total_photos_in_page),str(total_size_downloaded_in_page))

    #         total_photos_from_neighborhood = total_photos_from_neighborhood + total_photos_in_page
    #         total_size_downloaded_from_neighborhood = total_size_downloaded_from_neighborhood + total_size_downloaded_in_page

    #         if len(ads)<18:
    #             break       

    #         page += 1       
        
    #     print "[#TOTAL] Photos from all pages: %s | Tamanho:%s\n" % (str(total_photos_from_neighborhood),str(total_size_downloaded_from_neighborhood))


    # def set_images_histogram(self):

    #     number_of_subdirectories = 0
    #     number_of_files = 0

    #     data_json = []

    #     for dir_name, dir_names, file_names in os.walk('photos_avisos'):

    #         number_of_subdirectories += 1
            
    #         for subdir_name in dir_names:
    #             aviso_json = {"id": number_of_subdirectories, "id_aviso":subdir_name, "photos":[]}
    #             number_of_subdirectories += 1
    #             for dir_name_, dir_names_, file_names_ in os.walk(os.path.join(dir_name, subdir_name)):

    #                 for file_name_ in file_names_:

    #                     try:
    #                         hist = compare.get_histogram(os.path.join(dir_name, subdir_name, file_name_)) 
    #                         hist_json = {"photo_path":subdir_name + "/" + file_name_, "histogram":json.dumps(hist.tolist())}
    #                         aviso_json["photos"].append(hist_json)                                
    #                     except:
    #                         pass

                        
                        
    #                     number_of_files += 1

                        

    #                     if number_of_files%1000==0:
    #                         print number_of_files

    #                 con_mongo.ads_histograms.insert(aviso_json)
                            

    # def iterate_folders_directory(self):

    #     start = time.time()

    #     number_of_avisos = 0
        
    #     #getting all avisos from mongo db
    #     all_avisos = con_mongo.ads_histograms.find()

    #     for aviso in all_avisos:
            
    #         number_of_avisos += 1
    #         aviso_has_similar_photos = False

    #         #json that will save the entire aviso data that has duplicated photos
    #         aviso_json = {"id_aviso": aviso.get("id_aviso"), "photos":[]}

    #         photos = aviso.get("photos")            

    #         for photo in photos:

    #             is_photo_similar = False                

    #             #finding photos with the same histogram
    #             equals_avisos = con_mongo.ads_histograms.find({"photos.histogram":photo.get("histogram")})
                
    #             #json that saves the data of the main photo that is being compared
    #             main_photo_json = {"main_photo": photo.get("photo_path"), "similar_photos":[]}
                
    #             #iterate in all avisos that have some photo with the same histogram
    #             for aviso_to_compare in equals_avisos:

    #                 #getting all photos of the aviso that is being compared
    #                 photos_compare = aviso_to_compare.get("photos")

    #                 #iterating in all photos to verify which one has the same histogram
    #                 for photo_compare in photos_compare:
                        
    #                     #verifying if the photo has the same histogram, excluding photos of the same aviso
    #                     if aviso_to_compare.get("id_aviso")!=aviso.get("id_aviso") and photo.get("photo_path")!=photo_compare.get("photo_path") and photo.get("histogram")==photo_compare.get("histogram"):
    #                         #json that saves the data of the similar photo that will be saved in similar_photos[] of main_photo_json
    #                         similar_photo_json = {"similar_id_aviso":aviso_to_compare.get("id_aviso"), "similar_photo":photo_compare.get("photo_path")}
    #                         main_photo_json["similar_photos"].append(similar_photo_json)
    #                         aviso_has_similar_photos = True
    #                         is_photo_similar = True
                
    #             #saves main_photo_json if exists a photo inside the aviso that is equal to the main photo
    #             if is_photo_similar:
    #                 aviso_json["photos"].append(main_photo_json);
            
            
    #         now = time.time()
    #         if number_of_avisos%10==0:
    #             print str(number_of_avisos) + " - " + str(now-start)

    #         #saves in mongo the aviso json if there is any photo that has others equal photos 
    #         if aviso_has_similar_photos:
    #             con_mongo.ads_similar.insert(aviso_json)

    # ATTENTION THIS METHOD WAS COMPLETE REMOVED AND ADDED INSIDE find_similar_photos_in_other_ads
    # def update_number_of_ads_similar_collection(self):

    #     all_similar_avisos = con_mongo.ads_similar.find()
    #     number_of_similar_ads_updated = 0
    #     number_of_ads = 0

    #     for similar_aviso in all_similar_avisos:
    #         id_similar_aviso = similar_aviso.get("id_aviso")
    #         aviso_in_histograms_array = con_mongo.ads_histograms.find({"id_aviso":id_similar_aviso})
    #         aviso_in_histograms_array = loads(dumps(aviso_in_histograms_array))

    #         for aviso_hist in aviso_in_histograms_array:
    #             #getting all photos of the aviso that is being compared
    #             number_of_ads = len(aviso_hist.get("photos"))
    #             con_mongo.ads_similar.update({"id_aviso" :id_similar_aviso},{'$set' : {"number_of_ads":number_of_ads}})
    #             break

    #         number_of_similar_ads_updated += 1
    #         print number_of_similar_ads_updated

    # def create_similiar_avisos_collection(self):

    #     start = time.time()

    #     all_similar_avisos = con_mongo.ads_similar.find()

    #     images_not_valid = ["image-soon-po.png","sin-logo.png"]
    #     number_of_similar_aviso_analyzed = 0

    #     #iterating for avisos that have some image duplicated
    #     for similar_aviso in all_similar_avisos:
            
    #         photos = similar_aviso.get("photos")
    #         unique_similar_avisos = []

    #         aviso_json = {"id_aviso":similar_aviso.get("id_aviso"),"equal_avisos":[]}

    #         for photo in photos:

    #             #getting all similar photos
    #             similar_photos = photo.get("similar_photos")

    #             for similar_photo in similar_photos:

    #                 invalid_images = False;

    #                 #verifying if image is not one of the invalid images strings
    #                 for image_to_delete in images_not_valid:
    #                     if image_to_delete in similar_photo.get("similar_photo"):
    #                         invalid_images = True
    #                         break
                    
    #                 #getting the id of the aviso that has a image equal to the one being analized
    #                 similar_id_aviso = similar_photo.get("similar_id_aviso")

    #                 if not invalid_images:

    #                     similar_aviso_already_on_array = False
                        
    #                     #iterating all unique similar_avisos
    #                     for index, unique_similar_aviso in enumerate(unique_similar_avisos, start=0):
                            
    #                         #if similar_id_aviso already exists in json
    #                         if unique_similar_aviso.get("id_aviso")==similar_id_aviso:
    #                             similar_aviso_already_on_array = True
    #                             unique_similar_avisos[index]['num_photos_equal'] += 1
                                
    #                             number_total_photos = unique_similar_avisos[index]["num_photos_total"]
    #                             percentage_of_similar = self.percentage(unique_similar_avisos[index]['num_photos_equal'],number_total_photos)
                                
    #                             unique_similar_avisos[index]['percentage_similar_self_parent'] = int(percentage_of_similar)
                                
    #                     #did not find any similar id_aviso or the array is empty
    #                     if not similar_aviso_already_on_array:                            

    #                         similar_aviso_support = con_mongo.ads_similar.find({"id_aviso":similar_id_aviso})
    #                         similar_aviso_support = loads(dumps(similar_aviso_support))

    #                         number_of_ads_similar = similar_aviso_support[0].get("number_of_ads")
    #                         percentage_of_similar = self.percentage(1,number_of_ads_similar)

    #                         similar_aviso_json = {"id_aviso":similar_id_aviso,
    #                         "num_photos_equal":1,
    #                         "num_photos_total": number_of_ads_similar,
    #                         "percentage_similar_self_parent": int(percentage_of_similar)
    #                         }
                                
    #                         unique_similar_avisos.append(similar_aviso_json)
                       

    #         only_equal_avisos = []
            
    #         for unique_similar_aviso in unique_similar_avisos:
    #             if unique_similar_aviso['percentage_similar_self_parent']>85:
    #                 aviso_json["equal_avisos"].append(unique_similar_aviso)
                    
    #         if len(aviso_json["equal_avisos"]) > 0:
    #             con_mongo.ads_equals.insert(aviso_json)

    #         number_of_similar_aviso_analyzed += 1

    #         if number_of_similar_aviso_analyzed%100==0:
    #             now = time.time()
    #             print str(number_of_similar_aviso_analyzed) + " - " + str(now-start)

    # def create_tuples(self):
    #     start = time.time()

    #     all_duplicated_avisos = con_mongo.ads_equals.find()
    #     number_avisos = 0

    #     only_equals = []

    #     #getting all avisos that are duplicated
    #     for aviso in all_duplicated_avisos:
    #         aviso_id = aviso.get("id_aviso")

    #         equal_avisos_ids = aviso.get("raw_equal_avisos")

    #         #getting all equal_avisos that are equal to aviso
    #         for equal_aviso_id in equal_avisos_ids:

                
    #             if equal_aviso_id!=aviso_id:
                    
    #                 # print equal_aviso_id

    #                 #looking for the equal_aviso in all ads_equals collection
    #                 equal_aviso_object = con_mongo.ads_equals.find({"id_aviso":equal_aviso_id})
    #                 equal_aviso_object = loads(dumps(equal_aviso_object))

    #                 if len(equal_aviso_object)>0:                        
                        
    #                     #getting all avisos that is similar to equal_aviso
    #                     equal_aviso_object_equals_ids = equal_aviso_object[0]['raw_equal_avisos']

    #                     for equal_aviso_object_equal_id in equal_aviso_object_equals_ids:
                            
    #                         #checking if aviso_id is also in raw_equals of the equal_aviso
    #                         #this guarantee that the both sides of comparasion exists, so de aviso is equal
    #                         if equal_aviso_object_equal_id == aviso_id:
                                
    #                             tuple_to_add = [aviso_id, equal_aviso_id]

    #                             has_equal = False
                                
    #                             #iterating in array to see if the tuple was already added
    #                             for only_equals_tuples in only_equals:
    #                                 #if the tupled is already on array
    #                                 if set(tuple_to_add) == set(only_equals_tuples):
    #                                     has_equal=True
    #                                     break

    #                             if not has_equal:
    #                                 con_mongo.ads_all_tuples.insert({'avisos_tuple': tuple_to_add})
    #                                 only_equals.append(tuple_to_add)

    #         number_avisos += 1
    #         print number_avisos

    def delete_double_touples(self):

        start = time.time()

        all_tuples = con_mongo.ads_all_tuples.find()
        number_avisos = 0
        all_already_compared = []

        #getting all avisos that are duplicated
        for single_tuple in all_tuples:
            
            tuples = single_tuple.get("avisos_tuple")
            only_equals = {"id_aviso":tuples[0],"all_equals":[]}

            all_tuples_compare = con_mongo.ads_all_tuples.find({"avisos_tuple":tuples[0]})

            if not tuples[0] in all_already_compared:
            
                for tuple_compare in all_tuples_compare:

                    tuples_compare = tuple_compare.get("avisos_tuple")

                    if tuples[0] == tuples_compare[0]:
                        only_equals["all_equals"].append(tuples_compare[1])
                    else:
                        only_equals["all_equals"].append(tuples_compare[0])

                number_avisos+=1

                all_already_compared.append(tuples[0])

                con_mongo.ads_all_similar.insert(only_equals)
            
            print only_equals

        print number_avisos

    def clean_group_final_repeated(self):

        all_avisos = con_mongo.ads_all_similar.find()
        number_avisos = 0
        number_avisos_removed = 0

        for aviso in all_avisos:
            id_aviso = aviso.get("id_aviso")
            
            
            if con_mongo.ads_all_similar.find({"id_aviso":id_aviso}).count()>0:

                equal_avisos = aviso.get("all_equals")

                for equal_aviso in equal_avisos:
                    
                    if con_mongo.ads_all_similar.find({"id_aviso":equal_aviso}).count()>0:
                        con_mongo.ads_all_similar.remove({ 'id_aviso': equal_aviso}, True)
                        number_avisos_removed += 1


            number_avisos += 1
            print "Removed: " + str(number_avisos_removed)
            print number_avisos


    def clean_group_final_repeated_group(self):

        all_avisos = con_mongo.ads_all_similar.find()
        number_avisos = 0
        number_avisos_removed = 0

        for aviso in all_avisos:
            id_aviso = aviso.get("id_aviso")
            all_equals_aviso = aviso.get("all_equals")

            for equal_aviso in all_equals_aviso:

                number_similar_ads = con_mongo.ads_all_similar.find({"all_equals":equal_aviso, "id_aviso": { "$ne": id_aviso}}).count()

                if number_similar_ads>0:

                    equals = con_mongo.ads_all_similar.find({"all_equals":equal_aviso, "id_aviso": { '$ne': id_aviso}})

                    for equal in equals:
                        id_aviso_equal = equal.get("id_aviso")

                        if not id_aviso_equal in all_equals_aviso:
                            con_mongo.ads_all_similar.update({"id_aviso":id_aviso},{ '$push': {'all_equals': id_aviso_equal}})

                        con_mongo.ads_all_similar.remove({'id_aviso':id_aviso_equal}, True)
                        number_avisos_removed += 1

            number_avisos +=1
            print number_avisos
            print number_avisos_removed

    def add_array_all_equals(self):
        all_avisos = con_mongo.ads_all_similar.find()
        number_avisos = 0
        number_avisos_removed = 0

        for aviso in all_avisos:
            id_aviso = aviso.get("id_aviso")
            con_mongo.ads_all_similar.update({"id_aviso":id_aviso},{ '$push': {'all_equals': id_aviso}})





    def verify_similarity_both_sides(self):

        start = time.time()

        all_duplicated_avisos = con_mongo.ads_equals_tuples.find()


        print "NUMBER: " + str(con_mongo.ads_equals_tuples.find().count())

        number_avisos = 0
        number_avisos_equal = 0

        only_equals = []

        for aviso in all_duplicated_avisos:
            aviso_a = aviso.get("id_aviso_a")
            aviso_b = aviso.get("id_aviso_b")

            has_equal = False

            all_duplicated_avisos_support = con_mongo.ads_equals_tuples.find()


            for aviso_support in all_duplicated_avisos_support:
                aviso_a_support = aviso_support.get("id_aviso_a")
                aviso_b_support = aviso_support.get("id_aviso_b")

                if(aviso_a==aviso_b_support):
                    
                    has_equal = True

                    tuple_to_add = [aviso_a, aviso_b]
                    # con_mongo.ads_only_equals.insert({'avisos_tuple': tuple_to_add})

                    
                    #only_equals loads(dumps(only_equals))

                    
                    if number_avisos>0:
                        for only_equals_tuples in only_equals:
                            # print only_equals_tuples.get("avisos_tuple")
                            # print str(only_equals_tuples) + " _ " + str(tuple_to_add)
                            if set(tuple_to_add) != set(only_equals_tuples):
                                has_equal=True
                                number_avisos_equal+=1
                                con_mongo.ads_only_equals.insert({'avisos_tuple': tuple_to_add})
                                break
                    else:
                        has_equal=True 
                        con_mongo.ads_only_equals.insert({'avisos_tuple': tuple_to_add})
                        only_equals.append(tuple_to_add)

                    if has_equal:
                        break



                    # con_mongo.ads_equals_tuples.remove({ 'id_aviso_a': aviso_a_support ,'id_aviso_b':aviso_b_support}, True)


                  

            # if not has_equal:
                # con_mongo.ads_equals_tuples.remove({ 'id_aviso_a': aviso_a ,'id_aviso_b':aviso_b}, True)

            number_avisos+=1

            print "Equal: " + str(number_avisos_equal)
            print "Total:" + str(number_avisos)          
       


    # def create_raw_equal_avisos(self):
    #     start = time.time()

    #     all_duplicated_avisos = con_mongo.ads_equals.find()

    #     for duplicated_aviso in all_duplicated_avisos:
                
    #         raw_equal_avisos = []

    #         raw_equal_avisos.append(duplicated_aviso.get("id_aviso"))
    #         # set(x) == set(y)

    #         equal_avisos = duplicated_aviso.get("equal_avisos")

    #         for equal_aviso in equal_avisos:

    #             raw_equal_avisos.append(equal_aviso.get("id_aviso"))

    #         con_mongo.ads_equals.update({"id_aviso" :duplicated_aviso.get("id_aviso")},{'$set' : {"raw_equal_avisos":raw_equal_avisos}})


    # def group_duplicateds(self):

    #     all_duplicated_avisos = con_mongo.ads_equals.find()
        

    #     all_equals_json = []

    #     all_avisos = 0

    #     for duplicated_aviso in all_duplicated_avisos:

    #         aviso_already_analized = False
    #         some_equal = False

    #         number_of_grouped = 0;

    #         #json that saves the raw_equal_avisos and the avisos[] that have this respective raw
    #         grouped_equal_avisos = {"avisos":[],"raw_equal_avisos":duplicated_aviso.get("raw_equal_avisos")}

    #         #adding the aviso that is being analized aviso to avisos[] array
    #         # grouped_equal_avisos["avisos"].append(duplicated_aviso.get("id_aviso"))
            
    #         for compared_aviso in all_equals_json:

    #             group_avisos_duplicated = compared_aviso.get("avisos")
                
    #             for aviso_duplicated in group_avisos_duplicated:
                    
    #                 if duplicated_aviso.get("id_aviso") == aviso_duplicated:
    #                     aviso_already_analized = True
    #                     # print "aviso_already_analized = TRUE"


    #         if not aviso_already_analized:

    #             all_duplicated_avisos_compare = con_mongo.ads_equals.find()

    #             #iterating in other avisos to see if there is a raw avisos equal to group them
    #             for duplicated_aviso_compare in all_duplicated_avisos_compare:

    #                 #checking if they have the same raw
    #                 if set(duplicated_aviso_compare.get("raw_equal_avisos")) == set(duplicated_aviso.get("raw_equal_avisos")):
    #                     some_equal = True
    #                     ## if they are different ads add to avisos[] array of avisos with the same raw
    #                     #if duplicated_aviso.get("id_aviso") != duplicated_aviso_compare.get("id_aviso"):
    #                     grouped_equal_avisos["avisos"].append(duplicated_aviso_compare.get("id_aviso"))

    #         all_avisos += 1
            
    #         if some_equal:
    #             all_equals_json.append(grouped_equal_avisos)
    #             print all_equals_json
    #             # number_of_grouped += 1
    #             print all_avisos
    #             con_mongo.ads_equals_grouped.insert(grouped_equal_avisos)
               

    #only to clean array
    def elimate_repeated_all_similar(self):

        all_avisos = con_mongo.ads_all_similar.find()
        number_avisos = 0
        number_avisos_removed = 0

        for index, aviso in enumerate(all_avisos, start=0):
        # for aviso in all_avisos:
            id_aviso = aviso.get("id_aviso")
            all_equals = aviso.get("all_equals")
            if all_equals!=None:
                con_mongo.ads_all_similar.update({"id_aviso" :id_aviso},{'$set' : {"all_equals":sorted(set(all_equals))}})
            else:
                con_mongo.ads_all_similar.remove({ 'id_aviso': id_aviso}, True)
            # print )

            # if con_mongo.ads_all_similar.find({"id_aviso":id_aviso}).count()>0:

            #     equal_avisos = aviso.get("all_equals")

            #     for equal_aviso in equal_avisos:
                    
            #         if con_mongo.ads_all_similar.find({"id_aviso":equal_aviso}).count()>0:
            #             con_mongo.ads_all_similar.remove({ 'id_aviso': equal_aviso}, True)
            #             number_avisos_removed += 1


            # number_avisos += 1
            # print "Removed: " + str(number_avisos_removed)
            # print number_avisos


    ########### BEGIN:UTILS

    def percentage(self, percent, whole):
        return (percent * 100.0) / whole

    def bytesto(bytes, to, bsize=1024):
        """convert bytes to megabytes, etc.
           sample code:
               print('mb= ' + str(bytesto(314575262000000, 'm')))

           sample output: 
               mb= 300002347.946
        """
     
        a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
        r = float(bytes)
        for i in range(a[to]):
            r = r / bsize
     
        return(r)

    def __print_inline(self, string):
        sys.stdout.write(string)
        sys.stdout.flush()

    ########### END:UTILS

    ############DB##############
    def __db_mysql(self):
        self.__print_inline("\n[db] conectando com o MySQL... \n")
        conn = MySQLdb.connect(host="192.168.22.78", db='navplat_realestate_imovelweb', user="imovelro", passwd="1m0v3lr0", charset='utf8', use_unicode=True) # US-RDS
        print "oK!"
        return conn

    def open_cursor(self):
        global con_mysql
        return con_mysql.cursor(cursors.SSDictCursor)

    def __db_mongo(self):
        self.__print_inline("\n[db] conectando com o MongoDB... \n")
        # connection = pymongo.Connection('ds063038-a1.mongolab.com', 63038)
        # db = connection['urbanizo']
        # db.authenticate('mestre', 'xirinxirion')

        connection = pymongo.Connection('localhost')
        db = connection['deduplication']

        print "oK mongo!"
        return db

    def setup_db(self):
        # global query_limits
        # query_limits = 0
        # global con_mysql
        # con_mysql = self.__db_mysql()
        global con_mongo
        con_mongo = self.__db_mongo()
        print("Done!")
    ############FIM DB##############

    def get_polygons(self):
       
        return con_mongo.place.find({'hierarchy': ObjectId("52d044555847c13b8587f338"), 'hierarchy_size':6})



    def info(self, title):
        print title
        print 'module name:', __name__
        if hasattr(os, 'getppid'):  # only available on Unix
            print 'parent process:', os.getppid()
        print 'process id:', os.getpid()

    def f(self, name):
        self.info('function f')
        print 'hello', name

    def start_processes(self):

        self.info('main line')
        p = Process(target=self.f, args=(['bob','clark'],))
        p.start()
        p.join()

    def f(self, x):
        return x*x

    def worker(num):
        """thread worker function"""
        print 'Worker:', num
        return

    def run(self):
        
        # self.setup_db()

        # self.iterate_folders_directory()
        # self.update_number_of_ads_similar_collection()
        # self.create_similiar_avisos_collection()
        # self.group_duplicateds()
        # self.create_tuples()
        # self.verify_similarity_both_sides()
        # self.delete_double_touples()
        # self.clean_group_final_repeated()
        # self.clean_group_final_repeated_group()
        # self.add_array_all_equals()
        # self.elimate_repeated_all_similar();
        
        # Downloader().download_photos();

        # self.con_mongo = self.__db_mongo()
        # Image_Processor().create_images_histogram_collection();
        # Image_Processor().create_similar_photos_collection()
        # Image_Processor().create_equals_avisos_collection()
        # Image_Processor().create_raw_equal_avisos()
        Image_Processor().create_duplicateds_group_collection()


if __name__ == '__main__':
    IW_Main().run()

