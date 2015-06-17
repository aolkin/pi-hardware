#!/usr/bin/env python3

from adafruit.ads1x15 import ADS1x15

from collections import defaultdict

try:
    from .component import *
except SystemError:
    from component import *

from threading import Thread

IC = 0 # ADS1015 (12-bit ADC)
GAIN = 0x1000 # (+/- 4.096V for Rasberry Pi 3V3 supply)
SPS = 2400
WAITMS = 100

MILLIVOLTS = 1000

class ADC4(I2CComponent, EventedInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread = Thread(target=self.runloop)
        self.thread.daemon = True
        self.thread.start()
        self.values = [None, None, None, None]
        self.__started = False

    def init(self, autostart=False):
        super().init()
        self.adc = ADS1x15(ic=IC, address=self._addr)
        if autostart:
            self.start()

    def cleanup(self):
        if self.__started:
            self.stop()
        del self.adc
        super().cleanup()

    def start(self):
        self.__started = True

    def stop(self):
        self.__started = False

    def get(self, pin):
        return self.values[pin]

    def read(self, pin):
        return self.process_reading(self.adc.readADCSingleEnded(pin, GAIN, SINGLE_SPS))
    def process_reading(self, reading):
        return reading / MILLIVOLTS

    def runloop(self):
        while True:
            if __started:
                for i in range(4):
                    v = self.read(i)
                    if self.values[i] != v:
                        self.values[i] = v
                        self._handle_pin(i)
            waitms(50)

def ScaledADC4(ADC4):
    def __init__(self, low=0, high=GAIN, precision=0, scale=100,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._low = low
        self._high = high - low
        self._precision = precision
        self._scale = scale

    def process_reading(self, reading):
        r = (reading - self._low) / self._high
        return round(r * self._scale, self._precision)
