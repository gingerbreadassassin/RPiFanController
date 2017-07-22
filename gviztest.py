import gviz_api
from pymongo import MongoClient
import datetime
from pprint import pprint

client = MongoClient()
db = client.fancontrol
sd = db.sensordata

data = []

recent = datetime.datetime.today() - datetime.timedelta(seconds=30)
for r in sd.find({'date_time': {'$gt': recent}}):
    data.append({'date_time': r['date_time'], 'wtemp': r['wtemp'], 'target': r['target']})

description = {'date_time': ('datetime', "Date"),
               'wtemp': ('number', 'Water Temp'),
               'target': ('number', 'Target Temp')}

data_table = gviz_api.DataTable(description)
data_table.LoadData(data)

print("Content-type: text/plain")
print()
pprint(data_table.__dict__)
print(data_table.ToJSonResponse())
print(data_table.ToJSon(columns_order=('date_time', 'wtemp', 'target')))
