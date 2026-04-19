import json
import os
import sys

# Paths - These should be adjusted by AnnIs if the game is in a subfolder
CONFIG_PATH = "config.py"
REPORT_PATH = "pilot_report.json"
COMMAND_PATH = "cmd_bridge.txt"

def get_debrief():
    """
    Returns a tiny text summary for the LLM to read.
    Saves tokens by translating JSON into a dense string.
    """
    try:
        if REPORT_PATH in os.listdir():
            with open(REPORT_PATH, "r") as f:
                d = json.load(f)
                return f"Pilot {d['res']}. Score: {d['scr']}. Kills: {d['kil']}. States Known: {d['states']}."
        return "No pilot report found. Start training first."
    except Exception as e:
        return f"Error reading report: {e}"

def optimize_pilot(style="balanced"):
    """
    Adjusts ALPHA and EPSILON in config.py.
    Styles: 'aggressive', 'safe', 'balanced'
    """
    params = {
        "aggressive": {"alpha": 0.2, "epsilon": 0.4},
        "safe": {"alpha": 0.05, "epsilon": 0.05},
        "balanced": {"alpha": 0.1, "epsilon": 0.2}
    }
    
    target = params.get(style.lower(), params["balanced"])
    
    try:
        with open(CONFIG_PATH, "r") as f:
            lines = f.readlines()
            
        new_lines = []
        for line in lines:
            if "AI_ALPHA =" in line:
                new_lines.append(f"AI_ALPHA = {target['alpha']}             # Updated by AnnIs Coach\n")
            elif "AI_EPSILON =" in line:
                new_lines.append(f"AI_EPSILON = {target['epsilon']}           # Updated by AnnIs Coach\n")
            else:
                new_lines.append(line)
                
        # Atomic write
        with open(CONFIG_PATH + ".tmp", "w") as f:
            for line in new_lines:
                f.write(line)
        os.remove(CONFIG_PATH)
        os.rename(CONFIG_PATH + ".tmp", CONFIG_PATH)
        return f"Pilot optimized for {style} style."
    except Exception as e:
        return f"Optimization failed: {e}"

def launch_training_session():
    """
    Signals the game to start the sentient pilot.
    Uses a command file bridge for cross-process communication.
    """
    try:
        with open(COMMAND_PATH, "w") as f:
            f.write("AUTOPILOT_ON\n")
        return "Training session signal sent."
    except Exception as e:
        return f"Launch failed: {e}"

def stop_training_and_save():
    """
    Signals the game to stop and save the brain.
    """
    try:
        with open(COMMAND_PATH, "w") as f:
            f.write("SAVE_BRAIN\n")
        return "Save signal sent to pilot."
    except Exception as e:
        return f"Save command failed: {e}"
