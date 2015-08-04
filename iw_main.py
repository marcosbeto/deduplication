from downloader import Downloader
from image_processor import Image_Processor

class IW_Main(object):

    def run(self):
        
        # Downloader().download_photos()
        # Image_Processor().outside_images()
        
        
        # Image_Processor().create_images_histogram_collection() # <---- USED LOCAL

        # Image_Processor().create_images_histogram_from_images_backup_iw() #<---- USED WITH ALL PHOTOS FROM BACKUP (OFFLINE + ONLINE)
        
    # Step 1: Cropping and creating histograms from all photos in backup
        # Image_Processor().create_images_histogram_from_online_ads() # <---- CURRENT IN USE: USED WITH BACKUP AND CURRENT ONLINE AVISOS
    
    # Step 2: Compressing histograms string for each photo to make the storage and search less costly
        Image_Processor().save_compressed_histogram_online()
        
        # Image_Processor().create_similar_photos_collection()
        
        # Image_Processor().create_equals_avisos_collection()
        # Image_Processor().create_raw_equal_avisos()
        # Image_Processor().create_duplicateds_group_collection()
        # Image_Processor().validate_grouped_equals()
        # Image_Processor().create_duplicateds_group_collection_new()


if __name__ == '__main__':
    IW_Main().run()

