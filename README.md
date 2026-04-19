# Pico 2W Space Shooter 🚀

A high-performance vertical space shooter for the Raspberry Pi Pico 2W with a cloud-based leaderboard.

![Hardware Setup](https://www.waveshare.com/w/upload/2/2f/Pico-LCD-1.3-1.jpg)

## Features
- **Fast 60 FPS Logic**: Optimized for the Pico 2W and the ST7789 display.
- **State Machine Architecture**: Clean separation between MENU, PLAYING, GAME_OVER, and LEADERBOARD states.
- **Double Buffering**: Flick-free rendering using MicroPython's `framebuf`.
- **Cloud Leaderboard**: Send and fetch high scores using Google Cloud Functions and Firestore.
- **Explosion Particles**: Smooth visual effects using custom particle system.

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
   - `CLOUD_SUBMIT_URL`: Your deployed GCP Function URL.
4. Upload `main.py`, `config.py`, and `st7789py.py` to your Pico using Thonny.

### 2. Google Cloud Setup (Backend)
1. **Firestore**: 
   - Create a Google Cloud Project.
   - Initialize Firestore in **Native Mode**.
   - Create a collection named `highscores`.
2. **Cloud Functions**:
   - Create a new **Cloud Run Function** (2nd Gen).
   - Set the runtime to **Python 3.10+**.
   - Use the code in `backend/main.py` and dependencies in `backend/requirements.txt`.
   - Set the Entry Point to `leaderboard_proxy`.
   - **Crucial**: Ensure the function has the `Cloud Datastore User` role for its Service Account so it can write to Firestore.
   - Allow **Unauthenticated invocations** (ingress: all) to make it publicly accessible for the Pico.

## Controls
- **Joystick**: Move ship
- **Key A**: Fire Bullet
- **Key B**: Start Game
- **Game Over**: Use Up/Down/Left/Right to enter your initials, then Key A to submit.

## License
MIT

---

## Technical Architecture & Walkthrough 👾

### 🎮 1. MicroPython Game Engine
The heart of the game is in `main.py`. It uses a **State Machine** to transition between states:
*   **MENU**: High-contrast title screen.
*   **PLAYING**: 60 FPS action with smooth input handling.
*   **GAME_OVER**: Interactive initials entry (A-Z) using the joystick.
*   **LEADERBOARD**: Displays the top 5 scores pulled from the cloud.

### 🔌 2. Hardware Configuration (`config.py`)
Hardware-specific constants are isolated here. I've pre-mapped all the pins for your Waveshare board:
*   **ST7789 Display**: High-speed SPI on Pins 10, 11, 9, 8.
*   **Input Buttons**: Map to your board's Key A, B, and directional joystick buttons.

### ☁️ 3. Google Cloud Backend (`backend/`)
Located in the `backend/` directory, these files are ready to deploy to GCP:
*   **Firestore**: Used as the database (NoSQL).
*   **Cloud Function**: A single Python entry point (`leaderboard_proxy`) that handles both score submission and leaderboard fetching.

### 📖 4. Key Implementation Details

#### Collision Detection (AABB)
```python
def check_collision(rect1, rect2):
    return (rect1["x"] < rect2["x"] + rect2["w"] and
            rect1["x"] + rect1["w"] > rect2["x"] and
            rect1["y"] < rect2["y"] + rect2["h"] and
            rect1["y"] + rect1["h"] > rect2["y"])
```

#### Double Buffering with FrameBuffer
To prevent "tearing" or flickering, the game renders to an off-screen buffer before sending the final frame to the display:
```python
# Initialization
fbuf_data = bytearray(config.DISPLAY_WIDTH * config.DISPLAY_HEIGHT * 2)
fb = framebuf.FrameBuffer(fbuf_data, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, framebuf.RGB565)

# Rendering (Inside main loop)
display.blit(0, 0, 240, 240, fbuf_data)
```
