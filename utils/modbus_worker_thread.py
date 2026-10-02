import threading
import time
import struct
import wx

from pubsub import pub
from pymodbus.client import ModbusTcpClient

class BasePlcWorker(threading.Thread):
    """ Class dasar untuk mengelola koneksi Modbus TCP dan mekanisme Retry """
    def __init__(self, server_num, config=None, polling_interval=0.1): # Default 0.1s = 100ms
        super().__init__()
        self.daemon = True
        self.running = True
        self.server_num = server_num
        self.config = config or {}
        self.polling_interval = polling_interval

        self.attempts = 0
        self.status = "NOT CONNECTED"
        self.reconnect_flag = True
        self.client = None

    def trigger_reconnect(self):
        self.attempts = 0
        self.reconnect_flag = True
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None

    def update_config(self, new_config):
        self.config = new_config
        self.trigger_reconnect()

    def _check_connection_limit(self):
        if self.status == "NOT CONNECTED":
            if not self.reconnect_flag and self.attempts >= 3:
                return False
            self.status = "CONNECTING"
            self.attempts += 1
            self.reconnect_flag = False
            self._notify_status()
        return True

    def _notify_status(self):
        pub.sendMessage(f"modbus_status_plc{self.server_num}", status=self.status)

    def stop(self):
        self.running = False


class Plc1WorkerThread(BasePlcWorker):
    """ Thread khusus Polling High-Speed untuk PLC 1 """
    def __init__(self, config=None, polling_interval=0.1):
        super().__init__(server_num=1, config=config, polling_interval=polling_interval)

    def run(self):
        while self.running:
            start_time = time.perf_counter()

            data1 = self.process_plc1()
            
            # Broadcast status dan data
            self._notify_status()
            if data1 is not None:
                pub.sendMessage("modbus.data.plc1", data=data1)

            # Hitung sisa jeda agar interval pas (misal 100ms)
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0.001, self.polling_interval - elapsed)
            time.sleep(sleep_time)

        # Cleanup socket
        if self.client:
            self.client.close()

    def process_plc1(self):
        cfg = self.config.get("server1")
        if not cfg or not self._check_connection_limit():
            return None

        # Re-use socket connection
        if self.client is None or not self.client.is_socket_open():
            # Timeout dipercepat ke 0.5 detik agar UI tidak freeze lama saat disconnected
            self.client = ModbusTcpClient(cfg["ip"], port=cfg.get("port", 502), timeout=0.5)
            if not self.client.connect():
                self.status = "NOT CONNECTED"
                return None

        self.status = "CONNECTED"
        self.attempts = 0
        read_data = {}

        try:
            # 1. Discrete Inputs X7-X10
            res_x = self.client.read_discrete_inputs(address=7, count=4, slave=1)
            if not res_x.isError():
                bits = res_x.bits
                read_data["X7"] = not bits[0]
                read_data["X8"] = not bits[1]
                read_data["X9"] = not bits[2]
                read_data["X10"] = not bits[3]

            # 2. Coils Y0-Y1
            res_y = self.client.read_coils(address=1536, count=2, slave=1)
            if not res_y.isError():
                read_data["Y0"] = res_y.bits[0]
                read_data["Y1"] = res_y.bits[1]

            # 3. Internal Coils M1102-M1103
            res_m = self.client.read_coils(address=4174, count=2, slave=1)
            if not res_m.isError():
                read_data["M1102"] = res_m.bits[0]
                read_data["M1103"] = res_m.bits[1]

            # 4. Holding Register V32 (0x0220 / Addr 544)
            res_v32 = self.client.read_holding_registers(address=544, count=2, slave=1)
            if not res_v32.isError():
                # Dekode FLOAT 32-bit (BIG ENDIAN WORD, LITTLE ENDIAN BYTE)
                raw = struct.pack('>HH', res_v32.registers[1], res_v32.registers[0])
                read_data["V32"] = round(struct.unpack('<f', raw)[0], 2)

            # 5. Holding Register V124 (0x027C / Addr 636)
            res_v124 = self.client.read_holding_registers(address=636, count=2, slave=1)
            if not res_v124.isError():
                # Dekode UINT 32-bit
                raw = struct.pack('>HH', res_v124.registers[1], res_v124.registers[0])
                read_data["V124"] = struct.unpack('>I', raw)[0]

            # 6. OPTIMASI BATCH: Gabung V1004 (addr 1516) & V1032 (addr 1544) dalam 1 Request
            # Rentang 1516 ke 1545 = 30 register. Memangkas 1 network request terpisah.
            res_batch = self.client.read_holding_registers(address=1516, count=30, slave=1)
            if not res_batch.isError():
                regs = res_batch.registers
                
                # V1004 (Indeks 0 & 1 dalam buffer batch)
                raw_v1004 = struct.pack('>HH', regs[1], regs[0])
                read_data["V1004"] = struct.unpack('>I', raw_v1004)[0]

                # V1032 (Indeks 28 & 29 dalam buffer batch -> 1544 - 1516 = 28)
                raw_v1032 = struct.pack('>HH', regs[29], regs[28])
                read_data["V1032"] = round(struct.unpack('<f', raw_v1032)[0], 2)

        except Exception:
            self.status = "NOT CONNECTED"
            if self.client:
                self.client.close()
                self.client = None
            return None

        return read_data


