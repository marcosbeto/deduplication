from downloader import Downloader
from image_processor import Image_Processor

class IW_Main(object):

    def run(self):
        
        Downloader().download_photos();
        # Image_Processor().create_images_histogram_collection();
        # Image_Processor().create_similar_photos_collection()
        # Image_Processor().create_equals_avisos_collection()
        # Image_Processor().create_raw_equal_avisos()
        # Image_Processor().create_duplicateds_group_collection()


if __name__ == '__main__':
    IW_Main().run()

