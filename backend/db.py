from pymongo import MongoClient

connection = MongoClient()
db = connection[ 'dhlab' ]
