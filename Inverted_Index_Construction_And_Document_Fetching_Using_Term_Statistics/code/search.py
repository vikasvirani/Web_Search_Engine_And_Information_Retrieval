from collections import Counter
from collections import OrderedDict
import json
import re
#import nltk
import string
import sys
import os
from collections import defaultdict
import hashlib
import argparse
import struct
#from cStringIO import StringIO
#BLOCKSIZE = 65536
#hasher = hashlib.md5()

def main():
    #filepath = sys.argv[1]

    parser = argparse.ArgumentParser(
        description="Accept Console Arguments for programme",
    )

    parser.add_argument(
        'lexicon',
        help='Generated Lexicons\' file Path',
        nargs='?',
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument(
        'invlists',
        help='Generated Inverted Index\'s file Path',
        nargs='?',
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument(
        'map',
        help='Generated Document Mapping\'s file Path',
        nargs='?',
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument(
        'Query_term',
        metavar='Q',
        nargs='+',
        help='Query terms to be searched'
    )

    args = parser.parse_args()
    lexicon = args.lexicon
    inverted = args.invlists
    map = args.map
    stopwordsDict = Counter()

    #print(sys.argv)
    if not os.path.isfile(lexicon):
        print("File path {} does not exist. Exiting...".format(lexicon))
        sys.exit()

    if not os.path.isfile(inverted):
        print("File path {} does not exist. Exiting...".format(inverted))
        sys.exit()

    if not os.path.isfile(map):
        print("File path {} does not exist. Exiting...".format(map))
        sys.exit()

    if os.path.isfile('stoplist'):
        stopWords = open('stoplist','r')
        #tStopwords = stopWords.read()
        lStopwords = [line.rstrip('\n') for line in stopWords]
        stopwordsDict.update(lStopwords)

    docmap = defaultdict(list)
    lexicons = defaultdict(list)

    with open(lexicon, "r") as lex,open(map, "r") as mapfile:
        #test = lex.read()
        #print(test)
        lines = lex.readlines()
        maplines = mapfile.readlines()

        for linet in lines:
            linet = re.sub(r"\s+",'',linet)
            line = linet.split(':')
            lexicons[line[0]] = [line[1],line[2]]

        for maplinet in maplines:
            maplinet = re.sub(r"\s+",'',maplinet)
            mapline = maplinet.split(':')
            docmap[mapline[0]] = mapline[1]

    #print(lexicons)
    #print(docmap)

    with open(inverted, "rb") as InvertedI:
        for term in sys.argv[4:]:
            term = term.lower()
            print(term)
            doc, offset = lexicons[term]
            InvertedI.seek(int(offset)*4,0)
            #print(InvertedI.tell())
            print(doc)
            for i in range(0,int(doc)*2):
                #value = int.from_bytes(InvertedI.read(3), 'big')
                #int.from_bytes(xbytes, 'big')
                value = struct.unpack('i', InvertedI.read(4))[0]
                one_byte = value
                if i%2==0:
                    print docmap[str(one_byte)],
                else:
                    print(one_byte)


if __name__ == '__main__':
   main()
