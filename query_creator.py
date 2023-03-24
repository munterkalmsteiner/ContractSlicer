from PIL import Image, ImageDraw, ImageFont, ImageChops
import operator
from optparse import OptionParser
from pdf2image import convert_from_path
import os
import re
from tqdm import tqdm

if __name__ == '__main__':
    usage = "usage: %prog DOCUMENT_FILE PAGE QUERY_HEIGHT OUTPUT_PATH"
    parser = OptionParser(usage=usage)
    (options,args) = parser.parse_args()

    if len(args) != 4:
        parser.error("Incorrect number of arguments")

    document_file = args[0]
    page_number = args[1]
    query_height = int(args[2])
    output_path = args[3]

    images = convert_from_path(document_file) 
    pages = len(images)    
    query_file_prefix = re.sub("[^a-zA-Z0-9\.\/]", "_", document_file).rsplit('/', 1)[1].split(".")[0]
    output_path = os.path.join(output_path, query_file_prefix, page_number)
    

    page_image = images[int(page_number) - 1]
    page_width = page_image.size[0]
    page_height = page_image.size[1]

    for j in tqdm(range(page_height - query_height + 1)):
        im = page_image.crop((0, j, page_width, j + query_height))
        #im = im.convert("L")
        im = im.convert("1")

        os.makedirs(output_path, exist_ok=True)
        im.save(os.path.join(output_path, "%s-%s-%s.png" % (query_file_prefix, page_number, j)))

    
