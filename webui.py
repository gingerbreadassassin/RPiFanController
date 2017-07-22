from flask import Flask, render_template, request
import datetime
from pymongo import MongoClient
import gviz_api

client = MongoClient()
db = client.fancontrol
sd = db.sensordata

app = Flask(__name__)
app.debug = True


@app.route("/getdata/<int:ms>")
def getdata(ms):
    data = []

    recent = datetime.datetime.today() - datetime.timedelta(milliseconds=ms)
    for r in sd.find({'date_time': {'$gt': recent}}):
        data.append({'date_time': r['date_time'], 'wtemp': r['wtemp'], 'target': r['target']})

    description = {'date_time': ('datetime', "Date"),
                   'wtemp': ('number', 'Water Temp'),
                   'target': ('number', 'Target Temp')}

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    return data_table.ToJSon(columns_order=('date_time', 'wtemp', 'target'))


@app.route("/settings/<settings>", methods=['GET', 'POST'])
def setmandc(settings):
    sets = db.settings.find_one()
    if request.method == 'GET':
        sets.pop('_id')
        return sets

    else:
        # TODO: parse settings from json
        db.settings.replace_one({'_id': sets['_id']}, sets)


@app.route("/")
def gviz():
    return render_template('gviz.html')
