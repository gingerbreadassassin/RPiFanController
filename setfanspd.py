from pymongo import MongoClient
from sys import argv

client = MongoClient()
db = client.fancontrol
sets = db.settings.find_one()

sets['mandc'] = argv[1]
db.settings.replace_one({'_id': sets['_id']}, sets)
