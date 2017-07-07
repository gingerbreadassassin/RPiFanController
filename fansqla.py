# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
metadata = Base.metadata


def setup():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite:///fancontrol.db')
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()


class SensorData(Base):
    __tablename__ = 'sensor_data'

    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, index=True)
    intemp = Column(Float)
    inhum = Column(Float)
    extemp1 = Column(Float)
    exhum = Column(Float)
    extemp2 = Column(Float)
    wtemp = Column(Float)
    inrpm1 = Column(Float)
    inrpm2 = Column(Float)
    indc = Column(Float)
    exrpm1 = Column(Float)
    exrpm2 = Column(Float)
    exrpm3 = Column(Float)
    exdc = Column(Float)
    prpm = Column(Float)
    watts = Column(Float)
    target = Column(Float)

    def __init__(self, sensordata):
        self.date_time = datetime.utcnow()
        self.intemp = sensordata[0]
        self.inhum = sensordata[1]
        self.extemp1 = sensordata[2]
        self.exhum = sensordata[3]
        self.extemp2 = sensordata[4]
        self.wtemp = sensordata[5]
        self.inrpm1 = sensordata[6]
        self.inrpm2 = sensordata[7]
        self.exrpm1 = sensordata[8]
        self.exrpm2 = sensordata[9]
        self.exrpm3 = sensordata[10]
        self.prpm = sensordata[11]
        self.watts = sensordata[12]


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    bias = Column(Float)
    man_dc = Column(Float)
    use_pid = Column(Boolean)
    target = Column(Float)
    kp = Column(Float)
    ki = Column(Float)
    kd = Column(Float)


class StatData(Base):
    __tablename__ = 'stat_data'

    id = Column(Integer, primary_key=True)
    intemp_tot = Column(Float)
    intemp_min = Column(Float)
    intemp_max = Column(Float)
    intemp_avg = Column(Float)
    inhum_tot = Column(Float)
    inhum_min = Column(Float)
    inhum_max = Column(Float)
    inhum_avg = Column(Float)
    extemp1_tot = Column(Float)
    extemp1_min = Column(Float)
    extemp1_max = Column(Float)
    extemp1_avg = Column(Float)
    exhum_tot = Column(Float)
    exhum_min = Column(Float)
    exhum_max = Column(Float)
    exhum_avg = Column(Float)
    extemp2_tot = Column(Float)
    extemp2_min = Column(Float)
    extemp2_max = Column(Float)
    extemp2_avg = Column(Float)
    wtemp_tot = Column(Float)
    wtemp_min = Column(Float)
    wtemp_max = Column(Float)
    wtemp_avg = Column(Float)
    watts_tot = Column(Float)
    watts_min = Column(Float)
    watts_max = Column(Float)
    watts_avg = Column(Float)
    samples = Column(Integer)

    def __init__(self, statdata):
        # intake temperature
        self.intemp_tot = statdata[0]
        self.intemp_min = statdata[1]
        self.intemp_max = statdata[2]
        self.intemp_avg = statdata[3]

        # intake relative humidity
        self.inhum_tot = statdata[4]
        self.inhum_min = statdata[5]
        self.inhum_max = statdata[6]
        self.inhum_avg = statdata[7]

        # exhaust temperature 1
        self.extemp1_tot = statdata[8]
        self.extemp1_min = statdata[9]
        self.extemp1_max = statdata[10]
        self.extemp1_avg = statdata[11]

        # exhaust relative humidity
        self.exhum_tot = statdata[12]
        self.exhum_min = statdata[13]
        self.exhum_max = statdata[14]
        self.exhum_avg = statdata[15]

        # exhaust temperature 2
        self.extemp2_tot = statdata[16]
        self.extemp2_min = statdata[17]
        self.extemp2_max = statdata[18]
        self.extemp2_avg = statdata[19]

        # water temperature
        self.wtemp_tot = statdata[20]
        self.wtemp_min = statdata[21]
        self.wtemp_max = statdata[22]
        self.wtemp_avg = statdata[23]

        # watts
        self.watts_tot = statdata[24]
        self.watts_min = statdata[25]
        self.watts_max = statdata[26]
        self.watts_avg = statdata[27]

        # total number of samples
        self.samples = statdata[28]
