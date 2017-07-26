from flask import Flask, render_template, request, jsonify
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
        data.append({'date_time': r['date_time'], 'wtemp': r['wtemp'], 'target': r['target'], 'indc': r['indc']})

    description = {'date_time': ('datetime', "Date"),
                   'wtemp': ('number', 'Water Temp'),
                   'target': ('number', 'Target Temp'),
                   'indc': ('number', 'Intake Fan Speed %')}

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    return data_table.ToJSon(columns_order=('date_time', 'wtemp', 'target', 'indc'))


@app.route("/settings/", methods=['GET', 'POST'])
def getsetsets():
    sets = db.settings.find_one()
    if request.method == 'GET':
        sets.pop('_id')
        return jsonify(sets)

    else:
        newsets = request.json
        sets['bias'] = float(newsets['bias'])
        sets['kd'] = float(newsets['kd'])
        sets['ki'] = float(newsets['ki'])
        sets['kp'] = float(newsets['kp'])
        sets['mandc'] = int(newsets['mandc'])
        sets['target'] = float(newsets['target'])
        sets['use_pid'] = newsets['use_pid']

        db.settings.replace_one({'_id': sets['_id']}, sets)
        return '', 204


@app.route("/")
def gviz():
    return render_template('gviz.html')
