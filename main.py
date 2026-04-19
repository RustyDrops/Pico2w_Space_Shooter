import machine
import time
import framebuf
import random
import network
import urequests
import json
import os
from machine import Pin, SPI
from st7789py import ST7789
import config
import sprites

# --- Hardware Initialization ---
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

btn_a = Pin(config.PIN_KEY_A, Pin.IN, Pin.PULL_UP)
btn_b = Pin(config.PIN_KEY_B, Pin.IN, Pin.PULL_UP)
joy_up    = Pin(config.PIN_JOY_UP, Pin.IN, Pin.PULL_UP)
joy_down  = Pin(config.PIN_JOY_DOWN, Pin.IN, Pin.PULL_UP)
joy_left  = Pin(config.PIN_JOY_LEFT, Pin.IN, Pin.PULL_UP)
joy_right = Pin(config.PIN_JOY_RIGHT, Pin.IN, Pin.PULL_UP)

fbuf_data = bytearray(config.DISPLAY_WIDTH * config.DISPLAY_HEIGHT * 2)
fb = framebuf.FrameBuffer(fbuf_data, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, framebuf.RGB565)

# Initialize Sprites
print("Compiling Sprites...")
sprites.compile_all()
SPR = sprites.COMPILED

# --- Colors ---
BLACK = 0x0000
WHITE = 0xFFFF
RED   = 0xF800
GREEN = 0x07E0
BLUE  = 0x001F
YELLOW= 0xFFE0
ORANGE= 0xFD20

# --- Game States ---
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEADERBOARD = 3
state = MENU

# --- Game Variables ---
player = {"x": 112, "y": 200, "w": 16, "h": 16, "fire_rate": 200, "type": "single", "bank": 0}
bullets = []
enemies = []
powerups = []
particles = []
boss = None
score = 0
best_score = 0
multiplier = 1
combo_timer = 0
enemy_timer = 0
planet = None
shake_timer = 0
global_tick = 0  # Used for animation frames

# Parallax Stars
stars = []
for _ in range(50):
    stars.append({"x": random.randint(0, 239), "y": random.randint(0, 239), "speed": random.uniform(0.5, 3), "color": WHITE})

# --- Persistence ---
def load_best_score():
    global best_score
    try:
        if config.PERSISTENT_FILE in os.listdir():
            with open(config.PERSISTENT_FILE, "r") as f:
                data = json.load(f)
                best_score = data.get("best", 0)
    except:
        best_score = 0

def save_best_score():
    try:
        with open(config.PERSISTENT_FILE, "w") as f:
            json.dump({"best": best_score}, f)
    except:
        pass

load_best_score()

# --- Helper Functions ---
def check_collision(rect1, rect2):
    return (rect1["x"] < rect2["x"] + rect2["w"] and
            rect1["x"] + rect1["w"] > rect2["x"] and
            rect1["y"] < rect2["y"] + rect2["h"] and
            rect1["y"] + rect1["h"] > rect2["y"])

def reset_game():
    global score, bullets, enemies, player, enemy_timer, particles, multiplier, combo_timer, boss, powerups
    score = 0
    multiplier = 1
    combo_timer = 0
    bullets = []
    enemies = []
    particles = []
    powerups = []
    boss = None
    player["x"] = 112
    player["y"] = 200
    player["fire_rate"] = 200
    player["type"] = "single"
    player["bank"] = 0
    enemy_timer = 0

def spawn_enemy():
    etype = "scout" if random.random() > 0.3 else "tank"
    hp = 1 if etype == "scout" else 3
    speed = random.randint(3, 6) if etype == "scout" else random.randint(1, 2)
    enemies.append({"x": random.randint(0, 220), "y": -20, "w": 16, "h": 16, "speed": speed, "type": etype, "hp": hp})

def spawn_boss():
    global boss
    boss = {"x": 88, "y": -100, "w": 64, "h": 30, "hp": 50, "max_hp": 50, "vx": 2, "target_y": 30}

def trigger_shake():
    global shake_timer
    shake_timer = 10

# --- Core Loop ---
last_tick = time.ticks_ms()
fire_timer = 0

