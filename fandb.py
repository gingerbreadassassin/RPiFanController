from flask import Flask
# from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/fancontrol/fancontrol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bias = db.Column(db.Float)
    man_dc = db.Column(db.Float)
    use_pid = db.Column(db.Boolean)
    target = db.Column(db.Float)
    kp = db.Column(db.Float)
    ki = db.Column(db.Float)
    kd = db.Column(db.Float)

    def __init__(self, bias, man_dc, use_pid, target, kp, ki, kd):
        self.bias = bias
        self.man_dc = man_dc
        self.use_pid = use_pid
        self.target = target
        self.kp = kp
        self.ki = ki
        self.kd = kd


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, index=True)
    intemp = db.Column(db.Float)
    inhum = db.Column(db.Float)
    extemp1 = db.Column(db.Float)
    exhum = db.Column(db.Float)
    extemp2 = db.Column(db.Float)
    wtemp = db.Column(db.Float)
    inrpm1 = db.Column(db.Float)
    inrpm2 = db.Column(db.Float)
    indc = db.Column(db.Float)
    exrpm1 = db.Column(db.Float)
    exrpm2 = db.Column(db.Float)
    exrpm3 = db.Column(db.Float)
    exdc = db.Column(db.Float)
    prpm = db.Column(db.Float)
    watts = db.Column(db.Float)
    target = db.Column(db.Float)

    # def __init__(self, sensordata):
    #     self.date_time = datetime.utcnow()
    #     self.intemp = sensordata[0]
    #     self.inhum = sensordata[1]
    #     self.extemp1 = sensordata[2]
    #     self.exhum = sensordata[3]
    #     self.extemp2 = sensordata[4]
    #     self.wtemp = sensordata[5]
    #     self.inrpm1 = sensordata[6]
    #     self.inrpm2 = sensordata[7]
    #     self.indc = sensordata[8]
    #     self.exrpm1 = sensordata[9]
    #     self.exrpm2 = sensordata[10]
    #     self.exrpm3 = sensordata[11]
    #     self.exdc = sensordata[12]
    #     self.prpm = sensordata[13]
    #     self.watts = sensordata[14]
    #     self.target = sensordata[15]

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        # return {
        #     'id': self.id,
        #     'date_timet': dump_datetime(self.date_time),
        #     'wtemp': self.wtemp
        #     # This is an example how to deal with Many2Many relations
        #     # 'many2many': self.serialize_many2many
        # }
        return {
            "c": [{"v": dump_datetime(self.date_time), "f": None}, {"v": self.wtemp, "f": None}]
        }

    # @property
    # def serialize_many2many(self):
    #     """
    #     Return object's relations in easily serializeable format.
    #     NB! Calls many2many's serialize property.
    #     """
    #     return [item.serialize for item in self.many2many]


class StatData(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # intake temperature
    intemp_tot = db.Column(db.Float)
    intemp_min = db.Column(db.Float)
    intemp_max = db.Column(db.Float)
    intemp_avg = db.Column(db.Float)

    # intake relative humidity
    inhum_tot = db.Column(db.Float)
    inhum_min = db.Column(db.Float)
    inhum_max = db.Column(db.Float)
    inhum_avg = db.Column(db.Float)

    # exhaust temperature 1
    extemp1_tot = db.Column(db.Float)
    extemp1_min = db.Column(db.Float)
    extemp1_max = db.Column(db.Float)
    extemp1_avg = db.Column(db.Float)

    # exhaust relative humidity
    exhum_tot = db.Column(db.Float)
    exhum_min = db.Column(db.Float)
    exhum_max = db.Column(db.Float)
    exhum_avg = db.Column(db.Float)

    # exhaust temperature 2
    extemp2_tot = db.Column(db.Float)
    extemp2_min = db.Column(db.Float)
    extemp2_max = db.Column(db.Float)
    extemp2_avg = db.Column(db.Float)

    # water temperature
    wtemp_tot = db.Column(db.Float)
    wtemp_min = db.Column(db.Float)
    wtemp_max = db.Column(db.Float)
    wtemp_avg = db.Column(db.Float)

    # watts
    watts_tot = db.Column(db.Float)
    watts_min = db.Column(db.Float)
    watts_max = db.Column(db.Float)
    watts_avg = db.Column(db.Float)

    # total number of samples
    samples = db.Column(db.Integer)

    # def __init__(self, statdata):
    #     # intake temperature
    #     self.intemp_tot = statdata[0]
    #     self.intemp_min = statdata[1]
    #     self.intemp_max = statdata[2]
    #     self.intemp_avg = statdata[3]
    #
    #     # intake relative humidity
    #     self.inhum_tot = statdata[4]
    #     self.inhum_min = statdata[5]
    #     self.inhum_max = statdata[6]
    #     self.inhum_avg = statdata[7]
    #
    #     # exhaust temperature 1
    #     self.extemp1_tot = statdata[8]
    #     self.extemp1_min = statdata[9]
    #     self.extemp1_max = statdata[10]
    #     self.extemp1_avg = statdata[11]
    #
    #     # exhaust relative humidity
    #     self.exhum_tot = statdata[12]
    #     self.exhum_min = statdata[13]
    #     self.exhum_max = statdata[14]
    #     self.exhum_avg = statdata[15]
    #
    #     # exhaust temperature 2
    #     self.extemp2_tot = statdata[16]
    #     self.extemp2_min = statdata[17]
    #     self.extemp2_max = statdata[18]
    #     self.extemp2_avg = statdata[19]
    #
    #     # water temperature
    #     self.wtemp_tot = statdata[20]
    #     self.wtemp_min = statdata[21]
    #     self.wtemp_max = statdata[22]
    #     self.wtemp_avg = statdata[23]
    #
    #     # watts
    #     self.watts_tot = statdata[24]
    #     self.watts_min = statdata[25]
    #     self.watts_max = statdata[26]
    #     self.watts_avg = statdata[27]
    #
    #     # total number of samples
    #     self.samples = statdata[28]
