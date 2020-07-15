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
import math
# import numpy as np
import collections
import time
from os import path
#hasher = hashlib.md5()

def main():
    #filepath = sys.argv[1]

    parser = argparse.ArgumentParser(
        description="Accept Console Arguments for programme",
    )

    parser.add_argument('-s',
        help='Remove Stop Words if Argument Passed'
    )

    parser.add_argument(
        '-p',
        help='Print each Tokens when processed if Argument Passed',
        action='store_true',
        default=False
    )

    parser.add_argument(
        'source_file',
        help='Source file Path of original documents list',
        nargs=1,
        type=str
        #type=argparse.FileType('r')
    )

    args = parser.parse_args()
    #print(vars(args))
    #print(args.source_file[0])
    if (args.source_file == None or not path.isfile(args.source_file[0])):
        print("File path {} does not exist for source file. Exiting...".format(args.source_file[0]))
        sys.exit()

    #flag to set if stoplist needs to be processed or not
    wordstoprint = args.p
    # print(wordstoprint)
    stoplist = args.s != None
    stopwordsDict = Counter()

    if stoplist and os.path.isfile(args.s):
        stopWords = open(args.s,'r')
        #tStopwords = stopWords.read()
        lStopwords = [line.rstrip('\n').tolower() for line in stopWords]
        stopwordsDict.update(lStopwords)

    map = defaultdict(list)
    lexicons = defaultdict(list)
    InvertedList = defaultdict(list)
    docsDictionary = defaultdict(list)

    BYTE_SIZE = 4
    SIGNED = False
    BYTE_ORDER = 'big'

    #I_index = InvertedIndex()
    docs = []

    with open(args.source_file[0], 'r') as f:
        # Read the entire file into a string
        contents = f.read()
        docs = re.findall(r'<DOC>\s+(.*?)\s+</DOC>',contents,re.DOTALL)

    cnt = 0
    processingTime = time.time()
    for doc in docs:
        #print(doc)
        head_final = ''
        text_final = ''
        cnt += 1
        heads = re.findall(r'<HEADLINE>\s+(.*?)\s+</HEADLINE>',doc,re.DOTALL)
        for head in heads:
            head_paras = re.findall(r'<P>\s+(.*?)\s+</P>',head,re.DOTALL)
            head_final = " ".join(head_paras)
            #print(head_final)
            head_final = re.sub(r"[^\w\s]",' ',head_final)
            head_final = re.sub(r"\s+",' ',head_final)

        texts = re.findall(r'<TEXT>\s+(.*?)\s+</TEXT>',doc,re.DOTALL)
        for text in texts:
            text_paras = re.findall(r'<P>\s+(.*?)\s+</P>',text,re.DOTALL)
            text_final = " ".join(text_paras)
            #print(text_final)
            text_final = re.sub(r"[^\w\s]",' ',text_final)
            text_final = re.sub(r"\s+",' ',text_final)

        doc_no = re.findall(r'<DOCNO>\s+(.*?)\s+</DOCNO>',doc,re.DOTALL)
        #print(doc_no)

        doc_content = head_final + text_final

        doc_content = doc_content.lower()
        ltTokens = doc_content.split(' ')

        if stoplist:
            lTokens = [token.strip() for token in ltTokens if token not in stopwordsDict if token]
        else:
            lTokens = [token.strip() for token in ltTokens if token] #and not token.isdigit()

        #docsTokenCounter = Counter(lTokens)
        docsTokenCounter = {}

        docWeight = 0
        for key in lTokens:
            #Updated part from assignment-1 for BM25 score calculation
            docsDictionary[key].append(cnt)
            if key in docsTokenCounter.keys():
                docsTokenCounter[key] += 1
            else:
                docsTokenCounter[key] = 1

        if wordstoprint:
            # print('inside')
            for token in docsTokenCounter.keys():
                print(token)

        #calculating doc weight
        for term, freq in docsTokenCounter.items():
            docWeight += math.pow((1 + math.log(freq)), 2)

        docWeight = math.sqrt(docWeight)

        #hash table to store doc details
        map[cnt] = ("".join(doc_no), len(lTokens), docWeight)

    #print(InvertedList)
    for i in docsDictionary.keys():
        docsDictionary[i] = dict(collections.Counter(docsDictionary[i]))

    print("Total Processing Time Taken in Seconds:",time.time() - processingTime)

    writingTime = time.time()
    offset = 0
    with open('lexicon', 'w') as lex,open("invlists", "wb") as InvertedI:
        for key, count in docsDictionary.items():
            occ = len(count)
            #writing lexicon file
            lex.write(key +':'+str(offset)+':'+str(occ * (BYTE_SIZE * 2))+'\n')
            offset = offset + (occ * (BYTE_SIZE * 2))
            #appending values to Inverted listlist
            for docid, termFreq in count.items():
                st = struct.Struct('>I')
                InvertedI.write(st.pack(docid))
                InvertedI.write(st.pack(termFreq))

    #writing map file
    with open('map', 'w') as mapfile:
        for key, value in map.items():
            mapfile.write(str(key) +':' +str(value[0])+':' +str(value[1])+':' +str(value[2])+'\n')

    print("Total Writing Time Taken in Seconds:",time.time() - writingTime)


if __name__ == '__main__':
    startTime = time.time()
    main()
    print("Total Time Taken in Seconds:",time.time() - startTime)
