import datetime
from pymongo import MongoClient

client = MongoClient()
db = client.fancontrol
sd = db.sensordata


def rawdata(ms):
    data = []

    recent = datetime.datetime.today() - datetime.timedelta(milliseconds=ms)
    for r in sd.find({'date_time': {'$gt': recent}}):
        data.append({'date_time': r['date_time'], 'wtemp': r['wtemp'], 'target': r['target'], 'indc': r['indc']})

    return data
