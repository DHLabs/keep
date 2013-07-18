'''
	This is a standalone script that is to be
	used to load the vocab into the server's
	mongo database.  This only needs to be run
	once, with the appropriate vocabulary on the
	filesystem as a	one column flat list text file.
'''

import re
import sys

import pymongo as pm

from optparse import OptionParser

'''
	This is a method to check if a string contains only 
	alphanumeric characters
'''
def re_sanitize(string, search=re.compile(r'[^a-zA-Z0-9-]').search):
	return not bool( search(string) )

db = None

client = pm.MongoClient()
filepath = raw_input("\nEnter the filename & path (either "
						"exact or from the current directory) "
						"to the flat vocab list: ")


try:
	db = client['dhlab']
except:
	print "\nDHLab database does not exist.  Please initialize database first.  Exiting now."
	exit(1)

'''
	This presents a menu, and forces the user to choose one of the options in
	the option Dictionary if the vocab collection already exists.
'''
if "vocab" in db.collection_names():
	options = ''
	optionDict = ['i', 'd', 'e']
	while (options.lower() not in optionDict):
		options = raw_input("\nVocabulary collection already exists. I can do one of the following:\n"
							"(I)\tINSERT this vocab into the current collection.\n"
							"(D)\tDROP the collection and start clean. (Irreversable!)\n"
							"(E)\tEXIT the program.\n"
							"(Type the above lettter corresponding to the chosen option and hit Return)\n")
	if options.lower() == 'i':
		pass
	elif options.lower() == 'd':
		yn = raw_input("\nContinuing WILL drop the collection, and reload it based on the provided\n"
						"file.  Continue? (yes) for yes, or any other key or phrase for no.\n"
						"NOTE: This is irreversible!\n")
		if yn == 'yes':
			db.drop_collection("vocab")
			print "\n'vocab' collection dropped successfully."
			db.create_collection("vocab")
		else:
			pass
	else:
		exit(0)
else:
	db.create_collection('vocab')  #Create the collection if it doesn't already exist.
	print "\nEmpty 'vocab' collection created."

collection = db.vocab

# Get a name for this group.
vocabName = raw_input("Provide a name for this vocabulary (only alphanumeric characters and dashes)\n"
						  "(Ex: ICD-10, UMLS)\n")
while not re_sanitize(vocabName):
	vocabName = raw_input("Invalid vocabulary name!\n"
							  "Provide a name for this vocabulary (only alphanumeric characters and dashes)\n"
						  	  "(Ex: ICD-10, UMLS)\n")

with open(filepath, 'r') as infile:
	first = True
	shiftMod = 0

	for line in infile:

		# need to do some checks to see if there are extraneous chars
		if first is True:
			first = False
			lastChar = line[-1]
			while not re_sanitize(lastChar):
				print "\nCurrent first line: ", line[:len(line) - shiftMod - 1]
				yn = raw_input("Last character of the first line is non-alphanumeric. "
								"If this is a CSV file, a character might have been added "
								"to the end of every line.  Would you like to remove the"
								" last character from every line? (y/n)\n")
				if yn is 'y':
					shiftMod += 1
					lastChar = line[-(1 + shiftMod)]
				else:
					break


		# Insert the lines into the vocab database!
		prepLine = line[:len(line) - shiftMod - 1]
		collection.save( { 'group': vocabName, 'term': prepLine } )

