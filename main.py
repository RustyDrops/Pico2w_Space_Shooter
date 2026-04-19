import machine
import time
import framebuf
import random
import network
import urequests
import json
import os
import sys
from machine import Pin, SPI
from st7789py import ST7789
import config
import sprites
from ai_pilot import QPilot

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
joy_ctrl  = Pin(config.PIN_JOY_CTRL, Pin.IN, Pin.PULL_UP)

# Use secondary fbuf for clean rendering
fbuf_data = bytearray(config.DISPLAY_WIDTH * config.DISPLAY_HEIGHT * 2)
fb = framebuf.FrameBuffer(fbuf_data, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, framebuf.RGB565)

# Initialize Sprites & AI
sprites.compile_all()
SPR = sprites.COMPILED
pilot = QPilot()
COMMAND_BRIDGE = "cmd_bridge.txt"

# --- Colors ---
BLACK = 0x0000
WHITE = 0xFFFF
RED   = 0xF800
GREEN = 0x07E0
BLUE  = 0x001F
YELLOW= 0xFFE0
MAGENTA=0xF81F
ORANGE= 0xFD20
GREY  = 0x7BEF

# --- Game States ---
MENU = 0
PLAYING = 1
CONFIRM_AI = 2
GAME_OVER = 3
state = MENU

# --- Game Variables ---
player = {"x": 112, "y": 180, "w": 16, "h": 16, "fire_rate": 200, "type": "single", "bank": 0}
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
global_tick = 0
autopilot = config.AI_ENABLED_BY_DEFAULT
ai_action = 0      # Current action the AI is holding
last_reward = 0    # Current reward accumulation
ai_stats = {"score": 0, "frames": 0, "kills": 0, "bosses": 0}

# Parallax Stars
stars = [{"x": random.randint(0, 239), "y": random.randint(0, 239), "speed": random.uniform(0.5, 3)} for _ in range(40)]

# --- Persistence ---
def load_best_score():
    global best_score
    try:
        if config.PERSISTENT_FILE in os.listdir():
            with open(config.PERSISTENT_FILE, "r") as f:
                best_score = json.load(f).get("best", 0)
    except: pass

def save_best_score():
    try:
        with open(config.PERSISTENT_FILE, "w") as f:
            json.dump({"best": best_score}, f)
    except: pass

def write_pilot_digest(result="ACTIVE"):
    """ Generates low-token report for AnnIs OS """
    try:
        report = {
            "res": result,
            "scr": score,
            "kil": ai_stats["kills"],
            "states": len(pilot.q_table),
            "mult": multiplier
        }
        with open(config.AI_REPORT_FILE, "w") as f:
            json.dump(report, f)
    except: pass

load_best_score()

# --- Helper Functions ---
def check_collision(rect1, rect2):
    return (rect1["x"] < rect2["x"] + rect2["w"] and
            rect1["x"] + rect1["w"] > rect2["x"] and
            rect1["y"] < rect2["y"] + rect2["h"] and
            rect1["y"] + rect1["h"] > rect2["y"])

def reset_game():
    global score, bullets, enemies, player, enemy_timer, particles, multiplier, combo_timer, boss, powerups, ai_stats
    score = 0; multiplier = 1; combo_timer = 0
    bullets = []; enemies = []; particles = []; powerups = []
    boss = None; enemy_timer = 0
    player["x"] = 112; player["y"] = 180; player["fire_rate"] = 200; player["type"] = "single"
    ai_stats = {"score": 0, "frames": 0, "kills": 0, "bosses": 0}

def spawn_enemy():
    etype = "scout" if random.random() > 0.3 else "tank"
    hp = 1 if etype == "scout" else 3
    speed = random.randint(3, 5) if etype == "scout" else random.randint(1, 2)
    enemies.append({"x": random.randint(0, 220), "y": -20, "w": 16, "h": 16, "speed": speed, "type": etype, "hp": hp})

def trigger_shake():
    global shake_timer; shake_timer = 8

# --- Core Loop ---
last_tick = time.ticks_ms()
fire_timer = 0
current_state = (0, 0, 0, 0)

