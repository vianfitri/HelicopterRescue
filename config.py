import json
import os

CONFIG_FILE = "modbus_config.json"

DEFAULT_CONFIG = {
    "server1": {
        "ip": "192.168.1.121",
        "port": 502
    },
    "server2": {
        "ip": "192.168.1.111",
        "port": 502
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False