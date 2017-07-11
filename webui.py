from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
# from bokeh.plotting import figure
# from bokeh.resources import INLINE
# from bokeh.embed import file_html
import datetime
# import numpy as np
# import sqlite3
import chartjs

app = Flask(__name__)
app.debug = True  # Make this False if you are no longer debugging
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/fancontrol/fancontrol.db'
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

@app.route("/")
def chart():
    dates = []
    wt = []
    starttime = datetime.datetime.today() - datetime.timedelta(hours=1)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        dates.append(row.date_time)
        wt.append(row.wtemp)

    # timestamps = []
    # for i in range(-59, 1):
    #     timestamps.append(i)
    # return render_template('chart.html', values=wt, labels=timestamps)

    mychart = chartjs.chart("My test chart", "Line", 800, 600)
    mychart.set_labels(dates)
    mychart.set_params(fillColor="rgba(220,220,220,0.5)", strokeColor="rgba(220,220,220,0.8)",
                       highlightFill="rgba(220,220,220,0.75)", highlightStroke="rgba(220,220,220,1)", )
    mychart.add_dataset(wt)
    html = mychart.make_chart_with_headers()
    return html