while True:
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_tick)
    last_tick = now
    global_tick += 1
    
    # --- Logic ---
    if state == MENU:
        if not btn_a.value() or not btn_b.value():
            reset_game()
            state = PLAYING
            time.sleep_ms(200)

    elif state == PLAYING:
        # Stars
        for s in stars:
            s["y"] += s["speed"]
            if s["y"] > 240:
                s["y"] = 0
                s["x"] = random.randint(0, 239)
        
        # Planet
        if planet:
            planet["y"] += 0.2
            if planet["y"] > 240: planet = None
        elif random.randint(1, config.PLANET_RARITY) == 1:
            planet = {"x": random.randint(0, 180), "y": -60, "size": random.randint(40, 60), "color": BLUE}

        # Player Movement
        player["bank"] = 0
        if not joy_left.value() and player["x"] > 0: 
            player["x"] -= 4
            player["bank"] = -1
        if not joy_right.value() and player["x"] < 240 - player["w"]: 
            player["x"] += 4
            player["bank"] = 1
        if not joy_up.value() and player["y"] > 0: player["y"] -= 4
        if not joy_down.value() and player["y"] < 240 - player["h"]: player["y"] += 4
        
        # Shooting
        if not btn_a.value() and time.ticks_diff(now, fire_timer) > player["fire_rate"]:
            if player["type"] == "single":
                bullets.append({"x": player["x"] + 6, "y": player["y"], "w": 4, "h": 8})
            elif player["type"] == "triple":
                bullets.append({"x": player["x"] + 6, "y": player["y"], "w": 4, "h": 8, "vx": 0})
                bullets.append({"x": player["x"], "y": player["y"]+4, "w": 4, "h": 8, "vx": -2})
                bullets.append({"x": player["x"]+12, "y": player["y"]+4, "w": 4, "h": 8, "vx": 2})
            fire_timer = now
        
        # Spawning
        if not boss:
            enemy_timer += 1
            spawn_rate = 25 - (score // 1000) if config.ADAPTIVE_DIFFICULTY else 30
            if enemy_timer > max(10, spawn_rate):
                spawn_enemy()
                enemy_timer = 0
            if score > 0 and score % config.BOSS_SCORE_THRESHOLD == 0 and score // config.BOSS_SCORE_THRESHOLD >= 1:
                spawn_boss()
                score += 100 

        # Boss Logic
        if boss:
            if boss["y"] < boss["target_y"]: boss["y"] += 1
            else:
                boss["x"] += boss["vx"]
                if boss["x"] <= 0 or boss["x"] >= (240 - boss["w"]): boss["vx"] *= -1
            
            # Boss collision with player
            if check_collision(player, boss):
                trigger_shake()
                state = GAME_OVER
        
        # Update Bullets
        for b in bullets[:]:
            b["y"] -= 8
            if "vx" in b: b["x"] += b["vx"]
            if b["y"] < -10 or b["x"] < -10 or b["x"] > 250: bullets.remove(b)
            
        # Update Enemies
        for e in enemies[:]:
            e["y"] += e["speed"]
            if e["y"] > 240: enemies.remove(e)
            if check_collision(player, e):
                trigger_shake()
                state = GAME_OVER
        
        # Update Powerups
        for p in powerups[:]:
            p["y"] += 2
            if p["y"] > 240: powerups.remove(p)
            if check_collision(player, p):
                if p["type"] == "triple": player["type"] = "triple"
                elif p["type"] == "speed": player["fire_rate"] = 100
                powerups.remove(p)
                score += 50
        
        # Bullet Collisions
        for b in bullets[:]:
            if boss and check_collision(b, boss):
                if b in bullets: bullets.remove(b)
                boss["hp"] -= 1
                if boss["hp"] <= 0:
                    score += 5000
                    boss = None
                    trigger_shake()
                break
            for e in enemies[:]:
                if check_collision(b, e):
                    if b in bullets: bullets.remove(b)
                    e["hp"] -= 1
                    if e["hp"] <= 0:
                        enemies.remove(e)
                        if random.random() < 0.1:
                            ptype = "triple" if random.random() > 0.5 else "speed"
                            powerups.append({"x": e["x"], "y": e["y"], "w": 12, "h": 12, "type": ptype})
                        
                        combo_timer = 60 
                        if multiplier < config.MAX_MULTIPLIER: multiplier += 1
                        score += 100 * multiplier
                        
                        for _ in range(5):
                            particles.append({"x": e["x"]+8, "y": e["y"]+8, "vx": random.uniform(-2, 2), "vy": random.uniform(-2, 2), "life": 12})
                    break
        
        # Combo Decay
        if combo_timer > 0: combo_timer -= 1
        else: multiplier = 1

        # Particles
        for p in particles[:]:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
            if p["life"] <= 0: particles.remove(p)

    elif state == GAME_OVER:
        if score > best_score:
            best_score = score
            save_best_score()
        if not btn_a.value():
            state = MENU
            time.sleep_ms(300)

    # --- Draw ---
    fb.fill(BLACK)
    
    # Parallax Stars
    for s in stars:
        fb.pixel(int(s["x"]), int(s["y"]), s["color"])
    
    # Planet
    if planet:
        fb.fill_circle(int(planet["x"]), int(planet["y"]), planet["size"], planet["color"])

    # Offset for Shake
    ox, oy = 0, 0
    if shake_timer > 0:
        ox = random.randint(-config.SHAKE_INTENSITY, config.SHAKE_INTENSITY)
        oy = random.randint(-config.SHAKE_INTENSITY, config.SHAKE_INTENSITY)
        shake_timer -= 1

    if state == MENU:
        fb.text("PICO ARCADE", 75, 80, YELLOW)
        fb.text(f"HI-SCORE: {best_score}", 65, 110, WHITE)
        fb.text("PRESS A TO START", 55, 160, GREEN)
        
    elif state == PLAYING:
        # Determine Animation Frame (toggle every 6 ticks)
        f_idx = "f2" if (global_tick // 6) % 2 == 1 else "f1"
        
        # Draw Player Ship depending on banking
        px = int(player["x"])
        py = int(player["y"])
        if player["bank"] == -1:
            fb.blit(SPR[f'player_left_{f_idx}'], px, py, 0x0000)
        elif player["bank"] == 1:
            fb.blit(SPR[f'player_right_{f_idx}'], px, py, 0x0000)
        else:
            fb.blit(SPR[f'player_straight_{f_idx}'], px, py, 0x0000)
        
        # Draw Bullets
        for b in bullets: 
            fb.fill_rect(int(b["x"]), int(b["y"]), b["w"], b["h"], YELLOW)
            
        # Draw Enemies
        for e in enemies:
            fb.blit(SPR[f'{e["type"]}_{f_idx}'], int(e["x"]), int(e["y"]), 0x0000)
            
        # Draw Powerups
        for p in powerups:
            # Powerups have 12x12 sprites
            fb.blit(SPR[f'pu_{p["type"]}_{f_idx}'], int(p["x"]), int(p["y"]), 0x0000)
            
        # Draw Hit Particles
        for p in particles: 
            fb.pixel(int(p["x"]), int(p["y"]), ORANGE)
        
        # Draw Boss
        if boss:
            fb.blit(SPR[f'boss_{f_idx}'], int(boss["x"]), int(boss["y"]), 0x0000)
            # HP Bar
            bw = int((boss["hp"] / boss["max_hp"]) * 200)
            fb.fill_rect(20, 10, 200, 5, RED)
            fb.fill_rect(20, 10, bw, 5, GREEN)
            
        # UI
        fb.text(f"SCORE: {score}", 5, 5, WHITE)
        if multiplier > 1:
            fb.text(f"X{multiplier}", 200, 5, YELLOW)
            fb.fill_rect(200, 15, int((combo_timer/60)*30), 2, YELLOW)

    elif state == GAME_OVER:
        fb.text("GAME OVER", 80, 80, RED)
        fb.text(f"SCORE: {score}", 80, 110, WHITE)
        fb.text("PRESS A TO RESTART", 50, 160, GREEN)

    # Blit with shake offset
    display.blit(ox, oy, 240, 240, fbuf_data)
    
    # Try to maintain ~60 FPS
    time.sleep_ms(max(0, 16 - dt))
