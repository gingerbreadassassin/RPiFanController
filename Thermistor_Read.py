# Adopted to pigpio from Ken Powers' work

import math
import time

import pigpio

import pot_cap


class Thermistor:

    def __init__(self, pi, gpio, nf, samples=100, power=None):
        self.samples = samples
        self.nf = nf
        self.pc = pot_cap.reader(pi, gpio, 1.0, 0.1)
        self.ppin = power
        if self.ppin is not None:
            pi.write(self.ppin, 1)
            time.sleep(2)
        self.good = False

    def _resistance_calc(self, us):  # microsecond, nanoFarads
        t = us*1e-6
        c = self.nf*1e-9
        v = 1 - ((22.0/15.0)/3.3)  # gpio high trigger voltage / supply voltage
        lnv = math.log1p(v-1)  # log1p is natural log (1+x)
        return -t / (c * lnv)

    def _resistance_reading(self):
        total = 0
        for i in range(0, self.samples):
            # Record time interval in microseconds and sum
            self.good = False
            t = 0
            x = 0
            while not self.good and x < 10:
                self.good, t, r = self.pc.read()
                x += 1

            total += t
        # Average time readings

        if not self.good:
            return 2
        reading = total / self.samples
        # Convert average time reading to resistance
        return self._resistance_calc(reading)  # pass average time

    def kelvin(self):
        r = self._resistance_reading()
        lr = math.log1p(r - 1)
        # Steinhart-Hart equation using coefficients from bitspower thermistor probe
        tk = 1 / (0.000428670876749269 + 0.000322025554873117 * lr + -4.959174377042198e-8 * lr * lr * lr)
        if self.good:
            return tk
        return -99

    def celsius(self):
        c = self.kelvin() - 273.15
        if c is -99 - 273.15:
            return -99
        return c

    def fahrenheit(self):
        f = self.celsius() * 9.0 / 5.0 + 32.0
        if f == -99 * 9.0 / 5.0 + 32:
            return -99
        return f

    def cancel(self):
        self.pc.cancel()

if __name__ == "__main__":
    pi = pigpio.pi()
    th = Thermistor(pi, 25, 350, 10, 8)
    print("Kelvin = {} | Celsius = {} | Fahrenheit = {}".format(th.kelvin(), th.celsius(), th.fahrenheit()))
    pi.stop()
