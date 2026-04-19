from machine import Pin

# Display Settings (Waveshare Pico-LCD-1.3)
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240

# Pin Mappings
PIN_LCD_BL = 13
PIN_LCD_DC = 8
PIN_LCD_CS = 9
PIN_LCD_SCK = 10
PIN_LCD_MOSI = 11
PIN_LCD_RST = 12

# Input Mappings (Buttons)
PIN_KEY_A = 15     # Fire
PIN_KEY_B = 17     # Start / Select
PIN_KEY_X = 2      # Auxiliary / Up
PIN_KEY_Y = 3      # Auxiliary / Center
PIN_JOY_UP = 2
PIN_JOY_DOWN = 18
PIN_JOY_LEFT = 16
PIN_JOY_RIGHT = 20
PIN_JOY_CTRL = 3

# Wi-Fi Credentials
WIFI_SSID = 'YOUR_WIFI_SSID'
WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'

# API Configuration
CLOUD_SUBMIT_URL = "https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/submit_score"
CLOUD_GET_URL = "https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/get_leaderboard"

# --- New Arcade Settings ---
ADAPTIVE_DIFFICULTY = True
PERSISTENT_FILE = "best_score.json"
BOSS_SCORE_THRESHOLD = 5000  # Spawn boss every 5000 pts
SHAKE_INTENSITY = 4         # Pixels for screen shake
PLANET_RARITY = 500         # 1 in 500 chance per frame
MAX_MULTIPLIER = 10
