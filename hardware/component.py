#
# Base classes for GPIO hardware
#

import RPi.GPIO as gpio
import time

from collections import defaultdict

def delay(microseconds):
    time.sleep(microseconds/1000000)

def waitms(milliseconds):
    time.sleep(milliseconds/1000)

class Component:
    def __init__(self):
        super().__init__()
        self.__initialized = False

    def _checkInit(self,quiet=False):
        if quiet:
            return self.__initialized
        if not self.__initialized:
            raise RuntimeError("This {} has not been initialized yet!".format(
                    self.__class__.__name__))

    def _set_init(self):
        self.__initialized = True

    def init(self):
        if self.__initialized:
            try:
                self.cleanup()
            finally:
                pass

    def cleanup(self):
        self.__initialized = False

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, tb):
        self.cleanup()

class GPIOComponent(Component):
    def __init__(self,outpins=(),inpins=()):
        super().__init__()
        self.__out_pins = outpins
        self.__in_pins = inpins

    def init(self,wait_set_init=False):
        super().init()
            
        gpio.setmode(gpio.BOARD)

        for ch in self.__out_pins:
            gpio.setup(ch, gpio.OUT, initial=gpio.LOW)
        for ch in self.__in_pins:
            gpio.setup(ch, gpio.IN, initial=gpio.LOW)

        if not wait_set_init:
            self._set_init()

    def cleanup(self):
        if not self._checkInit(True):
            return False
        super().cleanup()
        for ch in self.__out_pins + self.__in_pins:
            gpio.cleanup(ch)
        return True

class I2CComponent(Component):
    def __init__(self,addr):
        self._address = addr
        super().__init__()

class EventedInput:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__next_id = -1
        self.__handlers = defaultdict(dict)

    def _get_handlers(self,pin=None,generic=False):
        if (pin is None) and (not generic):
            raise TypeError("Must supply pin for non generic handler!")
        return self.__handlers["generic"] if generic else self.__handlers[pin]

    def add_handler(self,callback,pin=None,generic=False):
        self.__next_id += 1
        self._get_handlers(pin,generic)[self.__next_id] = callback
        return self.__next_id

    def remove_handler(self,hid,pin=None,generic=False):
        del self._get_handlers(pin,generic)[hid]

    def _handle_pin(self,pin):
        for i in self._get_handlers(generic=True).values():
            i(pin)
        for i in self._get_handlers(pin).values():
            i(pin)
