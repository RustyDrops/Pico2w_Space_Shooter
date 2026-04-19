import machine
import time
import framebuf
import random
import network
import urequests
import json
from machine import Pin, SPI
from st7789py import ST7789
import config

# --- Hardware Initialization ---
# SPI for Display
spi = SPI(1, baudrate=40000000, sck=Pin(config.PIN_LCD_SCK), mosi=Pin(config.PIN_LCD_MOSI))
display = ST7789(
    spi, 
    config.DISPLAY_WIDTH, 
    config.DISPLAY_HEIGHT, 
    reset=Pin(config.PIN_LCD_RST, Pin.OUT),
    dc=Pin(config.PIN_LCD_DC, Pin.OUT),
    cs=Pin(config.PIN_LCD_CS, Pin.OUT),
    backlight=Pin(config.PIN_LCD_BL, Pin.OUT)
)

# Buttons
btn_a = Pin(config.PIN_KEY_A, Pin.IN, Pin.PULL_UP) # Fire
btn_b = Pin(config.PIN_KEY_B, Pin.IN, Pin.PULL_UP) # Select
joy_up    = Pin(config.PIN_JOY_UP, Pin.IN, Pin.PULL_UP)
joy_down  = Pin(config.PIN_JOY_DOWN, Pin.IN, Pin.PULL_UP)
joy_left  = Pin(config.PIN_JOY_LEFT, Pin.IN, Pin.PULL_UP)
joy_right = Pin(config.PIN_JOY_RIGHT, Pin.IN, Pin.PULL_UP)
joy_ctrl  = Pin(config.PIN_JOY_CTRL, Pin.IN, Pin.PULL_UP)

# Framebuffer for double buffering
# RGB565 is 2 bytes per pixel
fbuf_data = bytearray(config.DISPLAY_WIDTH * config.DISPLAY_HEIGHT * 2)
fb = framebuf.FrameBuffer(fbuf_data, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, framebuf.RGB565)

# --- Colors (RGB565 format) ---
BLACK = 0x0000
WHITE = 0xFFFF
RED   = 0xF800
GREEN = 0x07E0
BLUE  = 0x001F
YELLOW= 0xFFE0

# --- Game States ---
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEADERBOARD = 3
state = MENU

# --- Game Variables ---
player = {"x": 112, "y": 200, "w": 16, "h": 16}
bullets = []
enemies = []
particles = [] # For explosions
score = 0
enemy_timer = 0
initials = ["A", "A", "A"]
initial_idx = 0
leaderboard_data = []

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        # Timeout after 10 seconds
        for _ in range(100):
            if wlan.isconnected(): break
            time.sleep_ms(100)
    return wlan.isconnected()

def check_collision(rect1, rect2):
    return (rect1["x"] < rect2["x"] + rect2["w"] and
            rect1["x"] + rect1["w"] > rect2["x"] and
            rect1["y"] < rect2["y"] + rect2["h"] and
            rect1["y"] + rect1["h"] > rect2["y"])

def reset_game():
    global score, bullets, enemies, player, enemy_timer, particles
    score = 0
    bullets = []
    enemies = []
    particles = []
    player["x"] = 112
    player["y"] = 200
    enemy_timer = 0

def submit_score():
    if not connect_wifi():
        return False
    name = "".join(initials)
    payload = json.dumps({"name": name, "score": score})
    headers = {'Content-Type': 'application/json'}
    try:
        res = urequests.post(config.CLOUD_SUBMIT_URL, data=payload, headers=headers)
        res.close()
        return True
    except:
        return False

def fetch_leaderboard():
    global leaderboard_data
    if not connect_wifi():
        return False
    try:
        res = urequests.get(config.CLOUD_GET_URL)
        data = res.json()
        leaderboard_data = data.get("leaderboard", [])
        res.close()
        return True
    except:
        return False

# --- Main Loop ---
last_tick = time.ticks_ms()

