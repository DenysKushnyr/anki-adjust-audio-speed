from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer
from aqt.sound import av_player, MpvManager
from aqt.qt import QShortcut, Qt
from aqt.utils import tooltip
import json
import os

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "config.json")
default_config = {"speed_step": 0.25, "reset_speed": 1.0, "last_speed": 1.0}
try:
    with open(config_path, "r") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = default_config
    with open(config_path, "w") as f:
        json.dump(config, f)

def save_config():
    with open(config_path, "w") as f:
        json.dump(config, f)

def adjust_speed(delta):
    player = next((p for p in av_player.players if isinstance(p, MpvManager)), None)
    if not player:
        return

    current_speed = player.get_property("speed")
    new_speed = max(0.5, min(3.0, current_speed + delta))
    player.set_property("speed", new_speed)
    tooltip(f"Speed: {new_speed:.2f}x", period=2000) 
    config["last_speed"] = new_speed 
    save_config()

def reset_speed():
    player = next((p for p in av_player.players if isinstance(p, MpvManager)), None)
    if player:
        player.set_property("speed", config["reset_speed"])
        tooltip(f"Speed: {config['reset_speed']}x", period=2000)
        config["last_speed"] = config["reset_speed"]
        save_config()

# Add keyboard shortcuts
def add_shortcuts(reviewer: Reviewer):
    QShortcut(Qt.Key.Key_BracketLeft, mw, activated=lambda: adjust_speed(-config["speed_step"]))
    QShortcut(Qt.Key.Key_BracketRight, mw, activated=lambda: adjust_speed(config["speed_step"]))
    QShortcut(Qt.Key.Key_Backslash, mw, activated=reset_speed)

def load_saved_speed():
    player = next((p for p in av_player.players if isinstance(p, MpvManager)), None)
    if player:
        player.set_property("speed", config["last_speed"])
        tooltip(f"Loaded speed: {config['last_speed']:.1f}x", period=1000)

gui_hooks.profile_did_open.append(load_saved_speed)
gui_hooks.reviewer_did_init.append(add_shortcuts)
