#!/usr/bin/env python3
#
# PINS:
# A D3: CE1
# B D2: CE0
# C D1: RXD
# D D0: TXD
#

import RPi.GPIO as gpio
from time import sleep

try:
    from .component import GPIOComponent, EventedInput
except SystemError:
    from component import GPIOComponent, EventedInput

A = 8  # TXD
B = 10 # RXD
C = 24 # CE0
D = 26 # CE1

class RFReceiver(GPIOComponent, EventedInput):
    def __init__(self,a=A,b=B,c=C,d=D):
        self.pins = (a, b, c, d)
        super().__init__(inpins=self.pins)

    def init(self):
        super().init()
        for n, i in enumerate(self.pins):
            gpio.add_event_detect(i, gpio.RISING, bouncetime=500,
                                  callback=lambda x,n=n: self._handle_pin(n))

    def cleanup(self):
        for i in self.pins:
            gpio.remove_event_detect(i)
        super().cleanup()

if __name__ == "__main__":
    def echo(pin):
        print("Press on button:", pin)
    rf = RFReceiver()
    rf.add_handler(echo,generic=True)
    with rf:
        while True:
            sleep(1)
    
