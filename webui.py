from flask import Flask, jsonify, render_template, url_for
from flask_googlecharts import GoogleCharts, LineChart
from flask_googlecharts.utils import prep_data
from flask_sqlalchemy import SQLAlchemy
from fandb import SensorData
from gpcharts import figure
import datetime

app = Flask(__name__)
app.debug = True  # Make this False if you are no longer debugging
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/fancontrol/fancontrol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)


charts = GoogleCharts(app)


@app.route("/sql")
def sql():
    wt = []

    starttime = datetime.datetime.today() - datetime.timedelta(hours=1)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        wt.append(row.serialize)

    d = {"cols": [{"id": "", "label": "Date", "pattern": "", "type": "date"},
                  {"id": "", "label": "Water Temp", "pattern": "", "type": "number"}],
         "rows": wt}

    return jsonify(prep_data(d))


@app.route("/fgcharts")
def fgcharts():

    temp_chart = LineChart("temps",
                           options={"title": "Water Temperature",
                                    "width": 1280,
                                    "height": 600,
                                    "hAxis": {"format": "k:m:S"},
                                    "vAxis": {"format": "decimal",
                                              "minValue": "0",
                                              "maxValue": "100"}},
                           data_url=url_for('sql'))

    charts.register(temp_chart)

    return render_template("index.html")


@app.route("/gpcharts")
def gpcharts():
    fig = figure()
    fig.title = 'Water Temp'
    fig.ylabel = 'Temperature'
    fig.height = 800
    fig.width = 1280
    xVals = ['Dates']
    yVals = [['Water']]

    starttime = datetime.datetime.today() - datetime.timedelta(hours=1)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        xVals.append(row.strdate)
        yVals.append(row.getvals)

    fig.plot(xVals, yVals)

    return str(fig)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
