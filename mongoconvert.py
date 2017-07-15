from fansqla import setup, SensorData, Settings, StatData
from pymongo import MongoClient

client = MongoClient()
db = client.fancontrol
sensordata = db.sensordata
settings = db.settings
stats = db.statistics

session = setup()

for row in session.query(Settings).all():
    sensor = {"date": row.date_time,
              "intemp": row.intemp,
              "inhum": row.inhum,
              "extemp1"
              }
    settings.insert_one(sets)


