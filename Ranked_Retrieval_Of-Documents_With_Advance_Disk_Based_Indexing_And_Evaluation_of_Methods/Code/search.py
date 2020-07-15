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
import time
import collections
import heapq
import math
# import numpy as np
from os import path
#from cStringIO import StringIO
#BLOCKSIZE = 65536
#hasher = hashlib.md5()

def main():
    #filepath = sys.argv[1]

    parser = argparse.ArgumentParser(
        description="Accept Console Arguments for programme",
    )

    parser.add_argument(
        '-q',
        help='Query Label',
        nargs=1,
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument(
        '-n',
        help='Num Results',
        nargs=1,
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument(
        '-l',
        help='Generated Lexicons\' file Path',
        nargs=1,
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument(
        '-i',
        help='Generated Inverted Index\'s file Path',
        nargs=1,
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument(
        '-m',
        help='Generated Document Mapping\'s file Path',
        nargs=1,
        type=str
        #type=argparse.FileType('r')
    )

    parser.add_argument('-s',
        help='Remove Stop Words if Argument Passed'
    )

    parser.add_argument(
        'Query_term',
        metavar='Q',
        nargs='+',
        help='Query terms to be searched'
    )

    args = parser.parse_args()
    # query_label = args.q
    # numResults = args.n
    lexicon = args.l
    inverted = args.i
    map = args.m
    Query_term = ' '.join(args.Query_term)
    stoplist_check = args.s != None
    stoplist = args.s
    stopwordsDict = Counter()

    #print(query_label)
    #print(num_results)
    # print(lexicon[0])
    #print(inverted)
    #print(map)
    #print(Query_term)
    if (lexicon == None or not path.exists(lexicon[0])):
        print("File path {} does not exist for lexicon file. Exiting...".format(lexicon))
        sys.exit()

    if (inverted == None or not path.exists(inverted[0])):
        print("File path {} does not exist for inverted list. Exiting...".format(inverted))
        sys.exit()

    if (map == None or not path.exists(map[0])):
        print("File path {} does not exist for map file. Exiting...".format(map))
        sys.exit()

    start_time = time.time()

    if stoplist_check and os.path.isfile(stoplist):
        stopWords = open(stoplist,'r')
        #tStopwords = stopWords.read()
        lStopwords = [line.rstrip('\n') for line in stopWords]
        stopwordsDict.update(lStopwords)

    docmap = defaultdict(list)
    lexicons = defaultdict(list)

    BYTE_ORDER = 'big'
    BYTE_SIZE = 4
    SIGNED = False

    avgDocLength = 0

    numResults = 100
    if args.n != None:
        numResults = int(args.n[0])

    query_label = '9999'
    if args.q != None:
        query_label = args.q[0]

    Counter_Doc = 0
    minHeap = []
    heap = []
    N = 0
    k1 = 1.2
    b = 0.75
    accumulator = collections.OrderedDict()

    with open(lexicon[0], "r") as lex,open(map[0], "r") as mapfile:
        #test = lex.read()
        #print(test)
        lines = lex.readlines()
        maplines = mapfile.readlines()

        #loading lexicon file to memory
        counter_lex = 0
        for linet in lines:
            linet = re.sub(r"\s+",'',linet)
            line = linet.split(':')
            lexicons[line[0]] = [int(line[1]),int(line[2])]
            counter_lex += 1

        #loading Map file to memory
        DocLength = 0
        for maplinet in maplines:
            maplinet = re.sub(r"\s+",'',maplinet)
            mapline = maplinet.split(':')
            docmap[int(mapline[0])] = (mapline[1],int(mapline[2]),float(mapline[3]))
            DocLength += int(mapline[2])
            Counter_Doc += 1

    #count average length of documents to use it in BM25
    if Counter_Doc > 0:
        avgDocLength = DocLength / Counter_Doc

    N = counter_lex

    # print(lexicons)
    # print(docmap)
    Query_term = Query_term.translate(str.maketrans('', '', string.punctuation))
    #Query_term = str.lower(Query_term)
    Query_term = re.sub('\s+', ' ', Query_term)

    terms = set(str.lower(term) for term in Query_term.split(' ') if term)

    for term in terms:
        if term in lexicons.keys():
            value = lexicons[term]
            offset = value[0]
            BytesToRead = value[1]

            DocTfPairs = []
            with open(inverted[0], "rb") as InvertedI:
                InvertedI.seek(offset)
                content = InvertedI.read(BytesToRead)
                for i in range(0, BytesToRead//BYTE_SIZE, 2):
                    docid = struct.unpack(">I",content[i * BYTE_SIZE: (i + 1) * BYTE_SIZE])[0]
                    termFreq = struct.unpack(">I",content[(i + 1) * BYTE_SIZE: (i + 2) * BYTE_SIZE])[0]
                    DocTfPairs.append((docid,termFreq))

            #below part is upated code from assignemt-1 to
            # Calculate BM25 similarity score & store it into accumulators
            for pair in DocTfPairs:
                k = k1 * ((1 - b) + ((b * docmap[pair[0]][1]) / avgDocLength))
                similarityScore = math.log((Counter_Doc - len(DocTfPairs) + 0.5) / (len(DocTfPairs) + 0.5)) *  (((k1 + 1) * pair[1]) / (k + pair[1]))
                if pair[0] in accumulator.keys():
                    accumulator[pair[0]] += similarityScore
                else:
                    accumulator[pair[0]] = similarityScore


    # Final score
    # for Id, simscore in accumulator.items():
    #     accumulator[Id] = accumulator[Id] / docmap[Id][2]

    # print("Accumulator Size : " + str(len(accumulator)))

    # Heapifying accumulator
    AccList = list(accumulator)
    # initialise heap with first numResults accumulator
    for key in AccList[0:numResults]:
        heapq.heappush(minHeap, list((float(accumulator[key]), key)))

    # for subsequent accumulators, process each accumultor by comaring similarity score
    # and if score is more than smallest score from heap, replace that accumulator
    for key in AccList[numResults:len(AccList)]:
        if accumulator[key] > heapq.nsmallest(1, minHeap)[0][0]:
            heapq.heapreplace(minHeap, list((accumulator[key], key)))

    # print(minHeap)

    #Sort the minHeap list to get the highest ranked documents first
    sorted_Heap = heapq.nlargest(numResults, minHeap)
    # print(sorted_Heap)

    # display results to users
    for i in range(0, len(sorted_Heap)):
        print(query_label, docmap[sorted_Heap[i][1]][0], i+1, sorted_Heap[i][0])

    print()
    print()
    print("Running time: ",str((time.time() - start_time)*1000)," ms")


if __name__ == '__main__':
   main()
