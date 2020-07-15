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
import itertools
#hasher = hashlib.md5()

map = defaultdict(list)
lexicons = defaultdict(list)
InvertedList = defaultdict(list)
docsDictionary = defaultdict(list)

BYTE_SIZE = 4
SIGNED = False
BYTE_ORDER = 'big'
BufferSize = 30000

BufferNum = 0
docsinBuffer = 0

#I_index = InvertedIndex()
docs = []
cnt = 0
LexiconList = []

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

wordstoprint = args.p
stoplist = args.s != None
stopwordsDict = Counter()

if stoplist and os.path.isfile(args.s):
    stopWords = open(args.s,'r')
    #tStopwords = stopWords.read()
    lStopwords = [line.rstrip('\n').tolower() for line in stopWords]
    stopwordsDict.update(lStopwords)

LexiconFinal = defaultdict(list)

def main():
    #filepath = sys.argv[1]
    global map
    global docs
    global InvertedList
    global LexiconList
    global LexiconList_Buffer
    global BufferNum
    global docsinBuffer
    global LexiconFinal
    global cnt

    processingTime = time.time()
    with open(args.source_file[0], 'r') as f:

        currentDoc = ''
        #read file line by line instead of loading whole file to memory
        for contents in f:
            # contents = f.read()
            currentDoc += contents
            if re.search('</DOC>',contents) is not None:
                #add document to list when end of document is identified
                docs.append(currentDoc)
                docsinBuffer += 1
                currentDoc = ''

                if docsinBuffer == BufferSize:
                    # print('inside')
                    BufferstartTime = time.time()
                    BufferNum += 1
                    #Write partial Index of a buffer to memory
                    LexiconList.append(WriteIndex(docs, BufferNum))
                    print("Time Taken to parse Buffer -",BufferNum,':',time.time() - BufferstartTime, 'Seconds')
                    docs = []
                    docsDictionary = []
                    map = []
                    LexiconList_Buffer = []

                    docsinBuffer = 0

        #Write partial Index of remaining docs after last buffer to memory
        if docsinBuffer > 0:
            BufferstartTime = time.time()
            BufferNum += 1
            #append returned lexicon info dictionary for particular Buffer to a LexiconList
            LexiconList.append(WriteIndex(docs, BufferNum))
            print("Time Taken to parse Buffer -",BufferNum,':',time.time() - BufferstartTime, 'Seconds')
            docs = []
            docsDictionary = []
            map = []
            LexiconList_Buffer = []

    #print(InvertedList)
    # for i in docsDictionary.keys():
    #     docsDictionary[i] = dict(collections.Counter(docsDictionary[i]))
    print("Total Time for Processing & writing temporary files in Seconds:",time.time() - processingTime)

    writingTime = time.time()
    #Iterate through all temporary map file & combine it to one final map file
    with open('map', 'w') as mapfile:
        for num in range(1,BufferNum+1):
            with open("MapBuffer_"+str(num)+".tmp", "r") as BuffermapFile:
                for line in BuffermapFile.readlines():
                    tokens = line.split(':')
                    # map[tokens[0]] = [tokens[1], tokens[2], tokens[3]]
                    mapfile.write(str(tokens[0]) +':' +str(tokens[1])+':' +str(tokens[2])+':' +str(tokens[3]))

    # print(map.items())

    #combine all buffers lexicon info into one dictionary
    for elem in LexiconList:
        for key, value in elem.items():
            LexiconFinal[key].append(value[0])

    # print(LexiconFinal.items())
    offset = 0

    with open('lexicon', 'w') as lex,open("invlists", "wb") as InvertedI:
        for keyWord, meta in LexiconFinal.items():
            # print(key)
            count = []
            # Iterate through all relevant temporary Index file for given keyword & combine it
            # to one list & write to final Index file and Lexicon final for a keyword
            for lexinfo in LexiconFinal[keyWord]:
                content = []
                with open("IndexBuffer_"+str(lexinfo[0])+".tmp", "r") as indexFile:
                    indexFile.seek(lexinfo[1])
                    content = indexFile.read(lexinfo[2])
                # print(content)

                temp = []
                for term in content.split(";"):
                    if term:
                        temp.append((int(term.split(":")[0]), int(term.split(":")[1])))
                        # count.append(list((int(term.split(":")[0]), int(term.split(":")[1]))))
                        # print(term)
                count.append(list(temp))

            count = list(itertools.chain.from_iterable(count))
            occ = len(count)
            # print(keyWord)
            lex.write(keyWord +':'+str(offset)+':'+str(occ * (BYTE_SIZE * 2))+'\n')
            offset = offset + (occ * (BYTE_SIZE * 2))
            for items in count:
                docid = items[0]
                termFreq = items[1]
                st = struct.Struct('>I')
                InvertedI.write(st.pack(docid))
                InvertedI.write(st.pack(termFreq))

    print("Total Writing Time Taken in Seconds:",time.time() - writingTime)

    # print(cnt)
    # with open('map', 'w') as mapfile:
    #     for key, value in map.items():
    #         mapfile.write(str(key) +':' +str(value[0])+':' +str(value[1])+':' +str(value[2])+'\n')


# Stored Old code as function to Write Inverted index for each buffer
def WriteIndex(docs, BufferNum):

    global map
    global docsDictionary
    global InvertedList
    global LexiconList
    global cnt
    global stoplist
    global wordstoprint
    global stopwordsDict

    map = defaultdict(list)
    docsDictionary = defaultdict(list)
    LexiconList_Buffer = defaultdict(list)

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
            docsDictionary[key].append(cnt)
            if key in docsTokenCounter.keys():
                docsTokenCounter[key] += 1
            else:
                docsTokenCounter[key] = 1

        if wordstoprint:
            for token in docsTokenCounter.keys():
                print(token)

        for term, freq in docsTokenCounter.items():
            docWeight += math.pow((1 + math.log(freq)), 2)

        docWeight = math.sqrt(docWeight)

        map[cnt] = ("".join(doc_no), len(lTokens), docWeight)

    #Write temporary map file for a buffer
    with open("MapBuffer_"+str(BufferNum)+".tmp", "w") as BufferMapFile:
        for key, value in map.items():
            BufferMapFile.write(str(key) +':' +str(value[0])+':' +str(value[1])+':' +str(value[2])+'\n')

    for i in docsDictionary.keys():
        docsDictionary[i] = dict(collections.Counter(docsDictionary[i]))

    offset1 = 0
    #Write temporary Index file for a buffer
    with open(str("IndexBuffer_"+str(BufferNum)+".tmp"),"w+") as TempFile:
        for i, value in docsDictionary.items():
            size = 0
            DocTFPair = ""
            for docId, termfreq in value.items():
                DocTFPair += str(docId) + ":" + str(termfreq) +";"
            size += len(DocTFPair)
            TempFile.write(DocTFPair)
            LexiconList_Buffer[i].append([BufferNum,offset1,size])
            offset1 += len(DocTFPair)

    #return dictionary of information for lexicon to buffer & offset details
    return LexiconList_Buffer

if __name__ == '__main__':
   startTime = time.time()
   main()
   print("Total Time Taken in Seconds :",time.time() - startTime)
