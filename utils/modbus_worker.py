import threading
import time
import wx

from pubsub import pub
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

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
    def __init__(self, config=None):
        super().__init__()
        self.daemon = True
        self.running = True
        self.config = config or {}

        # State koneksi
        self.s1_attempts = 0
        self.s2_attempts = 0
        self.s1_status = "NOT CONNECTED"
        self.s2_status = "NOT CONNECTED"
        
        # Trigger re-connect manual
        self.s1_reconnect_flag = True
        self.s2_reconnect_flag = True

        # Persistent Modbus Client untuk menjaga koneksi tetap terbuka (mencegah socket overhead)
        self.client1 = None
        self.client2 = None

    def trigger_reconnect(self, server_num=None):
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
        self.config = new_config
        self.trigger_reconnect()

    def run(self):
        while self.running:
            data1 = self.process_plc1()
            data2 = self.process_plc2()

            # Publish status koneksi global ke subscriber UI
            pub.sendMessage(
                "modbus_status",
                status1 = self.s1_status,
                status2 = self.s2_status
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
        """ Mengelola batas 3 kali percobaan koneksi otomatis """
        status_attr = f"s{server_num}_status"
        attempts_attr = f"s{server_num}_attempts"
        reconnect_attr = f"s{server_num}_reconnect_flag"

        status = getattr(self, status_attr)
        attempts = getattr(self, attempts_attr)
        reconnect = getattr(self, reconnect_attr)

        if status == "NOT CONNECTED":
            if not reconnect and attempts >= 3:
                return False # Hentikan retry otomatis, menunggu tombol manual UI
            setattr(self, status_attr, "CONNECTING")
            setattr(self, attempts_attr, attempts + 1)
            setattr(self, reconnect_attr, False)

            # Notify status "CONNECTING" secara instant
            pub.sendMessage(
                "modbus.status", 
                status1=self.s1_status, 
                status2=self.s2_status
            )

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
            # 1. Baca Digital Input X (Modbus Function Code 02 - Discrete Inputs)
            # Haiwell Mapping: X7 (0x0007) s/d X10 (0x000A) -> Baca 4 bit sekaligus dalam 1 request
            res_x = self.client1.read_discrete_inputs(address=7, count=4, slave=1)

            if not res_x.isError():
                bits = res_x.bits
                read_data.update({
                    "X7": not bits[0],
                    "X8": not bits[1],
                    "X9": not bits[2],
                    "X10": not bits[3]
                })

            # 2. Baca Digital Output Y (Modbus Function Code 01 - Coils)
            # Haiwell Mapping: Y0 (0x0600) s/d Y1 (0x0601) -> Baca 2 bit sekaligus
            res_y = self.client1.read_coils(address=1536, count=2, slave=1)

            if not res_y.isError():
                bits = res_y.bits
                read_data.update({
                    "Y0": bits[0],
                    "Y1": bits[1]
                })

            # 3. Baca Internal Coils M (Modbus Function Code 01 - Coils)
            # Haiwell Mapping: M1102 (0x104E) s/d M1103 (0x104F) -> Baca 2 bit sekaligus
            res_m = self.client1.read_coils(address=4174, count=2, slave=1)

            if not res_m.isError():
                bits = res_m.bits
                read_data.update({
                    "M1102": bits[0],
                    "M1103": bits[1]
                })

            # 4. Baca Holding Register V (Modbus Function Code 03 - Holding Registers)
            # Haiwell Mapping: V32 (0x0220) -> Baca 2 register sekaligus untuk 32-bit data
            res_v32 = self.client1.read_holding_registers(address=544, count=2, slave=1)

            if not res_v32.isError():
                decoder = BinaryPayloadDecoder.fromRegisters(
                    res_v32.registers,
                    byteorder=Endian.BIG,
                    wordorder=Endian.LITTLE
                )
                read_data["V32"] = round(decoder.decode_32bit_float(), 2)

            # Haiwell Mapping: V124 (0x027C) -> Baca 2 register sekaligus
            res_v124 = self.client1.read_holding_registers(address=636, count=2, slave=1)

            if not res_v124.isError():
                decoder = BinaryPayloadDecoder.fromRegisters(
                    res_v124.registers,
                    byteorder=Endian.BIG,
                    wordorder=Endian.LITTLE
                )
                read_data["V124"] = decoder.decode_32bit_uint()

            # Haiwell Mapping: V1004 (0x05EC) -> Baca 2 register sekaligus
            res_v1004 =self.client1.read_holding_registers(address=1516, count=2, slave=1)

            if not res_v1004.isError():
                decoder = BinaryPayloadDecoder.fromRegisters(
                    res_v1004.registers,
                    byteorder=Endian.BIG,
                    wordorder=Endian.LITTLE
                )
                read_data["V1004"] = decoder.decode_32bit_uint()

            # Haiwell Mapping: V1032 (0x0608) -> Baca 2 register sekaligus
            res_v1032 = self.client1.read_holding_registers(address=1544, count=2, slave=1)

            if not res_v1032.isError():
                decoder = BinaryPayloadDecoder.fromRegisters(
                    res_v1032.registers,
                    byteorder=Endian.BIG,
                    wordorder=Endian.LITTLE
                )
                read_data["V1032"] = round(decoder.decode_32bit_float(), 2)

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
            # Baca Aux Relay M3008 - M3016 (Modbus FC 01 - Coils)
            # Haiwell Mapping: M3008 (0x17C0) s/d M3016 (0x17C8) -> Baca 9 bit sekaligus
            res_m = self.client2.read_coils(address=6080, count=9, slave=1)

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