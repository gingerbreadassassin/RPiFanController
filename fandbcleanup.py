import datetime
from pymongo import MongoClient

client = MongoClient()
db = client.fancontrol
sd = db.sensordata

too_old = datetime.datetime.today() - datetime.timedelta(hours=12)
sd.delete_many({'date_time': {'$lt': too_old}})