while True:
    dt = time.ticks_diff(time.ticks_ms(), last_tick)
    last_tick = time.ticks_ms()
    
    # --- Input & Logic ---
    if state == MENU:
        if not btn_a.value() or not btn_b.value() or not joy_ctrl.value():
            reset_game()
            state = PLAYING
            time.sleep_ms(200)

    elif state == PLAYING:
        # Movement
        if not joy_left.value() and player["x"] > 0: player["x"] -= 3
        if not joy_right.value() and player["x"] < config.DISPLAY_WIDTH - player["w"]: player["x"] += 3
        if not joy_up.value() and player["y"] > 0: player["y"] -= 3
        if not joy_down.value() and player["y"] < config.DISPLAY_HEIGHT - player["h"]: player["y"] += 3
        
        # Shooting
        if not btn_a.value():
            if len(bullets) < 5: # Limit bullets on screen
                bullets.append({"x": player["x"] + 6, "y": player["y"], "w": 4, "h": 8})
                time.sleep_ms(150) # Debounce/Rate limit
        
        # Enemy Spawning
        enemy_timer += 1
        if enemy_timer > 30: # Spawn every ~0.5s
            enemies.append({"x": random.randint(0, 220), "y": -20, "w": 20, "h": 20, "speed": random.randint(2, 5)})
            enemy_timer = 0
            
        # Update Bullets
        for b in bullets[:]:
            b["y"] -= 7
            if b["y"] < -10: bullets.remove(b)
            
        # Update Enemies
        for e in enemies[:]:
            e["y"] += e["speed"]
            if e["y"] > config.DISPLAY_HEIGHT: 
                enemies.remove(e)
                # Penalty for letting enemies pass? No, just keep it simple.
            
            # Collision: Player vs Enemy
            if check_collision(player, e):
                state = GAME_OVER
                time.sleep_ms(200)
        
        # Collision: Bullet vs Enemy
        for b in bullets[:]:
            for e in enemies[:]:
                if check_collision(b, e):
                    if b in bullets: bullets.remove(b)
                    if e in enemies: enemies.remove(e)
                    score += 100
                    # Create explosion particles
                    for _ in range(5):
                        particles.append({"x": e["x"]+10, "y": e["y"]+10, "vx": random.uniform(-2, 2), "vy": random.uniform(-2, 2), "life": 10})
                    break
                    
        # Update Particles
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0: particles.remove(p)

    elif state == GAME_OVER:
        # Move through letters
        if not joy_up.value():
            initials[initial_idx] = chr(((ord(initials[initial_idx]) - 65 + 1) % 26) + 65)
            time.sleep_ms(150)
        if not joy_down.value():
            initials[initial_idx] = chr(((ord(initials[initial_idx]) - 65 - 1) % 26) + 65)
            time.sleep_ms(150)
        if not joy_right.value():
            initial_idx = (initial_idx + 1) % 3
            time.sleep_ms(150)
        if not joy_left.value():
            initial_idx = (initial_idx - 1) % 3
            time.sleep_ms(150)
            
        if not btn_a.value(): # Submit
            fb.fill(BLACK)
            fb.text("SUBMITTING...", 70, 110, WHITE)
            display.blit(0, 0, 240, 240, fbuf_data)
            submit_score()
            fetch_leaderboard()
            state = LEADERBOARD
            time.sleep_ms(300)

    elif state == LEADERBOARD:
        if not btn_a.value() or not btn_b.value():
            state = MENU
            time.sleep_ms(300)

    # --- Draw ---
    fb.fill(BLACK)
    
    if state == MENU:
        fb.text("SPACE SHOOTER", 65, 80, YELLOW)
        fb.text("PICO 2W EDITION", 60, 100, WHITE)
        fb.text("PRESS A TO START", 55, 160, GREEN)
        
    elif state == PLAYING:
        # Draw Player (Triangle)
        fb.line(player["x"]+8, player["y"], player["x"], player["y"]+16, WHITE)
        fb.line(player["x"]+8, player["y"], player["x"]+16, player["y"]+16, WHITE)
        fb.line(player["x"], player["y"]+16, player["x"]+16, player["y"]+16, WHITE)
        
        # Draw Bullets
        for b in bullets:
            fb.fill_rect(b["x"], b["y"], b["w"], b["h"], YELLOW)
            
        # Draw Enemies
        for e in enemies:
            fb.fill_rect(e["x"], e["y"], e["w"], e["h"], RED)
            fb.text("!", e["x"]+7, e["y"]+6, WHITE)
            
        # Draw Particles
        for p in particles:
            fb.pixel(int(p["x"]), int(p["y"]), YELLOW)
            
        # UI
        fb.text(f"SCORE: {score}", 5, 5, WHITE)

    elif state == GAME_OVER:
        fb.text("GAME OVER", 80, 60, RED)
        fb.text(f"FINAL SCORE: {score}", 55, 90, WHITE)
        fb.text("ENTER INITIALS:", 55, 130, YELLOW)
        
        for i in range(3):
            color = GREEN if i == initial_idx else WHITE
            fb.text(initials[i], 100 + i*15, 160, color)
            if i == initial_idx:
                fb.line(100 + i*15, 170, 108 + i*15, 170, GREEN)
                
        fb.text("PRESS A TO SUBMIT", 50, 200, WHITE)

    elif state == LEADERBOARD:
        fb.text("LEADERBOARD", 75, 40, YELLOW)
        for i, entry in enumerate(leaderboard_data):
            y = 70 + i*25
            fb.text(f"{i+1}. {entry['name']} - {entry['score']}", 60, y, WHITE)
        
        if not leaderboard_data:
            fb.text("LOADING...", 85, 120, WHITE)
            
        fb.text("PRESS A TO MENU", 60, 210, GREEN)

    # Blit to hardware
    display.blit(0, 0, 240, 240, fbuf_data)
    
    # Target ~60 FPS
    time.sleep_ms(16)
