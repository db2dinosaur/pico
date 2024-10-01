# MIT License (MIT)
# Copyright (c) 2024 James Gill
# https://opensource.org/licenses/MIT

# Provide a simple application interface to an I2C provisioned rotary encoder
# NB - this implementation is for the Pimoroni Pico W Micropython code base.
#
# Tested vs Rapbery Pi Pico W and using an encoder from RS provisioned on this
# I2C / STEMMA QT / Qwiic breakout: https://shop.pimoroni.com/products/adafruit-i2c-qt-rotary-encoder-with-neopixel-stemma-qt-qwiic?variant=39341919141971 

# Documentation:
#   from rotary_i2c import RotaryI2C
#   enc = RotaryI2C(16,17,400000,0,24,54)
#   print(enc.position())
#   if enc.button():
#      print("Clicked")
# If you don't know your device address:
#   from rotary_i2c import RotaryI2C
#   enc = RotaryI2C(16,17,400000)
#   print(enc.scan())
# More than one device to talk to? Switch device addresses with:
#   enc.set_device(addr2)
# If you want to change the enocder limits:
#   enc.min_val = 12
#   enc.max_val = 16
# We always wrap around, but could add a mode, I suppose?
# Note also that the primitive interfaces are exposed, so if you have other
# simple I2C needs, knock yourselves out :-)
#
# To poll data from our device, we send it commands and it sends us data back:
#   CMD        DATA
#   0x11,0x40  Send a delta from the last position (+/-integer)
#   0x01,0x04  Send status data byte[0] LSB = button state. 0 = pushed

from machine import Pin
from struct import unpack
from time import sleep_ms
from pimoroni_i2c import PimoroniI2C

CMD_READ_VAL_POS = const(0x11)
CMD_READ_BUTTONS = const(0x01)
CMD_READ_NUMBER = const(0x04)
VAL_POSITION = const(0x30)
VAL_DELTA = const(0x40)

class RotaryI2C:
    def __init__(
        self,
        pin_num_sda,
        pin_num_scl,
        freq=400000,
        min_val=0,
        max_val=10,
        devno=0
    ):
        self.pin_num_sda = pin_num_sda
        self.pin_num_scl = pin_num_scl
        self.freq = freq
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.i2c = PimoroniI2C(pin_num_sda,pin_num_scl,freq)
        self.devno = devno

# scan the i2c bus for devices
    def scan(self):
        return(self.i2c.scan())

# set the device number to talk to
    def set_device(self,devno):
        self.devno = devno

# write a message in a bytearray to an i2c device
    def i2c_write(self,cdata):
        if self.devno == 0:
            raise Exception("ERROR [rotary_i2c.i2c_write()] : No target device number has been set - I don't know where to send it!")
        clen = len(cdata)
        nsent = self.i2c.writeto(self.devno,cdata)
        return(nsent)

# read data from an i2c device into a bytearray - we write the command to request data to the device and read the response
# Parms:
# 1. cmd   = command to send the device - see CMD_xxx literals, above
# 2. cdata = data to send with the command
# 3. dsize = size of the anticipated reply message
    def i2c_read(self,cdata,dsize):
        self.i2c_write(cdata)
        sleep_ms(8)
        reply = bytearray(dsize)
        self.i2c.readfrom_into(self.devno,reply)
        return(reply)

# ask for the delta on the position of the encoder and apply this to our value (within bounds) before returning it
# Parms:
#  None
    def position(self):
        cdata = bytearray([CMD_READ_VAL_POS,VAL_DELTA])
        reply = self.i2c_read(cdata,4)
        delta = unpack(">l",reply)[0]
        self.value -= delta
        if self.value < self.min_val:
            self.value = self.max_val
        elif self.value > self.max_val:
            self.value = self.min_val
        return(self.value)

# get the button status - returns True if clicked
# Parms:
#   None
    def button(self):
        rv = False
        cdata = bytearray([CMD_READ_BUTTONS,CMD_READ_NUMBER])
        reply = self.i2c_read(cdata,4)
        if (reply[0] & 0x01) == 0:
            rv = True
        return(rv)
