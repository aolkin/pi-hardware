Application Framework
*****************************
	  
.. module:: hardware.app
    :synopsis: Provides the access management application framework.

A complex and unfortunately heavy framework for managing access to many
devices by many software components is provided.

.. todo:: Rewrite so things aren't imported into the root namespace to speed
	  things up.

A hardware application is made up of one :class:`HardwareApp` class and many
:class:`Context` classes. The latter represent different parts of the
application that may desire concurrent access to hardware components.

Application
=============================

.. class:: HardwareApp

   Applications should inherit from this class. It handles priority-based
   contextual I/O and init cycles across multiple devices with an asyncio
   event loop.

   Output devices used with it must provide an `insert(row, col, val)`
   method, and may provide a `flush()` method, which will be called after
   all calls to `insert()`.

   Input devices must use the :class:`~.LoopedInput` and
   :class:`~.EventedInput` interfaces.

   .. method:: add_hw(*objects)

      This method should be passed any number of components (though at least
      one) and will add them to the application's automatic hardware init cycle
      management, initializing them immediately if necessary.

   .. automethod:: mainloop

      This method will start the `asyncio` event loop, which will run until
      a `KeyboardInterrupt` is caught or :meth:`quit` is called.

   .. automethod:: quit

      Use this method to stop the :meth:`mainloop`.

Contexts
=============================

.. autoclass:: Context

   All :class:`Context` objects must know what app they belong to, so the
   :class:`HardwareApp` object in use must be passed in.

   .. method:: enter

      This method is the beginning of the visible life cycle of a
      :class:`Context`. Use it to make any initial calls to :meth:`capture`
      and :meth:`output` necessary, and call it when the app should begin
      using it.

   .. method:: leave

      The opposite of :meth:`enter`, this method will :meth:`release` all
      captured inputs and :meth:`outtake` all outputs used during the entire
      lifecycle of the :class:`Context`. It should be called when the app is
      done with it.

      This should automatically catch all used inputs and outputs and release
      them, and as such should usually not need to be overwritten.
      
   .. attribute:: priority

      This should be set at a class level to indicate the priority of the
      :class:`Context`. A lower priority value will take precendence over
      a :class:`Context` with a larger number for its priority.

   The following two methods should be used by :class:`Context` objects, but
   not overwritten.
      
   .. method:: capture(hw, pins, cb)

      Use this method to assign callbacks to one or more pins on an input
      device. They will be called with the triggering pin as an argument
      when the event happens only if the current context is the lowest priority
      on the stack.

      `hw` should be the object on which to register the
      callback. `pins` can be a single integer or a sequence of pins to
      register the callback for. `cb` should be the callback function.

   .. method:: output(hw, row, startcol, val)

      Use this method to display values on a piece of hardware. They will be
      shown only is the displaying :class:`Context` is the lowest priority on
      the stack.

      `hw` should be the object on which to display the values. `row` and
      `startcol` should be the coordinates to begin displaying at. If `val` is
      a sequence, it will be split up and assigned along the rest of the row,
      but be careful because if the value is longer than the remaining room
      on the row, it will simply try to output beyond the end of the row.

   .. method:: release(hw, pins)

      This method will remove callbacks assigned with :meth:`capture`.

   .. method:: outtake(hw, row, colrange)

      This method will stop displaying at the given coordinate range,
      allowing whatever was below to be displayed. Note that this will
      usually not actually change the contents of the hardware display unless
      something else tries to output to it.
