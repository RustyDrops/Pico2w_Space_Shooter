import time
from machine import Pin, SPI
import struct

# Constants
ST7789_SWRESET = 0x01
ST7789_SLPOUT = 0x11
ST7789_NORON = 0x13
ST7789_INVOFF = 0x20
ST7789_INVON = 0x21
ST7789_DISPON = 0x29
ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C
ST7789_COLMOD = 0x3A
ST7789_MADCTL = 0x36

class ST7789:
    def __init__(self, spi, width, height, reset, dc, cs=None, backlight=None, rotation=0):
        self.spi = spi
        self.width = width
        self.height = height
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self.rotation = rotation
        
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
        if self.reset:
            self.reset.on()
            time.sleep_ms(50)
            self.reset.off()
            time.sleep_ms(50)
            self.reset.on()
            time.sleep_ms(150)

        self.write_cmd(ST7789_SWRESET)
        time.sleep_ms(150)
        self.write_cmd(ST7789_SLPOUT)
        time.sleep_ms(255)
        self.write_cmd(ST7789_COLMOD)
        self.write_data(bytearray([0x55])) # 16-bit color
        self.write_cmd(ST7789_MADCTL)
        self.write_data(bytearray([0x00])) # Default orientation
        self.write_cmd(ST7789_INVON) # Invert for this display
        self.write_cmd(ST7789_NORON)
        self.write_cmd(ST7789_DISPON)
        
        if self.backlight:
            self.backlight.on()

    def set_window(self, x0, y0, x1, y1):
        if x0 > x1 or y0 > y1:
            return
        
        # Adjust offsets for 240x240 on 320x240 controller if necessary
        # Waveshare Pico-LCD-1.3 usually has zero offset but let's be careful
        self.write_cmd(ST7789_CASET)
        self.write_data(struct.pack(">HH", x0, x1))
        self.write_cmd(ST7789_RASET)
        self.write_data(struct.pack(">HH", y0, y1))
        self.write_cmd(ST7789_RAMWR)

    def fill(self, color):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        # Fast fill by blocks
        line = bytearray([color >> 8, color & 0xFF] * self.width)
        for _ in range(self.height):
            self.write_data(line)

    def blit(self, x, y, w, h, data):
        self.set_window(x, y, x + w - 1, y + h - 1)
        self.write_data(data)
