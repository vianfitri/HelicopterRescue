import wx
import time
import threading
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

class ModbusWorker(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.running = True
        self.daemon = True
        
        # Inisialisasi Klien Modbus
        self.plc1 = ModbusTcpClient("192.168.1.121", port=502, timeout=2)
        self.plc2 = ModbusTcpClient("192.168.1.111", port=502, timeout=2)

    def run(self):
        while self.running:
            data = {
                "plc1_connected": False,
                "plc2_connected": False,
                "plc1_data": {},
                "plc2_data": {}
            }

            # ==========================================
            # BACA PLC 1 (192.168.1.121)
            # ==========================================
            if self.plc1.connect():
                data["plc1_connected"] = True
                try:
                    # Baca X7 - X10 (Discrete Inputs, Address 7, count 4) - Logika NC
                    rx = self.plc1.read_discrete_inputs(address=7, count=4, slave=1)
                    if not rx.isError():
                        data["plc1_data"]["x7"] = not rx.bits[0]
                        data["plc1_data"]["x8"] = not rx.bits[1]
                        data["plc1_data"]["x9"] = not rx.bits[2]
                        data["plc1_data"]["x10"] = not rx.bits[3]

                    # Baca Y8 - Y11 (Coils, Address 8, count 4) - Logika NC
                    ry = self.plc1.read_coils(address=1536, count=22, slave=1)
                    if not ry.isError():
                        data["plc1_data"]["y0"] = ry.bits[0] # FWD
                        data["plc1_data"]["y1"] = ry.bits[1] # REV
                        data["plc1_data"]["y2"] = ry.bits[2]
                        data["plc1_data"]["y3"] = ry.bits[3]
                        data["plc1_data"]["y4"] = ry.bits[4]
                        data["plc1_data"]["y5"] = ry.bits[5]
                        data["plc1_data"]["y6"] = ry.bits[6]
                        data["plc1_data"]["y7"] = ry.bits[7]
                        data["plc1_data"]["y8"] = ry.bits[8]
                        data["plc1_data"]["y9"] = ry.bits[9]
                        data["plc1_data"]["y10"] = ry.bits[10]
                        data["plc1_data"]["y11"] = ry.bits[11]
                        data["plc1_data"]["y12"] = ry.bits[12]
                        data["plc1_data"]["y13"] = ry.bits[13]
                        data["plc1_data"]["y14"] = ry.bits[14]
                        data["plc1_data"]["y15"] = ry.bits[15]
                        data["plc1_data"]["y16"] = ry.bits[16]
                        data["plc1_data"]["y17"] = ry.bits[17]
                        data["plc1_data"]["y18"] = ry.bits[18]
                        data["plc1_data"]["y19"] = ry.bits[19]
                        data["plc1_data"]["y20"] = ry.bits[20]
                        data["plc1_data"]["y21"] = ry.bits[21]

                    # Baca M Register
                    rm = self.plc1.read_coils(address=(1102+3072), count=2, slave=1)
                    if not rm.isError():
                        data["plc1_data"]["m1102"] = rm.bits[0]
                        data["plc1_data"]["m1103"] = rm.bits[1]

                    rm = self.plc1.read_coils(address=(22+3072), count=2, slave=1)
                    if not rm.isError():
                        data["plc1_data"]["m22"] = rm.bits[0]
                        data["plc1_data"]["m23"] = rm.bits[1]

                    # Baca Holding Registers (V32, V102, V1004)
                    rv32 = self.plc1.read_holding_registers(address=(512+32), count=2, slave=1)
                    rv124 = self.plc1.read_holding_registers(address=(512+124), count=2, slave=1)
                    rv1004 = self.plc1.read_holding_registers(address=(512+1004), count=2, slave=1)
                    rv1032 = self.plc1.read_holding_registers(address=(512+1032), count=2, slave=1)
                    
                    if not rv32.isError():
                        decoder = BinaryPayloadDecoder.fromRegisters(
                            rv32.registers,
                            byteorder=Endian.BIG,
                            wordorder=Endian.LITTLE
                        )
                        data["plc1_data"]["v32"] = round(decoder.decode_32bit_float(), 2)
                    if not rv124.isError(): 
                        decoder = BinaryPayloadDecoder.fromRegisters(
                            rv124.registers,
                            byteorder=Endian.BIG,
                            wordorder=Endian.LITTLE
                        )
                        data["plc1_data"]["v124"] = decoder.decode_32bit_uint()
                    if not rv1004.isError(): 
                        decoder = BinaryPayloadDecoder.fromRegisters(
                            rv1004.registers,
                            byteorder=Endian.BIG,
                            wordorder=Endian.LITTLE
                        )
                        data["plc1_data"]["v1004"] = decoder.decode_32bit_uint()
                    if not rv1032.isError():
                        decoder = BinaryPayloadDecoder.fromRegisters(
                            rv1032.registers,
                            byteorder=Endian.BIG,
                            wordorder=Endian.LITTLE
                        )
                        data["plc1_data"]["v1544"] = round(decoder.decode_32bit_float(), 2)
                except Exception as e:
                    print("Error reading PLC 1:", e)
            else:
                self.plc1.close()

            # ==========================================
            # BACA PLC 2 (192.168.1.111)
            # ==========================================
            if self.plc2.connect():
                data["plc2_connected"] = True
                try:
                    ry = self.plc2.read_coils(address=1542, count=10, slave=1) #1536+6=1542
                    if not ry.isError():
                        data["plc2_data"]["y6"] = ry.bits[0]
                        data["plc2_data"]["y7"] = ry.bits[1]
                        data["plc2_data"]["y8"] = ry.bits[2]
                        data["plc2_data"]["y9"] = ry.bits[3]
                        data["plc2_data"]["y10"] = ry.bits[4]
                        data["plc2_data"]["y11"] = ry.bits[5]
                        data["plc2_data"]["y12"] = ry.bits[6]
                        data["plc2_data"]["y14"] = ry.bits[8]
                        data["plc2_data"]["y15"] = ry.bits[9]

                    # Baca M3008 - M3016 (Coils, Address 3008, count 9) - Asumsi NO (Normal)
                    rm = self.plc2.read_coils(address=6080, count=9, slave=1)
                    if not rm.isError():
                        data["plc2_data"]["m3008"] = rm.bits[0]
                        data["plc2_data"]["m3009"] = rm.bits[1]
                        data["plc2_data"]["m3010"] = rm.bits[2]
                        data["plc2_data"]["m3011"] = rm.bits[3]
                        data["plc2_data"]["m3012"] = rm.bits[4]
                        data["plc2_data"]["m3013"] = rm.bits[5]
                        data["plc2_data"]["m3014"] = rm.bits[6]
                        data["plc2_data"]["m3015"] = rm.bits[7]
                        data["plc2_data"]["m3016"] = rm.bits[8]
                except Exception as e:
                    print("Error reading PLC 2:", e)
            else:
                self.plc2.close()

            # Kirim data ke GUI menggunakan thread-safe wx.CallAfter
            wx.CallAfter(self.callback, data)

            # Polling delay
            time.sleep(0.5)

    def stop(self):
        self.running = False
        self.plc1.close()
        self.plc2.close()


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="PLC Modbus TCP Monitor", size=(650, 700))
        self.ui_elements = {}
        self.init_ui()
        self.Center()
        
        # Mulai Worker Thread
        self.worker = ModbusWorker(self.update_ui)
        self.worker.start()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # ---- Kolom Kiri: PLC 1 ----
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        self.lbl_status1 = wx.StaticText(panel, label="PLC 1 (192.168.1.121) - Terputus")
        self.lbl_status1.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox1.Add(self.lbl_status1, 0, wx.ALL, 10)

        # Daftar Boolean PLC 1 (NC)
        plc1_bools = [
            ("x7", "LS FWD 1 (X7, NC)"), ("x8", "LS FWD 2 (X8, NC)"),
            ("x9", "LS REV 1 (X9, NC)"), ("x10", "LS REV 2 (X10, NC)"),
            ("y0", "Y0"), ("y1","Y1"),
            ("m1102", "Hoist UP (M1102)"),("m1103","Hoist DOWN (M1103)"),
            ("m22", "Forward (M22)"),("m23", "Reverse (M23)")
        ]
        
        for key, label in plc1_bools:
            vbox1.Add(self.create_status_row(panel, key, label), 0, wx.EXPAND | wx.ALL, 5)

        vbox1.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Daftar Value PLC 1
        plc1_vals = [("v32", "RPM Value (V32)"), ("v124", "Hoist Travel Value (V124)"), ("v1004", "Travel Value (V1004)"), ("v1544", "LOAD Value (V1544)")]
        for key, label in plc1_vals:
            vbox1.Add(self.create_value_row(panel, key, label), 0, wx.EXPAND | wx.ALL, 5)

        # ---- Kolom Kanan: PLC 2 ----
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        self.lbl_status2 = wx.StaticText(panel, label="PLC 2 (192.168.1.111) - Terputus")
        self.lbl_status2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox2.Add(self.lbl_status2, 0, wx.ALL, 10)

        plc2_bools = [
            ("y6", "DOWNWASH LOW (Y6)"), ("y7", "DOWNWASH HIGH (Y7)"),
            ("y8", "WAVE 1 (Y8)"), ("y9", "WAVE 2 (Y9)"),
            ("y10", "Rain Slight (Y10)"), ("y11", "Rain Moderate (Y11)"),
            ("y12", "Rain Heavy (Y12)"), ("y14", "Wind Low (Y14)"),
            ("y15", "Wind High (Y15)"),
            ("m3008", "DOWNWASH LOW (M3008)"), ("m3009", "DOWNWASH HIGH (M3009)"),
            ("m3010", "WAVE 1 (M3010)"), ("m3011", "WAVE 2 (M3011)"),
            ("m3012", "Rain Slight (M3012)"), ("m3013", "Rain Moderate (M3013)"),
            ("m3014", "Rain Heavy (M3014)"), ("m3015", "Wind Low (M3015)"),
            ("m3016", "Wind High (M3016)")
        ]

        for key, label in plc2_bools:
            vbox2.Add(self.create_status_row(panel, key, label), 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(vbox1, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(wx.StaticLine(panel, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(vbox2, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(main_sizer)

    def create_status_row(self, panel, key, label_text):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(panel, label=label_text)
        val = wx.StaticText(panel, label="OFF")
        val.SetForegroundColour(wx.Colour(150, 150, 150)) # Abu-abu saat off/error
        
        hbox.Add(lbl, 1, wx.EXPAND)
        hbox.Add(val, 0, wx.EXPAND)
        self.ui_elements[key] = val
        return hbox

    def create_value_row(self, panel, key, label_text):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(panel, label=label_text)
        val = wx.StaticText(panel, label="0")
        val.SetForegroundColour(wx.BLUE)
        
        hbox.Add(lbl, 1, wx.EXPAND)
        hbox.Add(val, 0, wx.EXPAND)
        self.ui_elements[key] = val
        return hbox

    def update_ui(self, data):
        """ Fungsi ini dipanggil secara thread-safe dari worker thread """
        
        # Update Status Koneksi PLC 1
        if data["plc1_connected"]:
            self.lbl_status1.SetLabel("PLC 1 (192.168.1.121) - TERHUBUNG")
            self.lbl_status1.SetForegroundColour(wx.Colour(0, 150, 0))
        else:
            self.lbl_status1.SetLabel("PLC 1 (192.168.1.121) - TERPUTUS")
            self.lbl_status1.SetForegroundColour(wx.RED)

        # Update Status Koneksi PLC 2
        if data["plc2_connected"]:
            self.lbl_status2.SetLabel("PLC 2 (192.168.1.111) - TERHUBUNG")
            self.lbl_status2.SetForegroundColour(wx.Colour(0, 150, 0))
        else:
            self.lbl_status2.SetLabel("PLC 2 (192.168.1.111) - TERPUTUS")
            self.lbl_status2.SetForegroundColour(wx.RED)

        # Update Widget UI PLC 1
        for key, value in data["plc1_data"].items():
            widget = self.ui_elements.get(key)
            if widget:
                if isinstance(value, bool):  # Untuk limit switch & indikator
                    if value:
                        widget.SetLabel("ON")
                        widget.SetForegroundColour(wx.GREEN)
                    else:
                        widget.SetLabel("OFF")
                        widget.SetForegroundColour(wx.RED)
                else:  # Untuk register value (V)
                    widget.SetLabel(str(value))

        # Update Widget UI PLC 2
        for key, value in data["plc2_data"].items():
            widget = self.ui_elements.get(key)
            if widget:
                if value:
                    widget.SetLabel("ON")
                    widget.SetForegroundColour(wx.GREEN)
                else:
                    widget.SetLabel("OFF")
                    widget.SetForegroundColour(wx.RED)

    def on_close(self, event):
        self.worker.stop()
        self.Destroy()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()