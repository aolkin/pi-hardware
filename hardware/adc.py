#!/usr/bin/env python3

from adafruit.ads1x15 import ADS1x15

try:
    from .component import *
except SystemError:
    from component import *

IC = 0 # ADS1015 (12-bit ADC)
GAIN = 0x1000 # (+/- 4.096V for Rasberry Pi 3V3 supply)
SINGLE_SPS = SPS = 2400
WAITMS = 100

MILLIVOLTS = 1000

class ADC4(I2CComponent, EventedInput, LoopedInput):
    _mswait = 50

    def __init__(self, *args, **kwargs):
        self.values = [None, None, None, None]

    def init(self, autostart=False):
        super().init()
        self.adc = ADS1x15(ic=IC, address=self._address)

    def cleanup(self):
        super().cleanup()
        del self.adc

    def get(self, pin):
        return self.values[pin]

    def read(self, pin):
        self._checkInit()
        return self.process_reading(
            self.adc.readADCSingleEnded(pin, GAIN, SINGLE_SPS))

    def process_reading(self, reading):
        return reading / MILLIVOLTS

    def tick(self):
        for i in range(4):
            v = self.read(i)
            if self.values[i] != v:
                self.values[i] = v
                self._handle_pin(i)

class ScaledADC4(ADC4):
    # 34 - 3272
    def __init__(self, addr, low=0, high=GAIN, precision=0, scale=100,
                 **kwargs):
        super().__init__(addr, **kwargs)
        self._low = low
        self._high = high
        self._precision = precision
        self._scale = scale

    def process_reading(self, reading):
        r = (reading - self._low) / (self._high - self._low)
        return round(r * self._scale, self._precision)

class ADCSet(EventedInput):
    def __init__(self, startaddr, n=2, scaled=False, *args, **kwargs):
        super().__init__()
        self.adcs = []
        self.__class = ScaledADC4 if scaled else ADC4
        for i in range(startaddr, startaddr+n):
            self.adcs.append(self.__class(i, *args, **kwargs))
            adc = len(self.adcs) - 1
            self.adcs[adc].add_handler((lambda x, s=self, a=adc: s.cb(x, a)), generic=True)
    
    def init(self, *args, **kwargs):
        for i in self.adcs:
            i.init(*args, **kwargs)

    def cleanup(self):
        for i in self.adcs:
            i.cleanup()

    def start(self):
        for i in self.adcs:
            i.start()

    def stop(self):
        for i in self.adcs:
            i.stop()
    
    def get(self, i):
        self.adcs[i // 4].get(i % 4)

    def cb(self, i, a):
        self.handle_pin(a*4 + i)
