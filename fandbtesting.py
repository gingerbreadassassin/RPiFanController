from fandb import SensorData
from flask import Flask
import json
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.debug = True  # Make this False if you are no longer debugging
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/fancontrol/fancontrol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)


def prep_data(data):
    # type: (dict) -> dict
    """Takes a dict intended to be converted to JSON for use with Google Charts and transforms date and datetime
    into date string representations as described here:

    https://developers.google.com/chart/interactive/docs/datesandtimes

    TODO:  Implement Timeofday formatting"""

    for row in data['rows']:
        for val in row['c']:
            if isinstance(val['v'], datetime.datetime):
                val['v'] = "Date({}, {}, {}, {}, {}, {}, {})".format(val['v'].year,
                                                                     val['v'].month - 1,  # JS Dates are 0-based
                                                                     val['v'].day,
                                                                     val['v'].hour,
                                                                     val['v'].minute,
                                                                     val['v'].second,
                                                                     val['v'].microsecond)
            elif isinstance(val['v'], datetime.date):
                val['v'] = "Date({}, {}, {})".format(val['v'].year,
                                                     val['v'].month-1,  # JS Dates are 0-based
                                                     val['v'].day)
    return data

json.JSONEncoder
def sql():
    wt = []

    starttime = datetime.datetime.today() - datetime.timedelta(minutes=1)
    for row in db.session.query(SensorData).filter(SensorData.date_time > starttime).all():
        # dates.append(row.date_time)
        wt.append(row.serialize)

    d = {"cols": [{"id": "", "label": "Date", "pattern": "", "type": "date"},
                  {"id": "", "label": "Water Temp", "pattern": "", "type": "number"}],
         "rows": wt}

    return json.dumps(prep_data(d))

if __name__ == "__main__":
    print(sql())
