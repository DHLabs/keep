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

if "vocab" in db.collection_names():
	yn = ''
	while ((yn.lower() != 'y') and (yn.lower() != 'n')):
		yn = raw_input("\nVocabulary collection already exists, continuing WILL "
						"drop the collection, and reload it based on the provided "
						"file.  Continue? (y/n)\n")
	if yn is 'n':
		exit(0)
	elif yn is 'y':
		db.drop_collection("vocab")
		print "\n'vocab' collection dropped successfully."
	else:
		exit(1)

db.create_collection('vocab')
collection = db.vocab
print "\nEmpty 'vocab' collection created, starting dump."

with open(filepath, 'r') as infile:
	first = True
	shiftMod = 0
	lineID = 0
	for line in infile:

		# need to do some checks to see if there are extraneous chars
		if first is True:
			first = False
			lastChar = line[-1]
			while re.match('([a-z]|[A-Z]|[0-9])', lastChar) is None:
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
		collection.save( { 'term': prepLine } )

