import pigpio

import hwpwm

pi = pigpio.pi()

inzone = hwpwm.PWM(pi, 12, dcmin=(20 / 0.749795))
exzone = hwpwm.PWM(pi, 19)
inzone.setdc(50)
exzone.setdc(50 * 0.749795)
