#!/usr/bin/env python3

from adafruit.trellis import Adafruit_Trellis

try:
    from .component import *
except SystemError:
    from component import *

class LEDKeypad(EventedInput, LoopedInput, I2CComponent):
    _mswait = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def init(self, *args, **kwargs):
        self.trellis = Adafruit_Trellis()
        self.trellis.begin(self._address)
        super().init(*args, **kwargs)

    def cleanup(self):
        self.trellis.clear()
        self.trellis.writeDisplay()
        super().cleanup()
        del self.trellis

    def tick(self):
        self._checkInit()
        if self.trellis.readSwitches(self):
            for i in range(16):
                if self.trellis.justPressed(i):
                    self._handle_pin(i)

    def __led(self, val, index):
        getattr(self.trellis,"setLED" if val else "clrLED")(index)

    def insert(self, row, col, val):
        self.__led(val, row*4 + col)

    def flush(self):
        self.trellis.writeDisplay()
        
    def set_leds(self, leds={}):
        self._checkInit()
        for i, val in leds.items():
            self.__led(val, i)
        self.flush()
