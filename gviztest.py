import gviz_api
from pymongo import MongoClient
import datetime

client = MongoClient()
db = client.fancontrol
sd = db.sensordata

data = []

recent = datetime.datetime.today() - datetime.timedelta(seconds=30)
for r in sd.find({'date_time': {'$gt': recent}}):
    data.append({'date_time': r['date_time'], 'wtemp': r['wtemp']})

description = {'date_time': ('datetime', "Date"),
               'wtemp': ('number', 'Water Temp')}

data_table = gviz_api.DataTable(description)
data_table.LoadData(data)

print("Content-type: text/plain")
print()
print(data_table.ToJSon())
