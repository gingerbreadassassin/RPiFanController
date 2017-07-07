from fansqla import SensorData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine('sqlite:////var/www/fancontrol/fancontrol.db')
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

datum = []
history = datetime.datetime.today() - datetime.timedelta(seconds=20)
for row in session.query(SensorData).filter(SensorData.date_time > history):
    datum.append(row.wtemp)

print(datum)
