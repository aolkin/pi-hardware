#!/usr/bin/env python3

from adafruit.trellis import Adafruit_Trellis

try:
    from .component import *
except SystemError:
    from component import *

from threading import Thread

class LEDKeypad(I2CComponent, EventedInput, LoopedInput):
    _waitms = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def init(self, *args, **kwargs):
        self.trellis = Adafruit_Trellis()
        self.begin(self._address)
        super().init(*args, **kwargs)

    def cleanup(self):
        super().cleanup()
        del self.trellis

    def tick(self):
        if self.trellis.readSwitches(self):
            for i in range(16):
                if self.trellis.justPressed(i):
                    self._handle_pin(i)

    def set_leds(self, leds={}):
        for i, val in leds.items():
            self.trellis.setLED(i) if val else self.trellis.clrLED(i)
        self.trellis.writeDisplay()