class Plc2WorkerThread(BasePlcWorker):
    """ Thread khusus Polling High-Speed untuk PLC 2 """
    def __init__(self, config=None, polling_interval=0.1):
        super().__init__(server_num=2, config=config, polling_interval=polling_interval)

    def run(self):
        while self.running:
            start_time = time.perf_counter()

            data2 = self.process_plc2()
            
            # Broadcast status dan data
            self._notify_status()
            if data2 is not None:
                pub.sendMessage("modbus.data.plc2", data=data2)

            # Hitung sisa jeda agar interval pas (misal 100ms)
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0.001, self.polling_interval - elapsed)
            time.sleep(sleep_time)

        # Cleanup socket
        if self.client:
            self.client.close()

    def process_plc2(self):
        cfg = self.config.get("server2")
        if not cfg or not self._check_connection_limit():
            return None

        if self.client is None or not self.client.is_socket_open():
            self.client = ModbusTcpClient(cfg["ip"], port=cfg.get("port", 502), timeout=0.5)
            if not self.client.connect():
                self.status = "NOT CONNECTED"
                return None

        self.status = "CONNECTED"
        self.attempts = 0
        read_data = {}

        try:
            # Baca Aux Relay M3008 - M3016 (9 bit)
            res_m = self.client.read_coils(address=6080, count=9, slave=1)
            if not res_m.isError():
                bits = res_m.bits
                for i, m_addr in enumerate(range(3008, 3017)):
                    read_data[f"M{m_addr}"] = bits[i]

        except Exception:
            self.status = "NOT CONNECTED"
            if self.client:
                self.client.close()
                self.client = None
            return None

        return read_data


class ModbusManager:
    """ Wrapper class untuk mengendalikan kedua thread PLC dari UI wxPython """
    def __init__(self, config=None, polling_interval=0.1):
        self.config = config or {}
        self.polling_interval = polling_interval
        
        self.t1 = Plc1WorkerThread(self.config, self.polling_interval)
        self.t2 = Plc2WorkerThread(self.config, self.polling_interval)

    def start(self):
        self.t1.start()
        self.t2.start()

    def stop(self):
        self.t1.stop()
        self.t2.stop()

    def update_config(self, new_config):
        self.config = new_config
        self.t1.update_config(new_config)
        self.t2.update_config(new_config)

    def trigger_reconnect(self, server_num=None):
        if server_num == 1 or server_num is None:
            self.t1.trigger_reconnect()
        if server_num == 2 or server_num is None:
            self.t2.trigger_reconnect()