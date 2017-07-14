import json
from urllib.request import urlopen
from flask import Flask, jsonify, render_template, url_for
from flask_googlecharts import GoogleCharts, LineChart
from flask_googlecharts.utils import prep_data
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup

from fandb import SensorData
from gpcharts import figure
import plotlywrapper
import datetime
from plotly.offline import plot
from plotly.graph_objs import Scattergl

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


@app.route("/plotly")
def plotly():

    xvals = []
    yvals = []

    starttime = datetime.datetime.today() - datetime.timedelta(hours=12)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        xvals.append(row.date_time)
        yvals.append(row.wtemp)

    trace0 = Scattergl(
        x=xvals,
        y=yvals,
        mode='lines+markers',
        name='Water Temps'
    )

    data = [trace0]

    fig = plot(data, output_type='div')

    return render_template('plotly.html', div_placeholder=Markup(fig))


@app.route("/pwrap")
def pwrap():

    xvals = []
    yvals = []

    starttime = datetime.datetime.today() - datetime.timedelta(hours=1)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        xvals.append(row.date_time)
        yvals.append(row.wtemp)

    graph = plotlywrapper.line(xvals, yvals)
    graph.ylim(0, 100)

    return graph.show()


def getExchangeRates():
    rates = []
    response = urlopen('http://api.fixer.io/latest')
    data = response.read().decode("utf-8")
    rdata = json.loads(data, parse_float=float)

    rates.append(rdata['rates']['USD'])
    rates.append(rdata['rates']['GBP'])
    rates.append(rdata['rates']['HKD'])
    rates.append(rdata['rates']['AUD'])
    return rates


@app.route("/gchart")
def gchart():
    rates = getExchangeRates()
    return render_template('gchart.html', **locals())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
