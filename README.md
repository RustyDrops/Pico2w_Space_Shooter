# Pico 2W Space Shooter (Roguelite High-Performance Edition) 🚀

A vertically scrolling space shooter optimized for the **Raspberry Pi Pico 2W (RP2350)**, featuring meta-progression and a sentient Q-Learning AI pilot.

## 🚀 Performance & Hardware
- **Dynamic Overclocking:** The RP2350 runs at **150MHz** during manual play and automatically ramps up to **250MHz** when the AI Pilot is engaged to handle intensive RL calculations.
- **Dedicated Rendering (Dual Core):** Pixel pushing is offloaded to the second CPU core (`_thread`), keeping the game logic at a locked **60FPS**.
- **62.5MHz SPI:** Ultra-fast display communication reduces frame latency.
- **ST7789 Optimized:** Native Big-Endian sprite rendering ensures vibrant, correct colors on the Waveshare 1.3" LCD.

## 🧠 Advanced Q-Learning AI
The standalone `ai_pilot.py` agent learns to play the game on-device using Tabular Reinforcement Learning.
- **Reward Shaping:** The AI is rewarded for aggressive positioning (lining up shots) and penalized for "Wall Hugging" or unnecessary movement.
- **Relative State Space:** The AI "sees" threats relative to its own position (Vertical and Horizontal), allowing for more tactical dodging.
- **Epsilon Decay:** The pilot starts by exploring randomly but slowly transitions to "Expert Mode" as it decays its exploration rate.
- **Brain Pruning:** Intelligent memory management keeps the Q-Table within the Pico's RAM limits by discarding low-priority states.
- **Fast Loader:** Custom string-to-tuple parsing for brain persistence, avoiding the high overhead of `eval()`.

## 🛠️ Meta-Progression & Gameplay
- **Scrap Currency:** Enemies drop scrap ($) upon destruction. Higher combo multipliers yield significantly more currency.
- **The Hangar (Shop):** Spend scrap on permanent upgrades that persist across all game sessions:
    - **Engine:** Increases ship speed and maneuverability.
    - **Cannons:** Boosts fire rate for high-density combat.
    - **Armor:** Increases defensive capabilities for deep space sectors.
- **Sector System:** Progress through increasingly difficult "Sectors" every 10,000 points. Enemies become tougher, but scrap rewards increase.
- **Persistence:** All progress, upgrades, and high scores are saved locally to `save_data.json`.

## 🕹️ Controls
### Main Menu
- **Button A:** Start Mission
- **Button B:** Enter Hangar (Shop)

### Hangar (Shop)
- **Joystick Up:** Upgrade Engine
- **Joystick Down:** Upgrade Cannons
- **Button A:** Upgrade Armor
- **Button B:** Return to Menu

### Gameplay
- **Joystick:** Move Ship
- **Button A:** Primary Fire
- **Joystick Center:** Toggle AI Autopilot (Safety Menu)

## 🔧 Installation
1. Flash your Pico 2W with the latest MicroPython firmware.
2. Upload all `.py` files to the root directory.
3. Configure Wi-Fi in `config.py` if using cloud leaderboards.
4. Run `main.py`.

---
*Optimized for the RP2350 architecture.*
