from downloader import Downloader
from image_processor import Image_Processor
from filters import Filters

class IW_Main(object):

    def run(self):
        
        # Downloader().download_photos()
        # Image_Processor().outside_images()
        
        
        # Image_Processor().create_images_histogram_collection() # <---- USED LOCAL

        # Image_Processor().create_images_histogram_from_images_backup_iw() #<---- USED WITH ALL PHOTOS FROM BACKUP (OFFLINE + ONLINE)
        
    # Step 1: Cropping and creating histograms from all photos in backup
        # Image_Processor().create_images_histogram_from_online_ads() # <---- CURRENT IN USE: USED WITH BACKUP AND CURRENT ONLINE AVISOS

#TODO: REMOVE DUPLICATED ID_AVISS
    
    # Step 2: Compressing histograms string for each photo to make the storage and search less costly
        # Image_Processor().save_compressed_histogram_online()
    
    # Step 3: Finds other ads that have similiar photos
        Image_Processor().create_similar_photos_collection()
    
    # Step 4: Finds the ads that are exactly or __% with similiar photos
        # Image_Processor().create_equals_avisos_collection()

    # Step 5: Creates an array with all equal ads
        # Image_Processor().create_raw_equal_avisos()
    
    # Step 6: 
        # Image_Processor().create_duplicateds_group_collection_new()

    # Step 7: Adding some filters to each of equal aviso data 
        # Filters().create_detailed_repeated_ads_filters()

    # Step 8: Grouping all the equal ads by its filters
        # Filters().group_repeated_ads_filters()


        # Image_Processor().create_duplicateds_group_collection()
        

        # Image_Processor().validate_grouped_equals()

        # Image_Processor().check_differents()

       
        


if __name__ == '__main__':
    IW_Main().run()

