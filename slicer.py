from PIL import Image, ImageDraw, ImageFont, ImageChops
import numpy as np
import operator
from optparse import OptionParser
from pdf2image import convert_from_path
import glob
import os
import re
import shutil
import csv
import sys
import multiprocessing as mp
from p_tqdm import p_map

def image_has_more_white_than(im, percentage):
    colors = im.getcolors()

    if len(colors) < 2:
        return True
    
    black = colors[0][0]
    white = colors[1][0]
    total = black + white
    
    whitepercentage = white * 100 / total

    if whitepercentage > percentage:
        return True
    else:
        return False

def slice(task):
    query_file = task[0]
    query_image = Image.open(query_file)
    
    query_width = query_image.size[0]
    query_height = query_image.size[1]
    query_image = query_image.resize((query_width, query_height), resample=Image.NEAREST)
    #query_image = query_image.convert("L")
    query_image = query_image.convert("1")
    
    document = task[1]
    images = convert_from_path(document) 
    pages = len(images)    
    target_document = re.sub("[^a-zA-Z0-9\.\/]", "_", document).rsplit('/', 1)[1].split(".")[0]
    top_per_page = {}
    
    for page in range(pages):
        target_image = images[page]
        base_width = query_width
        target_width = target_image.size[0]
        target_height = target_image.size[1]

        wpercent = (base_width/float(target_width))
        hsize = int((float(target_height)*float(wpercent)))
        target_image = target_image.resize((base_width, hsize), resample=Image.NEAREST)  

        for j in range(hsize - query_height + 1):
            im = target_image.crop((0, j, query_width, j + query_height))
            #im = im.convert("L")
            im = im.convert("1")

            if image_has_more_white_than(im, 97):
                continue

            try:
                diff = ImageChops.difference(query_image, im)
                diff = np.mean(np.array(diff))
                
                if page not in top_per_page:
                    top_per_page[page] = (diff, im)
                else:
                    if diff < top_per_page[page][0]:
                        top_per_page[page] = (diff, im)
            except Exception as e:
                print("Could not analyze difference of %s: %s" % (target_document, e))

    # store top_per_page results in list and sort by diff in ascending order
    result = sorted(list(zip(top_per_page.keys(), top_per_page.values())), key=lambda r: r[1][0])
    return (query_file, query_image, target_document, result)

def merge_horizontal(im1, im2, rank, page, difference):
    topmargin = 100
    bottommargin = 50
    w = im1.width + im2.width
    h = max(im1.height, im2.height) + topmargin + bottommargin
    im = Image.new("L", (w,h), color=255)

    im.paste(im1, (0, topmargin))
    im.paste(im2, (im1.width, topmargin))

    info = ImageDraw.Draw(im)

    font = ImageFont.truetype("DejaVuSans.ttf", 30)
    info.text((im2.width, 30), "Page: %s / Rank: %s / Difference: %s" % \
              (page, rank, difference), font=font) 
    
    linewidth = 3
    liney = im.height - linewidth
    info.line([(0,liney),(im.width,liney)], fill=0, width=linewidth)
    
    return im

def merge_vertical(im1, im2):
    if im1 is None:
        im = Image.new("L", (im2.width, im2.height))
        im.paste(im2)
    else:
        w = max(im1.width, im2.width)
        h = im1.height + im2.height
        im = Image.new("L", (w,h))

        im.paste(im1)
        im.paste(im2, (0, im1.height))
        
    return im

if __name__ == '__main__':
    usage = "usage: %prog QUERIES_PATH DOCUMENTS_PATH OUTPUT_PATH"
    parser = OptionParser(usage=usage)
    (options,args) = parser.parse_args()

    if len(args) != 3:
        parser.error("Incorrect number of arguments")

    queries = glob.glob("%s/*.png" % args[0])
    documents = glob.glob("%s/*.pdf" % args[1])
    outputpath = args[2]

    tasks = list()

    for q in queries:
        for d in documents:
            tasks.append((q, d))

    results = p_map(slice, tasks)

    #shutil.rmtree(outputpath)

    with open(os.path.join(outputpath, "result.csv"), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["Query", "Document", "Page", "Difference"])

        for result in results:
            query_file = result[0]
            query_image = result[1]
            target_document = result[2]
            diffs = result[3]

            if len(diffs) == 0:
                print("Query %s in %s had no diffs" % (query_file, target_document))
                continue

            query_dir = query_file.rsplit('/', 1)[1].split(".")[0]
            outputpath_query = os.path.join(outputpath, query_dir)
            os.makedirs(outputpath_query, exist_ok=True)

            ranking_image = None
            rank = 1
            
            # top 5
            for d in range(min(len(diffs), 5)):
                page = diffs[d][0] + 1
                difference = diffs[d][1][0]
                target_image = diffs[d][1][1]
                writer.writerow([query_file, target_document, page, difference])

                row_image = merge_horizontal(query_image, target_image, rank, page, difference)
                ranking_image = merge_vertical(ranking_image, row_image)

                rank = rank + 1

            ranking_image.save("%s.png" % os.path.join(outputpath_query, target_document))
    
