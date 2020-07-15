Vikas Virani - s3715555
Tejel Rumao - s3683206

Instructions:

1) Load index.py & search.py into a folder.

2) Run "index.py [-s S] [-p] source_file("/home/inforet/a1/latimes" file path)"
	Where, -p & -s are optional flags,
		if -p is provided, it prints each token as it is processed
		if -s is provided, S should have a file path of stoplist words to process those stop words.

3) Above program will generate 3 text files, "invlist.txt", "lexicon.txt" & "map.txt" in the same folder where index.py file resides.

4) From the same folder, Run "search.py [lexicon] [invlists] [map] Q [Q ...]"
	Where, [lexicon], [invlists] & [map] are the file paths of the three text files generated from bove program.
		Q [Q ...] is 1 or More query term to be searched.

5) Executing this program will display the information about each term in the below format;

	[term]
	[document_frequency of term]
	[Documnet_number in whch term exists] [within_document_term_frequency]
	.....
	.....

	and so on, for each term.