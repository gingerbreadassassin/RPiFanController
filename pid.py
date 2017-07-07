import time


class PIDController:

    def __init__(self, inval, target, kp, ki, kd):
        self.lasttick = time.time()
        self.delta = 1
        self.target = target
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # initialize variables used in PID controller
        self.err1 = inval - self.target
        self.integral = 0.0
        self.diffntl = 0.0
        self.output = 0.0

    def getoutput(self, inval):
        thistick = time.time()
        self.delta = thistick - self.lasttick
        self.lasttick = thistick
        err2 = inval - self.target
        self.integral += self.err1 * self.delta
        if self.integral < 0.0:
            self.integral = 0.0
        elif self.integral > 100.0:
            self.integral = 100.0
        self.diffntl = (err2 - self.err1)/self.delta

        # calculate output:
        e = self.err1 * self.kp
        i = self.integral * self.ki
        d = self.diffntl * self.kd
        self.output = e + i + d

        # bound between 0 and 100:
        if self.output > 100.0:
            self.output = 100.0
        elif self.output < 0.0:
            self.output = 0.0

        self.err1 = err2
        return self.output
