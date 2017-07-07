import pigpio
import time


class PWM:

    def __init__(self, pi, gpio, freq=25000, dc=0, dcmin=20, dcstart=30, offbelowmin=False):
        self.pi = pi
        self.gpio = int(gpio)
        self.freq = int(freq)
        self.dcmin = int(dcmin*10000)
        self.dcstart = int(dcstart*10000)
        self.dc = int(dc*10000)
        self.offbelowmin = offbelowmin
        self.setdc(self.dc)

    def setdc(self, dc):
        dc *= 10000
        dc = int(dc)
        if dc < self.dcmin:
            if self.offbelowmin:
                self.dc = 0
            else:
                self.dc = self.dcmin
        elif self.dc == 0:
            if dc < self.dcstart:
                self._startup()
                self.dc = dc
        else:
            self.dc = dc
        self._dc()

    def _startup(self):
        self.pi.hardware_PWM(self.gpio, self.freq, self.dcmin)
        time.sleep(2)

    def _dc(self):
        self.pi.hardware_PWM(self.gpio, self.freq, self.dc)
