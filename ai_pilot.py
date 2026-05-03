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
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.9995
        self.actions = [0, 1, 2, 3] # 0: Stay, 1: Left, 2: Right, 3: Fire
        self.load_brain()

    def discretize(self, player_x, player_y, enemies, powerups):
        """
        Improved discretization with vertical relative awareness.
        """
        # Player X bin (8 bins)
        p_bin = player_x // 30
        
        # Default empty values
        ne_rel_x, ne_rel_y = 5, 5 # Out of range/Safe
        pu_dir = 0 # 0: None, 1: Left, 2: Right
        
        # Nearest Enemy (focus on what's closest and in front)
        if enemies:
            # Filter for enemies above or near player
            targets = [e for e in enemies if e['y'] < player_y + 20]
            if targets:
                nearest = min(targets, key=lambda e: abs(e['y'] - player_y) + abs(e['x'] - player_x))
                # Relative coordinates in bins of 40px
                ne_rel_x = (nearest['x'] - player_x) // 40
                ne_rel_y = (nearest['y'] - player_y) // 40
                
                # Clip to small range to keep state space manageable
                ne_rel_x = max(-3, min(3, ne_rel_x))
                ne_rel_y = max(-3, min(3, ne_rel_y))
            
        # Nearest Powerup
        if powerups:
            nearest_p = min(powerups, key=lambda p: abs(p['y'] - player_y))
            if nearest_p['x'] < player_x: pu_dir = 1
            elif nearest_p['x'] > player_x + 16: pu_dir = 2
            
        return (p_bin, ne_rel_x, ne_rel_y, pu_dir)

    def get_action(self, state):
        # Epsilon-Greedy with Decay
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
            
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
                    data = json.load(f)
                    # Faster manual parsing than eval()
                    self.q_table = {}
                    for k, v in data.items():
                        # Key format: "(p_bin, ne_x, ne_y, pu_dir)"
                        clean_k = k.strip("()").split(",")
                        state_tuple = tuple(int(x.strip()) for x in clean_k)
                        self.q_table[state_tuple] = v
                print(f"Loaded brain with {len(self.q_table)} states.")
        except Exception as e:
            print(f"Failed to load brain: {e}")
            self.q_table = {}

    def save_brain(self):
        """
        Atomic write with memory pruning.
        """
        try:
            # Prune brain if too large to prevent MemoryError on Pico
            if len(self.q_table) > 4000:
                print("Pruning brain memory...")
                # Keep states with highest absolute Q-values (importance)
                sorted_keys = sorted(self.q_table.keys(), 
                                    key=lambda k: max(abs(x) for x in self.q_table[k]), 
                                    reverse=True)
                self.q_table = {k: self.q_table[k] for k in sorted_keys[:3000]}

            temp_file = config.AI_BRAIN_FILE + ".tmp"
            data = {str(k): v for k, v in self.q_table.items()}
            with open(temp_file, 'w') as f:
                json.dump(data, f)
            if config.AI_BRAIN_FILE in os.listdir():
                os.remove(config.AI_BRAIN_FILE)
            os.rename(temp_file, config.AI_BRAIN_FILE)
            print(f"Brain saved: {len(self.q_table)} states.")
        except Exception as e:
            print(f"Failed to save brain: {e}")
