from PIL import Image
from PIL import ImageChops
from optparse import OptionParser
import numpy as np
import glob
import os
import operator

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
    fn = file.split('/')[2].split('-')[0]
    page = file.split('-')[1]
    slice = file.split('-')[2].split('.')[0]


    if page not in result:
        result[page] = (1000, 0)

    target = Image.open(file)

    try:
        diff = ImageChops.difference(source, target)
        diff = np.mean(np.array(diff))
    
        if diff < result[page][0]:
            result[page] = (diff, slice)
    except:
        print(file)

    print("%s/%s" % (counter, len(targets)))
    counter = counter + 1


print(sorted(result.items(), key=operator.itemgetter(1)))
