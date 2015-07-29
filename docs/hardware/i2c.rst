I2C-based Components
****************************

These components depend on Adafruit libraries, and in some cases are just
wrappers around the Adafruit class to make them compatible with the
framework. 

.. autoclass:: hardware.component.I2CComponent

   I2C hardware is usually interfaced with using an Adafruit library, so this
   base class does very little.

hardware.adc module
===================

Provides an interface to Analog-to-Digital converters.

.. module:: hardware.adc
   :synopsis: Provides an interface to Analog-to-Digital converters.

.. autoclass:: ADC4

   This class uses both the :class:`~.LoopedInput` and :class:`~.EventedInput`
   interfaces.

   .. automethod:: read

      This method will read a value from the hardware and return it.

   .. automethod:: get

      This method returns the last value read for the pin by the loop. Note
      that it will only return the value read during the input loop, not
      one read during a manual call to :meth:`read`.

.. autoclass:: ScaledADC4

   This class provides the same interface as :class:`ADC4`, but scales
   readings to the bounds and precision set at object instantion. This can be
   helpful for reducing noise when using the event-based model.

.. autoclass:: ADCSet

   This class presents an interface similar to above that makes many ADCs
   appear as one.

   It does not, however, support the :meth:`.read` method.
		     
hardware.keypad module
======================

.. module:: hardware.keypad
   :synopsis: Provides an interface to an Adafruit Trellis keypad.

.. class:: LEDKeypad(addr)

   In addition to providing the standard :class:`~.EventedInput` and
   :class:`~.LoopedInput` interfaces, :class:`LEDKeypad` has the following
   methods to control the LEDs:

   .. automethod:: set_leds

      Use this method to set one or more leds by passing a dictionary of
      LED indices and boolean values. It automatically flushes the display
      buffer after writing all specified LEDs. Unspecififed LEDs will remain
      unchanged.

   The following two methods were written to provide compatibility with the
   application framework and may be removed, so they should not be used.

   .. automethod:: insert

   .. automethod:: flush
