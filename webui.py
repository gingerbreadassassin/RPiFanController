from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from scipy.signal import savgol_filter
from fandb import SensorData
import datetime
import pytz
from plotly.offline import plot
from plotly.graph_objs import Scattergl

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/fancontrol/fancontrol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)


@app.route("/smoothplotly")
def smoothplotly():

    timestamps = []
    wtemps = []
    ints = []
    ext1s = []
    ext2s = []
    targets = []
    dcs = []

    starttime = datetime.datetime.today() - datetime.timedelta(hours=12)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        timestamps.append(row.date_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Chicago")).replace(tzinfo=None))
        wtemps.append(row.wtemp)
        ints.append(row.intemp)
        ext1s.append(row.extemp1)
        ext2s.append(row.extemp2)
        targets.append(row.target)
        dcs.append(row.indc)

    trace0 = Scattergl(
        x=timestamps,
        y=savgol_filter(wtemps, 51, 3),
        mode='lines',
        name='Water Temp',
        line=dict(color='rgba(57, 106, 177)')
    )

    trace1 = Scattergl(
        x=timestamps,
        y=targets,
        mode='lines',
        name='Target Temp',
        line=dict(color='rgba(204, 37, 41)')
    )

    trace2 = Scattergl(
        x=timestamps,
        y=savgol_filter(dcs, 51, 3),
        mode='lines',
        name='Duty Cycle',
        line=dict(color='rgba(148, 139, 61)')
    )

    trace3 = Scattergl(
        x=timestamps,
        y=savgol_filter(ints, 51, 3),
        mode='lines',
        name='Intake Temp',
        line=dict(color='rgba(62, 150, 81)')
    )

    trace4 = Scattergl(
        x=timestamps,
        y=savgol_filter(ext1s, 51, 3),
        mode='lines',
        name='Top Exhaust Temp',
        line=dict(color='rgba(107, 76, 154)')
    )

    trace5 = Scattergl(
        x=timestamps,
        y=savgol_filter(ext2s, 51, 3),
        mode='lines',
        name='Rear Exhaust Temp',
        line=dict(color='rgba(218, 124, 48)')
    )

    data = [trace0, trace1, trace2, trace3, trace4, trace5]

    fig = plot(data, output_type='div')

    return render_template('plotly.html', div_placeholder=Markup(fig))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
