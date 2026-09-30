import threading
import time
import wx


from pymodbus.client import ModbusTcpClient

# Event kustom untuk mengirimkan data dan status ke Thread UI
EVT_MODBUS_DATA_ID = wx.NewIdRef()

class ModbusDataEvent(wx.PyEvent):
    def __init__(self, status1, data1, status2, data2):
        super().__init__()
        self.SetEventType(EVT_MODBUS_DATA_ID)
        self.status1 = status1  # 'CONNECTED', 'CONNECTING', 'NOT CONNECTED'
        self.data1 = data1
        self.status2 = status2
        self.data2 = data2

class ModbusWorkerThread(threading.Thread):
    def __init__(self, notify_window, config):
        super().__init__()
        self.notify_window = notify_window
        self.config = config
        self.daemon = True
        self.running = True

        # State koneksi
        self.s1_attempts = 0
        self.s2_attempts = 0
        self.s1_status = "NOT CONNECTED"
        self.s2_status = "NOT CONNECTED"
        
        # Trigger re-connect manual
        self.s1_reconnect_flag = True
        self.s2_reconnect_flag = True

    def trigger_reconnect(self, server_num=None):
        if server_num == 1 or server_num is None:
            self.s1_attempts = 0
            self.s1_reconnect_flag = True
        if server_num == 2 or server_num is None:
            self.s2_attempts = 0
            self.s2_reconnect_flag = True

    def update_config(self, new_config):
        self.config = new_config
        self.trigger_reconnect()

    def run(self):
        while self.running:
            data1 = self.process_server("server1", 1)
            data2 = self.process_server("server2", 2)

            # Kirim status & data hasil polling ke UI secara aman
            wx.PostEvent(
                self.notify_window,
                ModbusDataEvent(self.s1_status, data1, self.s2_status, data2)
            )
            time.sleep(1.0)

    def process_server(self, server_key, server_num):
        cfg = self.config[server_key]
        ip = cfg["ip"]
        port = cfg["port"]

        status_attr = f"s{server_num}_status"
        attempts_attr = f"s{server_num}_attempts"
        reconnect_attr = f"s{server_num}_reconnect_flag"

        current_status = getattr(self, status_attr)
        current_attempts = getattr(self, attempts_attr)
        reconnect_flag = getattr(self, reconnect_attr)

        # Logika pembatasan max 3 kali percobaan
        if current_status == "NOT CONNECTED":
            if not reconnect_flag and current_attempts >= 3:
                return None
            
            setattr(self, status_attr, "CONNECTING")
            setattr(self, attempts_attr, current_attempts + 1)
            setattr(self, reconnect_attr, False)

        # Mencoba koneksi Modbus TCP
        client = ModbusTcpClient(ip, port=port, timeout=1.2)
        connected = False
        try:
            connected = client.connect()
        except Exception:
            connected = False

        if not connected:
            setattr(self, status_attr, "NOT CONNECTED")
            client.close()
            return None

        setattr(self, status_attr, "CONNECTED")
        setattr(self, attempts_attr, 0)

        # Polling Data Register
        read_data = {}
        try:
            # 2 Holding Registers
            hr = client.read_holding_registers(cfg["holding_reg_1"], count=2)
            read_data["hr1"] = hr.registers[0] if not hr.isError() else "Err"
            read_data["hr2"] = hr.registers[1] if not hr.isError() else "Err"

            # 2 Coils
            c1 = client.read_coils(cfg["coil_1_addr"], count=1)
            c2 = client.read_coils(cfg["coil_2_addr"], count=1)
            read_data["coil1"] = (c1.bits[0] if not c1.isError() else False)
            read_data["coil2"] = (c2.bits[0] if not c2.isError() else False)

            # 2 Discrete Inputs
            di1 = client.read_discrete_inputs(cfg["di_1_addr"], count=1)
            di2 = client.read_discrete_inputs(cfg["di_2_addr"], count=1)
            read_data["di1"] = (di1.bits[0] if not di1.isError() else False)
            read_data["di2"] = (di2.bits[0] if not di2.isError() else False)

            # 2 Discrete Outputs
            do1 = client.read_coils(cfg["di_out_1_addr"], count=1)
            do2 = client.read_coils(cfg["di_out_2_addr"], count=1)
            read_data["do1"] = (do1.bits[0] if not do1.isError() else False)
            read_data["do2"] = (do2.bits[0] if not do2.isError() else False)

        except Exception as e:
            print(f"Error reading server {server_num}: {e}")

        client.close()
        return read_data

    def stop(self):
        self.running = False