import machine
import time
import framebuf
from machine import Pin, SPI
from st7789py import ST7789
import config

# --- HARDWARE RECOVERY TEST ---
# This script strips all logic to verify the physical connection.
# Expectation: Magenta screen with "DIAGNOSTIC MODE" text.

machine.freq(150000000)
spi = SPI(1, baudrate=24000000, sck=Pin(config.PIN_LCD_SCK), mosi=Pin(config.PIN_LCD_MOSI))
display = ST7789(
    spi, 
    240, 240, 
    reset=Pin(config.PIN_LCD_RST, Pin.OUT),
    dc=Pin(config.PIN_LCD_DC, Pin.OUT),
    cs=Pin(config.PIN_LCD_CS, Pin.OUT),
    backlight=Pin(config.PIN_LCD_BL, Pin.OUT)
)

# Magenta Background (Big-Endian for ST7789: 0xF81F -> 0x1FF8)
# We use framebuf to draw, then blit.
fbuf_data = bytearray(240 * 240 * 2)
fb = framebuf.FrameBuffer(fbuf_data, 240, 240, framebuf.RGB565)

while True:
    fb.fill(0x1FF8) # Magenta (Swapped)
    fb.text("DIAGNOSTIC MODE", 60, 100, 0xFFFF)
    fb.text("PICO 2W RECOVERY", 60, 120, 0xFFFF)
    
    display.blit(0, 0, 240, 240, fbuf_data)
    time.sleep_ms(500)
