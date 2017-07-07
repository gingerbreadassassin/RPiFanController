import time

import pigpio

import read_RPM


class Fan:
    def __init__(self, pi, gpio, power=None, dr=60, max_rpm=2000, min_rpm=1):
        self.max_rpm = max_rpm + 50
        self.min_rpm = min_rpm
        self.pi = pi
        self.gpio = gpio
        self.power = power
        self.dr = dr

        if power is not None:
            pi.write(power, 1)
            time.sleep(2)

        self.sensor = read_RPM.reader(self.pi, self.gpio, 2.0)

    def getrpm(self):
        time.sleep(0.1)
        r = self.sensor.RPM()
        if r < self.min_rpm:
            return -99
        return round(r)

    def cancel(self):
        self.sensor.cancel()
        if self.power is not None:
            self.pi.write(self.power, 0)

if __name__ == "__main__":
    p = pigpio.pi()
    time.sleep(2)
    inf = Fan(p, 6)
    time.sleep(2)
    for i in range(0, 10):
        print(inf.getrpm())
    time.sleep(2)
    p.stop()
