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
    if not os.path.isfile(args.source_file[0]):
        print("File path {} does not exist. Exiting...".format(args.source_file[0]))
        sys.exit()

    wordstoprint = args.p
    stoplist = args.s != None
    stopwordsDict = Counter()

    if stoplist and os.path.isfile(args.s):
        stopWords = open(args.s,'r')
        #tStopwords = stopWords.read()
        lStopwords = [line.rstrip('\n') for line in stopWords]
        stopwordsDict.update(lStopwords)

    map = defaultdict(list)
    lexicons = defaultdict(list)
    InvertedList = defaultdict(list)

    #I_index = InvertedIndex()
    docs = []

    with open(args.source_file[0], 'r') as f:
        # Read the entire file into a string
        contents = f.read()
        docs = re.findall(r'<DOC>\s+(.*?)\s+</DOC>',contents,re.DOTALL)

    cnt = 0

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
        map[cnt] = "".join(doc_no)
        doc_content = head_final + text_final

        doc_content = doc_content.lower()
        ltTokens = doc_content.split(' ')

        if stoplist:
            lTokens = [token.strip() for token in ltTokens if token not in stopwordsDict if token]
        else:
            lTokens = [token.strip() for token in ltTokens if token] #and not token.isdigit()

        docsTokenCounter = Counter(lTokens)

        if wordstoprint:
            for token in docsTokenCounter.keys():
                print(token)

        for key, occurrence in docsTokenCounter.items():
            values = InvertedList.setdefault(key, [])
            values.append(cnt)
            values.append(occurrence)

    #print(InvertedList)

    offset = 0
    with open('lexicon.txt', 'w') as lex,open("invlists.txt", "wb") as InvertedI:
        for key in InvertedList:
            occ = int(len(InvertedList[key])/2)
            lex.write(key +':'+str(occ)+':'+str(offset)+'\n')
            offset = offset + (occ*2)
            for value in InvertedList[key]:
                InvertedI.write(struct.pack("i", value))

    with open('map.txt', 'w') as mapfile:
        for key in map:
            mapfile.write(str(key) +':' +map[key]+'\n')


if __name__ == '__main__':
   main()
