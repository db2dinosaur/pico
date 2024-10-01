# pico
Some Micropython device support stuff for the Pimoroni supplied Raspberry Pi Pico W.

Nothing clever - to use the module, copy it onto the board (in Thonny, right click the downloaded file and select "Upload to /"), then import.

* rotary_i2c.py - class RotaryI2C that exposes a rotary encoder over I2C. We use this device a lot for user input. See comments in the top of the code for use instructions.
