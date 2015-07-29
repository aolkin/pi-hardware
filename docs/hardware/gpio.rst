GPIO-based Components
******************************

GPIO-based components inherit from the following class, which manages the
initialization cycle of the specified GPIO pins.

.. autoclass:: hardware.component.GPIOComponent

   .. method:: init

      Prepares the component for use by setting up the GPIO pins.

   .. method:: cleanup

      This method must be called before the program exits to release
      the used pins.

LED Character Display
=======================

.. module:: hardware.display
   :synopsis: Classes for high-level use of a character LCD

This code is written for a 4x20 monochrome display wired with 4 data pins,
but could be easily adapted for other similar displays.

.. autoclass:: Display

   The base :class:`Display` class provides a basic interface to the
   functionality of the display.

   It is barely thread-safe in that calling methods on a display object in
   multiple threads should never cause invalid commands to be sent to the
   display, but threaded use could still result in an inconsistent state.

   .. automethod:: init

      This method, as with all :class:`.Component` subclasses, must be called
      before using the device. However, this method also takes an argument
      which, if `True`, will light and enable the device as soon as
      initialization finishes.

   .. method:: cleanup

      In addition to resetting the GPIO pins, this method will also disable
      the display and turn off the backlight.
      
   .. automethod:: printString

      This method will write a string of characters to the display.

   .. attribute:: lit

      Setting this to `True` will output high on the backlight pin, and also
      enable the display, but setting it to `False` will only turn off the
      backlight.

   .. attribute:: enabled

      This controls whether the display will actually show anything or be
      blank. Note that even while disabled, the display still maintains
      the memory of what was displayed, so when it is later re-enabled it
      will look exactly as before. Setting this to false will also turn off
      the backlight.

   .. attribute:: cursor

      This controls whether an underscore cursor will be displayed at the
      cursor position on the display.

   .. attribute:: blink

      This controls whether the above cursor will blink repeatedly.

   .. automethod:: clear

   .. automethod:: move

   .. automethod:: shift

   .. automethod:: writeChar

      Use this method to write a custom character to the display's CGRAM.

.. autoclass:: ManagedDisplay

   This class inherits from :class:`Display` and provides a higher level
   interface to a display.

   .. automethod:: insert

      This method will insert the specified string at the given row and
      column. If `wrap` is `True`, it will wrap to the following rows if
      necessary. If `clear` is `True`, it will clear each row before
      writing to it.

      It will return `True` if the entire contents were successfully written
      to the display, or `False` if it ran out of room either because it got
      to the last row or wrapping was disabled.

      This method is thread-safe, multiple simultaneous calls to it will wait
      for each other.

   .. automethod:: move

      Unlike the :meth:`Display.move` method, this method takes a row and
      column of the display to move the insertion cursor to.

   .. automethod:: clearRow

      This method will print spaces to an entire row of the display.

   .. automethod:: redisplay

      This method will redraw the specified row (or entire display if a row
      is not specified) from the :class:`ManagedDisplay` object's cache from
      calls to :meth:`insert`.

.. autoclass:: AnimatedDisplay

   This class provides automatic centering or scrolling of text that does not
   exactly fit the width of a row on the display.

   .. automethod:: displayLoadingAnimation

   .. automethod:: stopLoadingAnimation

      Passing something to `error` will cause `"Error!"` to be printed on
      the display instead of `"Done"` to replace the loading animation.

   .. automethod:: animateRow

      This method will either center the given text in the given row, or
      scroll it over time if the text does not fit in a single row.

   .. automethod:: stopRow

      If `skip_reprint` is not `True`, this method will either clear the row
      or insert as much of the expected contents of the row as it can, with
      ellipses at the end, depending on the value of `clear`.
		   
   .. automethod:: stopRows

      Shorthand for calling :meth:`stopRow` multiple times.

rf module
==================

.. automodule:: hardware.rf
    :members:
    :undoc-members:
