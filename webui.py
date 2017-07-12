from flask import Flask, jsonify, render_template, url_for
from flask_googlecharts import GoogleCharts, BarChart, MaterialLineChart
from flask_googlecharts.utils import prep_data
from flask_sqlalchemy import SQLAlchemy
# from bokeh.plotting import figure
# from bokeh.resources import INLINE
# from bokeh.embed import file_html
import datetime

# import numpy as np
# import sqlite3
# import chartjs

app = Flask(__name__)
app.debug = True  # Make this False if you are no longer debugging
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/fancontrol/fancontrol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)

from fandb import Settings, SensorData, StatData

# test

# @app.route("/")
# def hello():
#     # db = sqlite3.connect('/var/www/fancontrol/fancontrol.db')
#     # cur = db.cursor()
#     # cur.execute("""SELECT rDatetime FROM sensorData WHERE rDatetime
#     #             BETWEEN datetime('2017-06-24 20:00:00') AND datetime('2017-06-24 20:15:00');""")
#     # data = cur.fetchall()
#     # dates = np.array(data, dtype=np.datetime64)
#     #
#     # cur.execute("""select wtemp from sensorData where rDatetime
#     #             BETWEEN datetime('2017-06-24 20:00:00') AND datetime('2017-06-24 20:15:00');""")
#     # data = cur.fetchall()
#     # wt = np.array(data)
#     # db.close()
#
#     dates = []
#     wt = []
#     starttime = datetime.datetime.today() - datetime.timedelta(hours=1)
#     for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
#         dates.append(row.date_time)
#         wt.append(row.wtemp)
#
#     # dates = dates.reshape(-1)
#     # wt = wt.reshape(-1)
#
#     p = figure(width=800, height=350, x_axis_type="datetime")
#     p.line(dates, wt, color='navy', legend='water')
#
#     p.title.text = "Temperatures"
#     p.legend.location = "top_left"
#     p.grid.grid_line_alpha = 0
#     p.xaxis.axis_label = 'Date'
#     p.yaxis.axis_label = 'Celsius'
#     p.ygrid.band_fill_color = "olive"
#     p.ygrid.band_fill_alpha = 0.1
#
#     html = file_html(p, INLINE, "my plot")
#
#     return html

# @app.route("/")
# def chart():
#     dates = []
#     wt = []
#     starttime = datetime.datetime.today() - datetime.timedelta(hours=1)
#     for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
#         dates.append(row.date_time)
#         wt.append(row.wtemp)
#
#     # timestamps = []
#     # for i in range(-59, 1):
#     #     timestamps.append(i)
#     # return render_template('chart.html', values=wt, labels=timestamps)
#
#     mychart = chartjs.chart("My test chart", "Line", 800, 600)
#     mychart.set_labels(dates)
#     mychart.set_params(fillColor="rgba(220,220,220,0.5)", strokeColor="rgba(220,220,220,0.8)",
#                        highlightFill="rgba(220,220,220,0.75)", highlightStroke="rgba(220,220,220,1)", )
#     mychart.add_dataset(wt)
#     html = mychart.make_chart_with_headers()
#     return html


charts = GoogleCharts(app)


@app.route("/data")
def data():

    d = {"cols": [{"id": "", "label": "Date", "pattern": "", "type": "date"},
                  {"id": "", "label": "Spectators", "pattern": "", "type": "number"}],
         "rows": [{"c": [{"v": datetime.date(2016, 5, 1), "f": None}, {"v": 3987, "f": None}]},
                  {"c": [{"v": datetime.date(2016, 5, 2), "f": None}, {"v": 6137, "f": None}]},
                  {"c": [{"v": datetime.date(2016, 5, 3), "f": None}, {"v": 9216, "f": None}]},
                  {"c": [{"v": datetime.date(2016, 5, 4), "f": None}, {"v": 22401, "f": None}]},
                  {"c": [{"v": datetime.date(2016, 5, 5), "f": None}, {"v": 24587, "f": None}]}]}

    return jsonify(prep_data(d))


@app.route("/sql")
def sql():
    # dates = []
    wt = []

    starttime = datetime.datetime.today() - datetime.timedelta(minutes=1)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        # dates.append(row.date_time)
        wt.append(row.serialize)

    d = {"cols": [{"id": "", "label": "Date", "pattern": "", "type": "date"},
                  {"id": "", "label": "Water Temp", "pattern": "", "type": "number"}],
         "rows": wt}

    return jsonify(prep_data(d))


@app.route("/")
def index():
    hot_dog_chart = BarChart("hot_dogs", options={"title": "Contest Results",
                                                  "width": 500,
                                                  "height": 300})

    hot_dog_chart.add_column("string", "Competitor")
    hot_dog_chart.add_column("number", "Hot Dogs")
    hot_dog_chart.add_rows([["Matthew Stonie", 62],
                            ["Joey Chestnut", 60],
                            ["Eater X", 35.5],
                            ["Erik Denmark", 33],
                            ["Adrian Morgan", 31]])

    charts.register(hot_dog_chart)

    spectators_chart = MaterialLineChart("spectators",
                                         options={"title": "Contest Spectators",
                                                  "width": 500,
                                                  "height": 300},
                                         data_url=url_for('data'))

    charts.register(spectators_chart)

    temp_chart = MaterialLineChart("temps",
                                         options={"title": "Water Temperature",
                                                  "width": 500,
                                                  "height": 300},
                                         data_url=url_for('sql'))

    charts.register(temp_chart)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
