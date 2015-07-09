Hardware Framework
*************************

.. module:: hardware.component
   :synopsis: Base classes for generic functionality

Component Types
=========================

All base hardware classes inherit from a :class:`Component` class or subclass,
which provide the basic init/cleanup cycle, as well as ``with`` support.

.. class:: Component

   The base component class just tracks initialization state and provides
   context management support, subclasses must override init and cleanup if
   they need to do anything during those steps.

.. autoclass:: GPIOComponent

   A :class:`GPIOComponent` automatically manages the initialization cycle of
   the specified GPIO pins.

.. autoclass:: I2CComponent

   I2C hardware is usually interfaced with using an Adafruit library, so this
   base class does very little.

Generic Functionality
=========================

The following classes provide generic functionality for handling various types
of input devices.

.. class:: EventedInput

   :class:`EventedInput` is used by devices to provide a consistent API for
   managing callbacks.

   .. automethod:: add_handler

      This method takes a callback function and either the number of pin on
      which to listen for events, or ``generic`` to listen on all pins. It
      returns an integer id, which can be stored and used to later remove
      the handler.

   .. automethod:: remove_handler

      This method takes the same arguments as above, except instead of a
      callback function to add, the id of the handler to remove.

.. class:: LoopedInput

   :class:`LoopedInput` provides a consistent API for devices which need to be
   polled to get input. It uses a thread to repeatedly call the subclass's
   :meth:`tick` method at the interval defined by the subclass's
   :attr:`_mswait` attribute.

   .. method:: start

   .. method:: stop

   .. automethod:: init

   .. automethod:: cleanup
