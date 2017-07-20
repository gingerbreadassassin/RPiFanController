from flask import Flask, render_template
import datetime
from pymongo import MongoClient
import gviz_api

client = MongoClient()
db = client.fancontrol
sd = db.sensordata

app = Flask(__name__)


@app.route("/getdata")
def getdata():
    data = []

    recent = datetime.datetime.today() - datetime.timedelta(seconds=30)
    for r in sd.find({'date_time': {'$gt': recent}}):
        data.append({'date_time': r['date_time'], 'wtemp': r['wtemp']})

    description = {'date_time': ('datetime', "Date"),
                   'wtemp': ('number', 'Water Temp')}

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    return data_table.ToJSon()


@app.route("/")
def gviz():
    return render_template('gviz.html')
