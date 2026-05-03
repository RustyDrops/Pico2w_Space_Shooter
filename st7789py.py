import time
from machine import Pin, SPI
import struct

class ST7789:
    def __init__(self, spi, width, height, reset, dc, cs=None, backlight=None):
        self.spi = spi
        self.width = width
        self.height = height
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self.init()

    def write_cmd(self, cmd):
        self.dc.off()
        if self.cs: self.cs.off()
        self.spi.write(bytearray([cmd]))
        if self.cs: self.cs.on()

    def write_data(self, data):
        self.dc.on()
        if self.cs: self.cs.off()
        self.spi.write(data)
        if self.cs: self.cs.on()

    def init(self):
        # Extended Reset Cycle
        if self.reset:
            self.reset.on()
            time.sleep_ms(100)
            self.reset.off()
            time.sleep_ms(100)
            self.reset.on()
            time.sleep_ms(200)

        self.write_cmd(0x01) # SW Reset
        time.sleep_ms(150)
        self.write_cmd(0x11) # Sleep Out
        time.sleep_ms(255)
        
        self.write_cmd(0x3A) # Colmod
        self.write_data(bytearray([0x55])) # 16bit
        
        self.write_cmd(0x36) # Madctl
        self.write_data(bytearray([0x00]))
        
        self.write_cmd(0x21) # Inv On (Required for Waveshare)
        self.write_cmd(0x13) # Normal Display
        self.write_cmd(0x29) # Display On
        
        if self.backlight:
            self.backlight.on()

    def blit(self, x, y, w, h, data):
        self.write_cmd(0x2A) # CASET
        self.write_data(struct.pack(">HH", x, x + w - 1))
        self.write_cmd(0x2B) # RASET
        self.write_data(struct.pack(">HH", y, y + h - 1))
        self.write_cmd(0x2C) # RAMWR
        self.dc.on()
        if self.cs: self.cs.off()
        self.spi.write(data)
        if self.cs: self.cs.on()
