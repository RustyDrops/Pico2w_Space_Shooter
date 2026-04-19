# Pico 2W Space Shooter 🚀

A high-performance vertical space shooter for the Raspberry Pi Pico 2W with a cloud-based leaderboard.

![Hardware Setup](https://www.waveshare.com/w/upload/2/2f/Pico-LCD-1.3-1.jpg)

## Features
- **Fast 60 FPS Logic**: Optimized for the Pico 2W and the ST7789 display.
- **State Machine Architecture**: Clean separation between MENU, PLAYING, GAME_OVER, and LEADERBOARD states.
- **Parallax Starfield**: Three-layer background with varied speeds and rare decorative planets.
- **Advanced Entities**: Multiple enemy types (Scouts, Tanks) and massive **Boss Battle** encounters.
- **Power-up System**: Drop-based buffs including Triple Shot and Rapid Fire.
- **Arcade Feedback**: Screen shake, combo multipliers (up to x10), and adaptive difficulty.
- **Persistence**: HI-SCORE tracking using local JSON storage on the Pico.
- **Double Buffering**: Flick-free rendering using MicroPython's `framebuf`.

## Hardware Requirements
- **Raspberry Pi Pico 2W**
- **Waveshare Pico-LCD-1.3** (240x240 Resolution)
- Micro-USB cable

## Installation

### 1. MicroPython Setup
1. Flash your Pico 2W with the latest MicroPython firmware.
2. Clone this repository.
3. Open `config.py` and update:
   - `WIFI_SSID`: Your Wi-Fi name.
   - `WIFI_PASSWORD`: Your Wi-Fi password.
   - `CLOUD_SUBMIT_URL`: Your deployed GCP Function URL (Optional for online sync).
4. Upload `main.py`, `config.py`, and `st7789py.py` to your Pico using Thonny.

### 2. Google Cloud Setup (Backend - Optional)
1. **Firestore**: 
   - Create a Google Cloud Project and initialize Firestore in native mode.
   - Create a collection named `highscores`.
2. **Cloud Functions**:
   - Create a new Python Cloud Function using the code in `backend/`.
   - Set the Entry Point to `leaderboard_proxy`.
   - Allow **unauthenticated invocations** for public access.

## Controls
- **Joystick**: Move ship
- **Key A**: Fire Bullet / Select
- **Key B**: Start Game
- **Game Over**: Use directionals to enter initials, then Key A to submit.

## License
MIT

---

## Technical Architecture & Walkthrough 🕹️

### 🎮 1. MicroPython Game Engine
The game uses a **State Machine** managed in the main loop of `main.py`. Rendering is handled via **Double Buffering** to the ST7789 display to ensure 60 FPS without tearing.

### 🔌 2. Hardware Configuration (`config.py`)
Pre-mapped for the **Waveshare Pico-LCD-1.3**:
*   **ST7789 Display**: Pins 10, 11, 9, 8, 12, 13.
*   **Input Buttons**: Key A (15), Key B (17), Up (2), Down (18), Left (16), Right (20), Center (3).

### ☁️ 3. Persistence & Cloud Logic
*   **Local High Score**: Automatically saves/loads from `best_score.json` on the terminal.
*   **GCP Integration**: Uses `urequests` to sync the top players to a Google Cloud Firestore backend.

### 📖 4. Key Implementation Details

#### Screen Shake (Visual Juice)
```python
# Intensity set in config.py
ox = random.randint(-config.SHAKE_INTENSITY, config.SHAKE_INTENSITY)
oy = random.randint(-config.SHAKE_INTENSITY, config.SHAKE_INTENSITY)
display.blit(ox, oy, 240, 240, fbuf_data)
```

#### Parallax Stars
Background stars are stored in a list with unique `speed` properties, updated every frame to create a layered scrolling effect.

#### Collision Detection (AABB)
Standard Axis-Aligned Bounding Box collision checks for bullets, enemies, and power-ups.
