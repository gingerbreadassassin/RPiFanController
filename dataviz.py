import sqlite3
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from fansql import SensorData
import numpy as np
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.embed import file_html
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/fancontrol/fancontrol.db'
db = SQLAlchemy(app)

start = time.time()
print('connecting to db at ', start)

session = db.session()

stop = time.time()
print('connected to db after ', stop - start)


start = time.time()
print('querying db at ', start)
values = session.query(SensorData).filter(SensorData.rDatetime > datetime('2017-06-24 20:00:00')).filter(SensorData.rDatetime < datetime('2017-06-24 20:15:00')).all()

for val in values:
    dates = val.rDatetime
    wt = val.wtemp

stop = time.time()
print('data grabbed after ', stop - start)

start = time.time()
print('creating np array ', start)
dates = np.array(dates, dtype=np.datetime64)
stop = time.time()
print('np array took ', stop - start)

# start = time.time()
# print('querying db at ', start)
#
# stop = time.time()
# print('data grabbed after ', stop - start)

start = time.time()
print('creating np array ', start)
wt = np.array(wt)
stop = time.time()
print('np array took ', stop - start)
session.close()

start = time.time()
print('manipulating np arrays at ', start)
dates = dates.reshape(-1)
wt = wt.reshape(-1)
stop = time.time()
print('np array manip took ', stop - start)

start = time.time()
print('generating graph at ', start)
window_size = 30
window = np.ones(window_size)/float(window_size)

p = figure(width=800, height=350, x_axis_type="datetime")
p.line(dates, wt, color='navy', legend='water')

p.title.text = "Temperatures"
p.legend.location = "top_left"
p.grid.grid_line_alpha = 0
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Celsius'
p.ygrid.band_fill_color = "olive"
p.ygrid.band_fill_alpha = 0.1

html = file_html(p, INLINE, "my plot")

stop = time.time()
print('graph / html gen took ', stop - start)


print(dates, wt)