while True:
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_tick)
    last_tick = now
    global_tick += 1
    
    # --- Command Bridge Parser (Incoming Agentic/Serial Commands) ---
    cmd = None
    if sys.stdin in machine.select.select([sys.stdin], [], [], 0)[0]:
        cmd = sys.stdin.readline().strip().upper()
    
    # Check for file-based bridge (AnnIs Coach Tool)
    if COMMAND_BRIDGE in os.listdir():
        try:
            with open(COMMAND_BRIDGE, "r") as f:
                cmd = f.read().strip().upper()
            os.remove(COMMAND_BRIDGE) # Consume command
        except: pass

    if cmd:
        if "AUTOPILOT_ON" in cmd: autopilot = True
        elif "AUTOPILOT_OFF" in cmd: autopilot = False
        elif "SAVE_BRAIN" in cmd: pilot.save_brain()

    # --- Game Logic ---
    if state == MENU:
        if not btn_a.value() or not btn_b.value():
            reset_game()
            state = PLAYING
            time.sleep_ms(300)

    elif state == CONFIRM_AI:
        if not btn_a.value(): # Yes
            autopilot = True
            state = PLAYING
            time.sleep_ms(300)
        if not btn_b.value(): # No
            autopilot = False
            state = PLAYING
            time.sleep_ms(300)

    elif state == PLAYING:
        # Toggle Autopilot (Manual override)
        if not joy_ctrl.value():
            state = CONFIRM_AI
            time.sleep_ms(300)

        # Update Stars
        for s in stars:
            s["y"] += s["speed"]
            if s["y"] > 240: s["y"] = 0; s["x"] = random.randint(0, 239)
        
        # AI Thought Cycle (Every 5 frames)
        if autopilot and (global_tick % config.AI_THINK_RATE == 0):
            next_s = pilot.discretize(player["x"], enemies, powerups)
            reward = 1 # Survival
            if last_reward != 0:
                reward += last_reward
                last_reward = 0
            
            pilot.learn(current_state, ai_action, reward, next_s)
            current_state = next_s
            ai_action = pilot.get_action(current_state)

        # Apply Movement (AI or Manual)
        player["bank"] = 0
        l_in = (autopilot and ai_action == 1) or (not autopilot and not joy_left.value())
        r_in = (autopilot and ai_action == 2) or (not autopilot and not joy_right.value())
        u_in = (not autopilot and not joy_up.value())
        d_in = (not autopilot and not joy_down.value())
        f_in = (autopilot and ai_action == 3) or (not autopilot and not btn_a.value()) # Fire

        if l_in and player["x"] > 0: player["x"] -= 4; player["bank"] = -1
        if r_in and player["x"] < 224: player["x"] += 4; player["bank"] = 1
        if u_in and player["y"] > 0: player["y"] -= 4
        if d_in and player["y"] < (240 - config.AI_DASHBOARD_HEIGHT - 16): player["y"] += 4
        
        # Shooting
        if f_in and time.ticks_diff(now, fire_timer) > player["fire_rate"]:
            if player["type"] == "single":
                bullets.append({"x": player["x"] + 6, "y": player["y"], "w": 4, "h": 8})
            elif player["type"] == "triple":
                bullets.append({"x": player["x"] + 6, "y": player["y"], "w": 4, "h": 8, "vx": 0})
                bullets.append({"x": player["x"], "y": player["y"]+4, "w": 4, "h": 8, "vx": -2})
                bullets.append({"x": player["x"]+12, "y": player["y"]+4, "w": 4, "h": 8, "vx": 2})
            fire_timer = now

        # Spawning & Difficulty
        if not boss:
            enemy_timer += 1
            if enemy_timer > max(10, 30 - (score // 1000)):
                spawn_enemy(); enemy_timer = 0
            if score > 0 and score % config.BOSS_SCORE_THRESHOLD == 0 and score // config.BOSS_SCORE_THRESHOLD > ai_stats["bosses"]:
                boss = {"x": 88, "y": -100, "w": 64, "h": 30, "hp": 50, "max_hp": 50, "vx": 2, "target_y": 30}
                ai_stats["bosses"] += 1

        # Entity Updates
        for b in bullets[:]:
            b["y"] -= 8
            if "vx" in b: b["x"] += b["vx"]
            if b["y"] < -10: bullets.remove(b)
            
        for e in enemies[:]:
            e["y"] += e["speed"]
            if e["y"] > 240: enemies.remove(e)
            if check_collision(player, e):
                last_reward -= 500
                trigger_shake(); state = GAME_OVER
        
        for p in powerups[:]:
            p["y"] += 2
            if p["y"] > 240: powerups.remove(p)
            if check_collision(player, p):
                player["type"] = p["type"]
                last_reward += 300; score += 200
                powerups.remove(p)
        
        # Bullet Collisions
        for b in bullets[:]:
            if boss and check_collision(b, boss):
                if b in bullets: bullets.remove(b)
                boss["hp"] -= 1
                if boss["hp"] <= 0:
                    score += 5000; boss = None
                    last_reward += 2000; trigger_shake()
                    pilot.save_brain() # Milstone save
                break
            for e in enemies[:]:
                if check_collision(b, e):
                    if b in bullets: bullets.remove(b)
                    e["hp"] -= 1
                    if e["hp"] <= 0:
                        enemies.remove(e); last_reward += 100
                        ai_stats["kills"] += 1; multiplier = min(10, multiplier + 1)
                        score += 100 * multiplier
                        if random.random() < 0.1:
                            ptype = "triple" if random.random() > 0.5 else "speed"
                            powerups.append({"x": e["x"], "y": e["y"], "w": 12, "h": 12, "type": ptype})
                    break

        # Combo Decay
        if combo_timer > 0: combo_timer -= 1
        else: multiplier = 1

    elif state == GAME_OVER:
        if score > best_score: best_score = score; save_best_score()
        write_pilot_digest("DEFEAT")
        if not btn_a.value(): state = MENU; time.sleep_ms(300)

    # --- Draw ---
    fb.fill(BLACK)
    for s in stars: fb.pixel(int(s["x"]), int(s["y"]), WHITE)
    
    # Render with Shake
    ox, oy = 0, 0
    if shake_timer > 0:
        ox = random.randint(-4, 4); oy = random.randint(-4, 4); shake_timer -= 1

    if state == MENU:
        fb.text("PICO ARCADE", 75, 80, YELLOW)
        fb.text(f"HI-SCORE: {best_score}", 65, 110, WHITE)
        fb.text("PRESS A TO START", 55, 160, GREEN)
    elif state == CONFIRM_AI:
        fb.fill_rect(40, 60, 160, 100, GREY)
        fb.text("ENGAGE PILOT?", 65, 80, WHITE)
        fb.text("A: YES", 80, 110, GREEN)
        fb.text("B: NO", 80, 130, RED)
    elif state == PLAYING:
        # Determine Animation Frame
        f_idx = "f2" if (global_tick // 6) % 2 == 1 else "f1"
        
        # Draw Player
        pspr = f'player_straight_{f_idx}'
        if player["bank"] == -1: pspr = f'player_left_{f_idx}'
        elif player["bank"] == 1: pspr = f'player_right_{f_idx}'
        fb.blit(SPR[pspr], int(player["x"]), int(player["y"]), 0x0000)
        
        for b in bullets: fb.fill_rect(int(b["x"]), int(b["y"]), b["w"], b["h"], YELLOW)
        for e in enemies: fb.blit(SPR[f'{e["type"]}_{f_idx}'], int(e["x"]), int(e["y"]), 0x0000)
        for p in powerups: fb.blit(SPR[f'pu_{p["type"]}_{f_idx}'], int(p["x"]), int(p["y"]), 0x0000)
        if boss: fb.blit(SPR[f'boss_{f_idx}'], int(boss["x"]), int(boss["y"]), 0x0000)
        
        # UI & Dashboard
        fb.text(f"SCORE: {score}", 5, 5, WHITE)
        if autopilot: fb.text("AI ACTIVE", 160, 5, GREEN)
        
        # AI Status Bar (Bottom)
        db_y = 240 - config.AI_DASHBOARD_HEIGHT
        fb.fill_rect(0, db_y, 240, config.AI_DASHBOARD_HEIGHT, GREY)
        # Brain Fill Bar (States known)
        know_w = min(230, int((len(pilot.q_table)/1000) * 230))
        fb.text("BRAIN:", 5, db_y+5, WHITE)
        fb.fill_rect(55, db_y+7, 175, 6, BLACK)
        fb.fill_rect(55, db_y+7, know_w, 6, BLUE)

    elif state == GAME_OVER:
        fb.text("GAME OVER", 80, 80, RED)
        fb.text(f"SCORE: {score}", 80, 110, WHITE)
        fb.text("PRESS A TO RESTART", 50, 160, GREEN)

    display.blit(ox, oy, 240, 240, fbuf_data)
    time.sleep_ms(max(0, 16 - dt))
