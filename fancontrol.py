import time
from math import fabs
import DHT22
from Thermistor_Read import Thermistor
import pigpio
import hwpwm
from pid import PIDController
from fan import Fan
import logging
from datetime import datetime
from pymongo import MongoClient

# make debugging easier
logging.basicConfig(level=logging.DEBUG, filename='/var/log/fancontrol.log')


# wrap whole thing up in a single method to catch any exceptions:
def main():
    # instantiate the pigpio connection:
    pi = pigpio.pi()

    # if running at boot, sometimes pigpiod needs time to startup
    # in that case, wait and rety the connection
    while not pi.connected:
        time.sleep(5)
        pi = pigpio.pi()

    # connect to mongodb:
    client = MongoClient()
    db = client.fancontrol
    settings = db.settings.find_one()
    sensordata = db.sensordata

    # fans:
    in141 = Fan(pi, 1, 7)
    in142 = Fan(pi, 21, 20)
    ex141 = Fan(pi, 6, 5)
    ex142 = Fan(pi, 0, 11)
    ex120 = Fan(pi, 22)
    pump = Fan(pi, 3, 4)

    # create two PWM instances for intake and exhaust:
    inzone = hwpwm.PWM(pi, 12, dcmin=(20 / settings['bias']))
    exzone = hwpwm.PWM(pi, 19)
    inzone.setdc(50)
    exzone.setdc(50 * settings['bias'])

    # temp sensors:
    intrh = DHT22.sensor(pi, 14)
    outtrh = DHT22.sensor(pi, 15)
    time.sleep(0.1)
    th = Thermistor(pi, 25, 342, 100, 8)
    time.sleep(0.1)

    # set up the PID controller
    pid = PIDController(round(th.celsius()), settings['target'], settings['kp'], settings['ki'], settings['kd'])

    # record when last time data collection occurred to find delta t
    # for use in calculation of heat dissipation in watts
    lastrun = time.time()

    # method to read dallas 1-wire temp sensor:
    def ds18b20():
        pigpio.exceptions = False
        c, files = pi.file_list("/sys/bus/w1/devices/28*/w1_slave")
        pigpio.exceptions = True

        if c >= 0:

            for sensor in files[:-1].split(b"\n"):

                """
                Typical file name

                /sys/bus/w1/devices/28-000005d34cd2/w1_slave
                """

                # devid = sensor.split(b"/")[5]  # Fifth field is the device Id.

                h = pi.file_open(sensor, pigpio.FILE_READ)
                c, data = pi.file_read(h, 1000)  # 1000 is plenty to read full file.
                pi.file_close(h)

                """
                Typical file contents

                73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
                73 01 4b 46 7f ff 0d 10 41 t=23187
                """

                if b"YES" in data:
                    (discard, sep, reading) = data.partition(b' t=')
                    t = float(reading) / 1000.0
                    return t
                else:
                    return -999.0

    # method to gather data from all sensors (returns a list):
    def collect():
        intrh.trigger()
        outtrh.trigger()
        it = round(intrh.temperature(), 1)
        if it < 0:
            it = 0
        ih = round(intrh.rhum, 1)
        if ih < 0:
            ih = 0
        ot1 = round(outtrh.temperature(), 1)
        if ot1 < 0:
            ot1 = 0
        orh = round(outtrh.rhum, 1)
        if orh < 0:
            orh = 0
        ot2 = round(ds18b20(), 1)
        if ot2 < 0:
            ot2 = 0
        wt = round(th.celsius(), 1)
        while wt < 0:
            wt = round(th.celsius(), 1)
        ir1 = in141.getrpm()
        if ir1 < 0:
            ir1 = 0
        ir2 = in142.getrpm()
        if ir2 < 0:
            ir2 = 0
        or1 = ex141.getrpm()
        if or1 < 0:
            or1 = 0
        or2 = ex142.getrpm()
        if or2 < 0:
            or2 = 0
        or3 = ex120.getrpm()
        if or3 < 0:
            or3 = 0
        p = pump.getrpm()
        if p < 0:
            p = 0
        q = round((1.005 * (fabs(((ot1 + ot2) / 2) - it))), 3)
        s = (time.time() - lastrun)
        w = round(q / s)
        if w < 0:
            w = 0

        return {'date_time': datetime.utcnow(),
                'exdc': (exzone.dc / 10000),
                'exhum': orh,
                'exrpm1': or1,
                'exrpm2': or2,
                'exrpm3': or3,
                'extemp1': ot1,
                'extemp2': ot2,
                'indc': (inzone.dc / 10000),
                'inhum': ih,
                'inrpm1': ir1,
                'inrpm2': ir2,
                'intemp': it,
                'prpm': p,
                'target': settings['target'],
                'watts': w,
                'wtemp': wt}

    # trigger the AM2301 sensors, as first reading is always -999:
    intrh.trigger()
    outtrh.trigger()

    # AM2301 sensors cannot be queried more than once every 3 seconds
    # wait 3 seconds to ensure they remain in a good state:
    time.sleep(3)

    # do this until forever
    while True:
        # make sure this loop takes at least 3 seconds:
        start = time.time()

        # update the settings to reflect user changes:
        settings = db.settings.find_one()

        # collect readings from sensors:
        datum = collect()
        sensordata.insert_one(datum)

        lastrun = time.time()

        stats = db.statdata.find_one()
        stats['samples'] = stats['samples'] + 1
        stats['intemp_tot'] = datum['intemp'] + stats['intemp_tot']
        stats['intemp_avg'] = stats['intemp_tot'] / stats['samples']
        stats['inhum_tot'] = datum['inhum'] + stats['inhum_tot']
        stats['inhum_avg'] = stats['inhum_tot'] / stats['samples']
        stats['extemp1_tot'] = datum['extemp1'] + stats['extemp1_tot']
        stats['extemp1_avg'] = stats['extemp1_tot'] / stats['samples']
        stats['exhum_tot'] = datum['exhum'] + stats['exhum_tot']
        stats['exhum_avg'] = stats['exhum_tot'] / stats['samples']
        stats['extemp2_tot'] = datum['extemp2'] + stats['extemp2_tot']
        stats['extemp2_avg'] = stats['extemp2_tot'] / stats['samples']
        stats['wtemp_tot'] = datum['wtemp'] + stats['wtemp_tot']
        stats['wtemp_avg'] = stats['wtemp_tot'] / stats['samples']
        stats['watts_tot'] = datum['watts'] + stats['watts_tot']
        stats['watts_avg'] = stats['watts_tot'] / stats['samples']
        # intemp
        if stats['intemp_min'] > datum['intemp']:
            stats['intemp_min'] = datum['intemp']
        if stats['intemp_max'] < datum['intemp']:
            stats['intemp_max'] = datum['intemp']

        # inhum
        if stats['inhum_min'] > datum['inhum']:
            stats['inhum_min'] = datum['inhum']
        if stats['inhum_max'] < datum['inhum']:
            stats['inhum_max'] = datum['inhum']

        # extemp1
        if stats['extemp1_min'] > datum['extemp1']:
            stats['extemp1_min'] = datum['extemp1']
        if stats['extemp1_max'] < datum['extemp1']:
            stats['extemp1_max'] = datum['extemp1']

        # exhum
        if stats['exhum_min'] > datum['exhum']:
            stats['exhum_min'] = datum['exhum']
        if stats['exhum_max'] < datum['exhum']:
            stats['exhum_max'] = datum['exhum']

        # extemp2
        if stats['extemp2_min'] > datum['extemp2']:
            stats['extemp2_min'] = datum['extemp2']
        if stats['extemp2_max'] < datum['extemp2']:
            stats['extemp2_max'] = datum['extemp2']

        # wtemp
        if stats['wtemp_min'] > datum['wtemp']:
            stats['wtemp_min'] = datum['wtemp']
        if stats['wtemp_max'] < datum['wtemp']:
            stats['wtemp_max'] = datum['wtemp']

        # watts
        if stats['watts_min'] > datum['watts']:
            stats['watts_min'] = datum['watts']
        if stats['watts_max'] < datum['watts']:
            stats['watts_max'] = datum['watts']

        db.statdata.replace_one({'_id': stats['_id']}, stats)

        # update PID controller:
        pid.target = settings['target']
        pid.kp = settings['kp']
        pid.ki = settings['ki']
        pid.kd = settings['kd']

        # get the new duty cycle:
        if settings['use_pid']:
            dc = pid.getoutput(datum['wtemp'])
        else:
            dc = settings['mandc']

        # set the zone fan speeds:
        inzone.setdc(dc)
        exzone.setdc(dc * settings['bias'])

        # make sure this whole process takes at least 3 seconds:
        stop = time.time()
        if stop - start < 3.0:
            time.sleep(3.0 - (stop - start))

# noinspection PyBroadException
# run the program:
try:
    main()

# catch any errors:
except:
    logging.exception('main failed at: {}'.format(time.ctime()))
    exit()
