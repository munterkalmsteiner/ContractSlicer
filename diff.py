from PIL import Image, ImageDraw, ImageFont
from PIL import ImageChops
from optparse import OptionParser
import numpy as np
import glob
import os
import operator

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

def image_has_more_wite_than(im, percentage):
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
    

usage = "usage: %prog SOURCE_IMAGE INPUT_DIR"
parser = OptionParser(usage=usage)
(options,args) = parser.parse_args()

if len(args) != 2:
    parser.error("Incorrect number of arguments")

source = Image.open(args[0])

targets = glob.glob(os.path.join(args[1], "*"))

result = {}
counter = 1

for file in targets:
    print("%s/%s" % (counter, len(targets)))
    counter = counter + 1
    
    fn = file.split('/')[2].split('-')[0]
    page = file.split('-')[1]
    slice = file.split('-')[2].split('.')[0]

    if page not in result:
        result[page] = (1000, 0)

    target = Image.open(file)

    if image_has_more_wite_than(target, 97):
        continue
    try:
        diff = ImageChops.difference(source, target)
        diff = np.mean(np.array(diff))
        
        if diff < result[page][0]:
            result[page] = (diff, slice, file)
    except:
        print("Could not analyze difference of %s" % file)


    

result = sorted(result.items(), key=operator.itemgetter(1))
print(result)

ranking = None
contract = None
rank = 1

for r in result:
    if len(r[1]) == 3:
        filename = r[1][2]
        difference = r[1][0]
        page = filename.split('-')[1]
        top = Image.open(filename)
        source_top = merge_horizontal(source, top, rank, int(page) + 1, difference)
        ranking = merge_vertical(ranking, source_top)

        if contract is None:
            contract = filename.split('/')[3].split('-')[0]

        rank = rank + 1

ranking.save("%s.png" % contract)

