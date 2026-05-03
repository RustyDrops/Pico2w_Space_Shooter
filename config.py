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

# --- Arcade Settings ---
ADAPTIVE_DIFFICULTY = True
PERSISTENT_FILE = "save_data.json"
BOSS_SCORE_THRESHOLD = 5000  
SHAKE_INTENSITY = 4         
PLANET_RARITY = 500         
MAX_MULTIPLIER = 10

# --- Progression ---
SECTOR_LENGTH = 10000        # Score required to clear a sector
UPGRADE_COST_BASE = 500     # Base cost for the shop
MAX_UPGRADE_LEVEL = 5

# --- AI Pilot Settings (Reinforcement Learning) ---
AI_BRAIN_FILE = "soul_pilot.json"
AI_REPORT_FILE = "pilot_report.json"
AI_ALPHA = 0.1             # Learning Rate
AI_GAMMA = 0.95            # Discount Factor
AI_EPSILON = 0.2           # Exploration Rate
AI_THINK_RATE = 5          # Actions happen every 5 frames
AI_DASHBOARD_HEIGHT = 20    # Height of AI status bar at bottom
AI_ENABLED_BY_DEFAULT = False
