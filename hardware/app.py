
from heapq import heappush, heappop

import asyncio

class ZError(RuntimeError): pass

_2D_BIT_SHIFT = 8
def _get_id(row,col):
    return row << _2D_BIT_SHIFT | col
def _get_row(id):
    return id >> _2D_BIT_SHIFT
def _get_col(id):
    return id & (2 ** _2D_BIT_SHIFT - 1)

class HardwareApp:
    """Handles priority-based contextual I/O for multiple devices.

    inputs maps objects to [mappings of pin ids to (heaps of handlers)]
    outputs maps object to [mappings of pixel indices to (heaps of vals)]
    last_outputs maps objects to [mappings of pixel indices to vals]
    both priorities map objects to [mappings of ids to (sets of priorities)]

    outputs must have an `insert(row, col, val)` method, and may use `flush`
    """
    def __init__(self):
        self.__inputs = {}
        self.__outputs = {}
        self.__last_outputs = {}
        self.__ipriorities = {}
        self.__opriorities = {}
        self.__hw = []
        self.__hw_initialized = False
        self.loop = asyncio.get_event_loop()
        self.loop.call_soon(self.update)

    def add_hw(self, obj):
        """Adds an object to the init/cleanup cycle tracker, and initializes it
        immediately if the loop is already running."""
        self.__hw.append(obj)
        if self.__hw_initialized:
            obj.init()
        return obj

    def quit(self):
        self.loop.stop()

    def update(self):
        self.loop.call_later(0.08, self.update)
        for i in self.__inputs:
            i.tick()
        for o in self.__outputs:
            for l in self.__outputs[o]:
                val = self.__outputs[o][l][0]
                if self.__last_outputs[o][l] != val:
                    self.__last_outputs[o][l] = val
                    o.insert(_get_row(l), _get_col(l), val)
            if hasattr(o, "flush"):
                o.flush()

    def mainloop(self):
        for i in self.__hw:
            i.init()
        self.__hw_initialized = True
        self.loop.run_forever()
        self.__hw_initialized = False
        for i in self.__hw:
            i.cleanup()

class Context:
    priority = 2 ** 16
    
    def __init__(self, app):
        self.app = app

    def enter(self):
        """Capture inputs and outputs pixels, if necessary."""
        pass

    def leave(self):
        """Release all aquired inputs"""
        pass
