import json
import random
import os
import config

class QPilot:
    def __init__(self):
        self.q_table = {}
        self.alpha = config.AI_ALPHA
        self.gamma = config.AI_GAMMA
        self.epsilon = config.AI_EPSILON
        self.actions = [0, 1, 2, 3] # 0: Stay, 1: Left, 2: Right, 3: Fire
        self.load_brain()

    def discretize(self, player_x, enemies, powerups):
        """
        Converts raw coordinates into a discrete state tuple.
        Returns: (player_bin, nearest_enemy_rel_x, nearest_enemy_rel_y, powerup_dir)
        """
        # Bins of size 30 pixels (8 bins for 240px)
        p_bin = player_x // 30
        
        # Default empty values
        ne_x, ne_y = 10, 10 # Out of range
        pu_dir = 0 # 0: None, 1: Left, 2: Right
        
        # Nearest Enemy
        if enemies:
            nearest = min(enemies, key=lambda e: e['y'] if e['y'] > 0 else 999)
            ne_x = (nearest['x'] - player_x) // 30
            ne_y = nearest['y'] // 30
            
        # Nearest Powerup
        if powerups:
            nearest_p = min(powerups, key=lambda p: p['y'])
            if nearest_p['x'] < player_x: pu_dir = 1
            elif nearest_p['x'] > player_x + 16: pu_dir = 2
            
        return (p_bin, ne_x, ne_y, pu_dir)

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
            
        # Return index of max Q-value
        m = max(self.q_table[state])
        return self.q_table[state].index(m)

    def learn(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0] * len(self.actions)
            
        old_val = self.q_table[state][action]
        next_max = max(self.q_table[next_state])
        
        # Q-Learning Formula
        new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
        self.q_table[state][action] = new_val

    def load_brain(self):
        try:
            if config.AI_BRAIN_FILE in os.listdir():
                with open(config.AI_BRAIN_FILE, 'r') as f:
                    # Convert keys back to tuples from strings
                    data = json.load(f)
                    self.q_table = {eval(k): v for k, v in data.items()}
                print(f"Loaded brain with {len(self.q_table)} states.")
        except Exception as e:
            print(f"Failed to load brain: {e}")
            self.q_table = {}

    def save_brain(self):
        """
        Atomic write using temporary file.
        """
        try:
            temp_file = config.AI_BRAIN_FILE + ".tmp"
            # Keys must be strings for JSON
            data = {str(k): v for k, v in self.q_table.items()}
            with open(temp_file, 'w') as f:
                json.dump(data, f)
            # Atomic swap
            if config.AI_BRAIN_FILE in os.listdir():
                os.remove(config.AI_BRAIN_FILE)
            os.rename(temp_file, config.AI_BRAIN_FILE)
            print(f"Brain saved: {len(self.q_table)} states.")
        except Exception as e:
            print(f"Failed to save brain: {e}")
