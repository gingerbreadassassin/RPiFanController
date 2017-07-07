import time
from math import fabs
import DHT22
from Thermistor_Read import Thermistor
import pigpio
import hwpwm
from pid import PIDController
from fan import Fan
import logging
from fansqla import SensorData, Settings, StatData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

    target_temp = bias = ki = kp = kd = 0

    # connect to sqlite db:
    engine = create_engine('sqlite:////var/www/fancontrol/fancontrol.db')
    session = sessionmaker()
    session.configure(bind=engine)
    session = session()

    # fans:
    in141 = Fan(pi, 1, 7)
    in142 = Fan(pi, 21, 20)
    ex141 = Fan(pi, 6, 5)
    ex142 = Fan(pi, 0, 11)
    ex120 = Fan(pi, 22)
    pump = Fan(pi, 3, 4)

    # update user settings
    for setting in session.query(Settings):
        bias = setting.bias
        man_dc = setting.man_dc
        use_pid = setting.use_pid
        target_temp = setting.target
        kp = setting.kp
        ki = setting.ki
        kd = setting.kd

    # create two PWM instances for intake and exhaust:
    inzone = hwpwm.PWM(pi, 12, dcmin=(20 / bias))
    exzone = hwpwm.PWM(pi, 19)
    inzone.setdc(50)
    exzone.setdc(50 * bias)

    # temp sensors:
    intrh = DHT22.sensor(pi, 14)
    outtrh = DHT22.sensor(pi, 15)
    time.sleep(0.1)
    th = Thermistor(pi, 25, 342, 100, 8)
    time.sleep(0.1)

    # set up the PID controller
    pid = PIDController(round(th.celsius()), target_temp, kp, ki, kd)

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

        return it, ih, ot1, orh, ot2, wt, ir1, ir2, or1, or2, or3, p, w

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
        for setting in session.query(Settings):
            bias = setting.bias
            man_dc = setting.man_dc
            use_pid = setting.use_pid
            target_temp = setting.target
            kp = setting.kp
            ki = setting.ki
            kd = setting.kd

        # collect readings from sensors:
        datum = collect()
        lastrun = time.time()

        # set up the next row of sensor data:
        sensordata = SensorData(datum)
        sensordata.indc = (inzone.dc / 10000)
        sensordata.exdc = (exzone.dc / 10000)
        sensordata.target = target_temp

        # add the next row of sensor reading data:
        session.add(sensordata)

        # update the statistical data:
        for stat in session.query(StatData):
            stat.samples = stat.samples + 1
            stat.intemp_tot = sensordata.intemp + stat.intemp_tot
            stat.intemp_avg = stat.intemp_tot / stat.samples
            stat.inhum_tot = sensordata.inhum + stat.inhum_tot
            stat.inhum_avg = stat.inhum_tot / stat.samples
            stat.extemp1_tot = sensordata.extemp1 + stat.extemp1_tot
            stat.extemp1_avg = stat.extemp1_tot / stat.samples
            stat.exhum_tot = sensordata.exhum + stat.exhum_tot
            stat.exhum_avg = stat.exhum_tot / stat.samples
            stat.extemp2_tot = sensordata.extemp2 + stat.extemp2_tot
            stat.extemp2_avg = stat.extemp2_tot / stat.samples
            stat.wtemp_tot = sensordata.wtemp + stat.wtemp_tot
            stat.wtemp_avg = stat.wtemp_tot / stat.samples
            stat.watts_tot = sensordata.watts + stat.watts_tot
            stat.watts_avg = stat.watts_tot / stat.samples
            # intemp
            if stat.intemp_min > sensordata.intemp:
                stat.intemp_min = sensordata.intemp
            if stat.intemp_max < sensordata.intemp:
                stat.intemp_max = sensordata.intemp

            # inhum
            if stat.inhum_min > sensordata.inhum:
                stat.inhum_min = sensordata.inhum
            if stat.inhum_max < sensordata.inhum:
                stat.inhum_max = sensordata.inhum

            # extemp1
            if stat.extemp1_min > sensordata.extemp1:
                stat.extemp1_min = sensordata.extemp1
            if stat.extemp1_max < sensordata.extemp1:
                stat.extemp1_max = sensordata.extemp1

            # exhum
            if stat.exhum_min > sensordata.exhum:
                stat.exhum_min = sensordata.exhum
            if stat.exhum_max < sensordata.exhum:
                stat.exhum_max = sensordata.exhum

            # extemp2
            if stat.extemp2_min > sensordata.extemp2:
                stat.extemp2_min = sensordata.extemp2
            if stat.extemp2_max < sensordata.extemp2:
                stat.extemp2_max = sensordata.extemp2

            # wtemp
            if stat.wtemp_min > sensordata.wtemp:
                stat.wtemp_min = sensordata.wtemp
            if stat.wtemp_max < sensordata.wtemp:
                stat.wtemp_max = sensordata.wtemp

            # watts
            if stat.watts_min > sensordata.watts:
                stat.watts_min = sensordata.watts
            if stat.watts_max < sensordata.watts:
                stat.watts_max = sensordata.watts

            session.commit()

            if use_pid:
                dc = pid.getoutput(datum[5])
            else:
                dc = man_dc

            inzone.setdc(dc)
            exzone.setdc(dc * bias)

        # update PID controller:
        pid.target = target_temp
        pid.kp = kp
        pid.ki = ki
        pid.kd = kd

        # get the new duty cycle:
        if use_pid:
            dc = pid.getoutput(datum[5])
        else:
            dc = man_dc

        # set the zone fan speeds:
        inzone.setdc(dc)
        exzone.setdc(dc * bias)

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
