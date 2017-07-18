import datetime
from pymongo import MongoClient
from pprint import pprint

client = MongoClient()
db = client.fancontrol
sd = db.sensordata

recent = datetime.datetime.today() - datetime.timedelta(seconds=10)
for r in sd.find({'date_time': {'$gt': recent}}):
    pprint(r)
