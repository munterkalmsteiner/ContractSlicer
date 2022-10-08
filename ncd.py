from optparse import OptionParser
import lzma
import glob
import os
import operator

usage = "usage: %prog SOURCE_IMAGE INPUT_DIR"
parser = OptionParser(usage=usage)
(options,args) = parser.parse_args()

if len(args) != 2:
    parser.error("Incorrect number of arguments")


source = open(args[0], 'rb').read()

targets = glob.glob(os.path.join(args[1], "*"))

sizes = [os.path.getsize(f) for f in targets]


lzma_filters = my_filters = [
    {
      "id": lzma.FILTER_LZMA2, 
      "preset": 9 | lzma.PRESET_EXTREME, 
      "dict_size": max(sizes) * 10, # a big enough dictionary, but not more than needed, saves memory
      "lc": 3,
      "lp": 0,
      "pb": 0, # assume ascii
      "mode": lzma.MODE_NORMAL,
      "nice_len": 273,
      "mf": lzma.MF_BT4
    }
]

result = {}
counter = 1

for file in targets:
    fn = file.split('/')[2].split('-')[0]
    page = file.split('-')[1]
    slice = file.split('-')[2].split('.')[0]


    if page not in result:
        result[page] = (1, 0)
    
    target = open(file, 'rb').read()
    source_target = source + target

    source_comp = lzma.compress(source, format=lzma.FORMAT_RAW, filters= lzma_filters)
    target_comp = lzma.compress(target, format=lzma.FORMAT_RAW, filters= lzma_filters)
    source_target_comp = lzma.compress(source_target, format=lzma.FORMAT_RAW, filters= lzma_filters)

    #print(len(source_comp), len(target_comp), len(source_target_comp), sep=' ', end='\n')

    ncd = (len(source_target_comp) - min(len(source_comp), len(target_comp))) / \
        max(len(source_comp), len(target_comp))

    if ncd < result[page][0]:
        result[page] = (ncd, slice)

    print("%s/%s" % (counter, len(targets)))
    counter = counter + 1


print(sorted(result.items(), key=operator.itemgetter(1)))
