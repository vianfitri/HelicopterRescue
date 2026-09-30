import threading
import time
from pubsub import pub
from pymodbus.client import ModbusTcpClient


class ModbusWorkerThread(threading.Thread):
    def __init__(self, config=None):
        super().__init__()
        self.daemon = True
        self.running = True
        self.config = config or {}

        # Tracking state koneksi & percobaan (max 3x percobaan otomatis)
        self.s1_attempts = 0
        self.s2_attempts = 0
        self.s1_status = "NOT CONNECTED"
        self.s2_status = "NOT CONNECTED"

        # Flag retry koneksi manual
        self.s1_reconnect_flag = True
        self.s2_reconnect_flag = True

        # Persistent Modbus Client untuk menjaga koneksi tetap terbuka (mencegah socket overhead)
        self.client1 = None
        self.client2 = None

    def trigger_reconnect(self, server_num=None):
        """Memicu percobaan ulang koneksi secara manual (misal dari tombol UI)."""
        if server_num == 1 or server_num is None:
            self.s1_attempts = 0
            self.s1_reconnect_flag = True
            if self.client1:
                self.client1.close()
                self.client1 = None

        if server_num == 2 or server_num is None:
            self.s2_attempts = 0
            self.s2_reconnect_flag = True
            if self.client2:
                self.client2.close()
                self.client2 = None

    def update_config(self, new_config):
        """Update konfigurasi IP/Port dan pemicu koneksi ulang."""
        self.config = new_config
        self.trigger_reconnect()

    def run(self):
        while self.running:
            data1 = self.process_plc1()
            data2 = self.process_plc2()

            # Publish status koneksi global ke subscriber UI
            pub.sendMessage(
                "modbus.status",
                status1=self.s1_status,
                status2=self.s2_status
            )

            # Publish payload data spesifik jika polling berhasil
            if data1 is not None:
                pub.sendMessage("modbus.data.plc1", data=data1)

            if data2 is not None:
                pub.sendMessage("modbus.data.plc2", data=data2)

            time.sleep(1.0)

        # Cleanup socket saat thread dihentikan
        if self.client1:
            self.client1.close()
        if self.client2:
            self.client2.close()

    def _check_connection_limit(self, server_num):
        """Mengelola batas 3 kali percobaan koneksi otomatis."""
        status_attr = f"s{server_num}_status"
        attempts_attr = f"s{server_num}_attempts"
        reconnect_attr = f"s{server_num}_reconnect_flag"

        status = getattr(self, status_attr)
        attempts = getattr(self, attempts_attr)
        reconnect = getattr(self, reconnect_attr)

        if status == "NOT CONNECTED":
            if not reconnect and attempts >= 3:
                return False  # Hentikan retry otomatis, menunggu tombol manual UI
            setattr(self, status_attr, "CONNECTING")
            setattr(self, attempts_attr, attempts + 1)
            setattr(self, reconnect_attr, False)
            # Notify status "CONNECTING" secara instant
            pub.sendMessage("modbus.status", status1=self.s1_status, status2=self.s2_status)

        return True

    def process_plc1(self):
        cfg = self.config.get("server1")
        if not cfg or not self._check_connection_limit(1):
            return None

        # Re-use socket connection jika sudah terhubung
        if self.client1 is None or not self.client1.is_socket_open():
            self.client1 = ModbusTcpClient(cfg["ip"], port=cfg.get("port", 502), timeout=1.2)
            if not self.client1.connect():
                self.s1_status = "NOT CONNECTED"
                return None

        self.s1_status = "CONNECTED"
        self.s1_attempts = 0

        read_data = {}
        try:
            # 1. Baca Digital Inputs X (Modbus Function Code 02 - Discrete Inputs)
            # Haiwell Mapping: X0 (0x0000) s/d X10 (0x000A) -> Baca 11 bit sekaligus dalam 1 request
            res_x = self.client1.read_discrete_inputs(address=0, count=11)
            if not res_x.isError():
                bits = res_x.bits
                read_data.update({
                    "X0": bits[0], "X1": bits[1], "X7": bits[7],
                    "X8": bits[8], "X9": bits[9], "X10": bits[10]
                })

            # 2. Baca Digital Outputs Y (Modbus Function Code 01 - Coils)
            # Haiwell Mapping: Y8 (0x0008) s/d Y11 (0x000B) -> Baca 4 bit sekaligus
            res_y = self.client1.read_coils(address=8, count=4)
            if not res_y.isError():
                bits = res_y.bits
                read_data.update({
                    "Y8": bits[0], "Y9": bits[1], "Y10": bits[2], "Y11": bits[3]
                })

            # 3. Baca Registers V (Modbus Function Code 03 - Holding Registers)
            # V32 (0x0020) & V34 (0x0022)
            res_v32 = self.client1.read_holding_registers(address=32, count=3)
            if not res_v32.isError():
                read_data["V32"] = res_v32.registers[0]
                read_data["V34"] = res_v32.registers[2]

            # V102 (0x0066)
            res_v102 = self.client1.read_holding_registers(address=102, count=1)
            if not res_v102.isError():
                read_data["V102"] = res_v102.registers[0]

            # V1004 (0x03EC)
            res_v1004 = self.client1.read_holding_registers(address=1004, count=1)
            if not res_v1004.isError():
                read_data["V1004"] = res_v1004.registers[0]

        except Exception as e:
            self.s1_status = "NOT CONNECTED"
            if self.client1:
                self.client1.close()

        return read_data

    def process_plc2(self):
        cfg = self.config.get("server2")
        if not cfg or not self._check_connection_limit(2):
            return None

        if self.client2 is None or not self.client2.is_socket_open():
            self.client2 = ModbusTcpClient(cfg["ip"], port=cfg.get("port", 502), timeout=1.2)
            if not self.client2.connect():
                self.s2_status = "NOT CONNECTED"
                return None

        self.s2_status = "CONNECTED"
        self.s2_attempts = 0

        read_data = {}
        try:
            # Baca Aux Relays M3008 - M3016 (Modbus FC 01 - Coils)
            # Haiwell Mapping: M3008 (0x0BC0 / 3008) -> Baca 9 bit
            res_m = self.client2.read_coils(address=3008, count=9)
            if not res_m.isError():
                bits = res_m.bits
                for i, m_addr in enumerate(range(3008, 3017)):
                    read_data[f"M{m_addr}"] = bits[i]

        except Exception as e:
            self.s2_status = "NOT CONNECTED"
            if self.client2:
                self.client2.close()

        return read_data

    def stop(self):
        self.running = False