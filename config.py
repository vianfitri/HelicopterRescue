import json
import os

CONFIG_FILE = "modbus_config.json"

DEFAULT_CONFIG = {
    "server1": {
        "ip": "127.0.0.1",
        "port": 502,
        "holding_reg_1": 0,
        "holding_reg_2": 1,
        "coil_1_addr": 0,
        "coil_1_default": "NO",
        "coil_2_addr": 1,
        "coil_2_default": "NO",
        "di_1_addr": 0,
        "di_1_default": "NO",
        "di_2_addr": 1,
        "di_2_default": "NO",
        "di_out_1_addr": 0,
        "di_out_1_default": "NO",
        "di_out_2_addr": 1,
        "di_out_2_default": "NO",
    },
    "server2": {
        "ip": "127.0.0.1",
        "port": 503,
        "holding_reg_1": 0,
        "holding_reg_2": 1,
        "coil_1_addr": 0,
        "coil_1_default": "NO",
        "coil_2_addr": 1,
        "coil_2_default": "NO",
        "di_1_addr": 0,
        "di_1_default": "NO",
        "di_2_addr": 1,
        "di_2_default": "NO",
        "di_out_1_addr": 0,
        "di_out_1_default": "NO",
        "di_out_2_addr": 1,
        "di_out_2_default": "NO",
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