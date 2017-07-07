from fansqla import SensorData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine('sqlite:////var/www/fancontrol/fancontrol.db')
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

too_old = datetime.datetime.today() - datetime.timedelta(hours=12)
for row in session.query(SensorData).filter(SensorData.date_time < too_old):
    session.delete(row)

session.commit()
session.close()
