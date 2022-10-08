from PIL import Image
from optparse import OptionParser
import glob
import os

usage = "usage: %prog SOURCE_IMAGE INPUT_FILES OUTPUT_DIR"
parser = OptionParser(usage=usage)
(options,args) = parser.parse_args()

if len(args) != 3:
    parser.error("Incorrect number of arguments")

source = Image.open(args[0])
source_width = source.size[0]
source_height = source.size[1]

target_files = glob.glob(args[1])

for file in target_files:
    target = Image.open(file)
    base_width = source_width
    target_width = target.size[0]
    target_height = target.size[1]

    wpercent = (base_width/float(target_width))
    hsize = int((float(target_height)*float(wpercent)))
    target = target.resize((base_width, hsize), resample=Image.Resampling.LANCZOS)
    
    for i in range(hsize - source_height + 1):
        cropped = target.crop((0, i, source_width, i + source_height))
        fn = file.split('/')[1].split('.')[0]
        cropped.save(os.path.join(args[2], "%s-%s.png" % (fn, i)))  

    
