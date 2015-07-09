
from heapq import heappush, heappop

from collections import defaultdict

import asyncio

class ZError(RuntimeError): pass

_2D_BIT_SHIFT = 8
def _get_id(row,col):
    return row << _2D_BIT_SHIFT | col
def _get_row(id):
    return id >> _2D_BIT_SHIFT
def _get_col(id):
    return id & (2 ** _2D_BIT_SHIFT - 1)

list_dict = lambda: defaultdict(list)
dict_dict = lambda: defaultdict(dict)

def ensure_iter(val):
    if hasattr(val,"__iter__"):
        return val
    else:
        return (val,)

class HardwareApp:
    """Handles priority-based contextual I/O for multiple devices.

    inputs maps objects to [mappings of pin ids to (maps of handlers)]
    outputs maps object to [mappings of pixel indices to (maps of vals)]
    last_outputs maps objects to [mappings of pixel indices to vals]
    both priorities map objects to [mappings of ids to (heaps of priorities)]

    outputs must have an `insert(row, col, val)` method, and may use `flush`
    """
    def __init__(self):
        self.__inputs = defaultdict(dict_dict)
        self.__outputs = defaultdict(dict_dict)
        self.__last_outputs = defaultdict(dict)
        self.__ipriorities = defaultdict(list_dict)
        self.__opriorities = defaultdict(list_dict)
        self.__input_handlers = {}
        self.__hw = set()
        self.__hw_initialized = False
        self.loop = asyncio.get_event_loop()
        self.loop.call_soon(self.update)

    def add_hw(self, obj1, *objs):
        """Adds an object to the init/cleanup cycle tracker, and initializes it
        immediately if the loop is already running."""
        objs = [obj1] + list(objs)
        for obj in objs:
            self.__hw.add(obj)
            if self.__hw_initialized:
                obj.init()
        if len(objs) < 2:
            return obj1
        else:
            return objs

    def capture(self, priority, hw, pins, cb):
        if not (hw in self.__hw):
            self.add_hw(hw)
        pins = ensure_iter(pins)
        if not self.__inputs[hw]:
            self.__input_handlers[hw] = hw.add_handler(
                lambda pin, hw=hw: self._do_cb(hw,pin), generic=True)
        for i in pins:
            self.__inputs[hw][i][priority] = cb
            try:
                self.__ipriorities[hw][i].remove(priority)
            except ValueError:
                pass
            heappush(self.__ipriorities[hw][i], priority)

    def output(self, priority, hw, row, startcol, val):
        if not (hw in self.__hw):
            self.add_hw(hw)
        val = ensure_iter(val)
        for i, s in enumerate(val):
            pid = _get_id(row, startcol + i)
            self.__outputs[hw][pid][priority] = s
            try:
                self.__opriorities[hw][pid].remove(priority)
            except ValueError:
                pass
            heappush(self.__opriorities[hw][pid], priority)

    def release(self, priority, hw, pins):
        pins = ensure_iter(pins)
        for i in pins:
            try:
                self.__ipriorities[hw][i].remove(priority)
                del self.__inputs[hw][i][priority]
            except (ValueError, KeyError):
                pass

    def outtake(self, priority, hw, row, colrange):
        for i in ensure_iter(colrange):
            try:
                pid = _get_id(row, i)
                self.__opriorities[hw][pid].remove(priority)
                del self.__outputs[hw][pid][priority]
            except (ValueError, KeyError):
                pass
            
    def quit(self):
        self.loop.stop()

    def _do_cb(self, hw, pin):
        if self.__ipriorities[hw][pin]:
            self.__inputs[hw][pin][self.__ipriorities[hw][pin][0]](pin)
        
    def update(self):
        self.loop.call_later(0.05, self.update)
        for i in self.__inputs:
            i.tick()
        for o in self.__outputs:
            for l in self.__outputs[o]:
                if self.__opriorities[o][l]:
                    p = self.__opriorities[o][l][0]
                    val = self.__outputs[o][l][p]
                    if self.__last_outputs[o].get(l, None) != val:
                        self.__last_outputs[o][l] = val
                        o.insert(_get_row(l), _get_col(l), val)
            if hasattr(o, "flush"):
                o.flush()

    def mainloop(self):
        for i in self.__hw:
            i.init()
        self.__hw_initialized = True
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        self.__hw_initialized = False
        for i in self.__hw:
            i.cleanup()

class Context:

    priority = 2 ** 16
    
    def __init__(self, app):
        self.app = app
        self.__inputs = defaultdict(set)
        self.__outputs = defaultdict(lambda: defaultdict(set))

    def enter(self):
        """Capture inputs"""
        pass

    def leave(self):
        """Release all aquired inputs and outputs"""
        for i, j in self.__inputs.items():
            self.release(i, j)
        for i, j in self.__outputs.items():
            for r, c in j.items():
                self.outtake(i, r, c)

    def capture(self, hw, pins, cb):
        for i in ensure_iter(pins):
            self.__inputs[hw].add(i)
        self.app.capture(self.priority, hw, pins, cb)
        
    def output(self, hw, row, startcol, val):
        self.__outputs[hw][row].add(range(startcol,
                                          startcol + len(ensure_iter(val)) ))
        self.app.output(self.priority, hw, row, startcol, val)

    def release(self, hw, pins):
        self.app.release(self.priority, hw, pins)

    def outtake(self, hw, row, colrange):
        self.app.outtake(self.priority, hw, row, colrange)

    def outreset(self, hw, row, colrange, val):
        colrange = ensure_iter(colrange)
        self.output(hw, row, colrange[0], (val,)*len(colrange))
        self.app.loop.call_soon(lambda:self.app.outtake(self.priority, hw, row, colrange))
