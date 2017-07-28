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


@app.route("/rtd/")
def realtimedata():
    data = []

    for r in sd.find().skip(sd.count() - 1):
        r.pop('_id')
        data.append(r)

    return jsonify(data)


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


@app.route("/stats/", methods=['GET', 'POST'])
def getstats():
    stats = db.statdata.find_one()
    if request.method == 'GET':
        stats.pop('_id')
        return jsonify(stats)

    else:
        stats = {'_id': stats['_id'],
                 'exhum_avg': 0.0,
                 'exhum_max': 0.0,
                 'exhum_min': 100.0,
                 'exhum_tot': 0.0,
                 'extemp1_avg': 0.0,
                 'extemp1_max': 0.0,
                 'extemp1_min': 100.0,
                 'extemp1_tot': 0.0,
                 'extemp2_avg': 0.0,
                 'extemp2_max': 0.0,
                 'extemp2_min': 100.0,
                 'extemp2_tot': 0.0,
                 'inhum_avg': 0.0,
                 'inhum_max': 0.0,
                 'inhum_min': 100.0,
                 'inhum_tot': 0.0,
                 'intemp_avg': 0.0,
                 'intemp_max': 0.0,
                 'intemp_min': 100.0,
                 'intemp_tot': 0.0,
                 'samples': 0,
                 'watts_avg': 0.0,
                 'watts_max': 0.0,
                 'watts_min': 100.0,
                 'watts_tot': 0.0,
                 'wtemp_avg': 0.0,
                 'wtemp_max': 0.0,
                 'wtemp_min': 100.0,
                 'wtemp_tot': 0.0}

        db.statdata.replace_one({'_id': stats['_id']}, stats)
        return '', 204


@app.route("/")
def gviz():
    return render_template('gviz.html')
