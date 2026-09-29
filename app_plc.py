import wx
import time
import threading
from pymodbus.client import ModbusTcpClient

class ModbusWorker(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.running = True
        self.daemon = True
        
        # Inisialisasi Klien Modbus
        self.plc1 = ModbusTcpClient("192.168.1.112", port=502, timeout=2)
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
            # BACA PLC 1 (192.168.1.112)
            # ==========================================
            if self.plc1.connect():
                data["plc1_connected"] = True
                try:
                    # Baca X7 - X10 (Discrete Inputs, Address 7, count 4) - Logika NC
                    rx = self.plc1.read_discrete_inputs(address=7, count=4)
                    if not rx.isError():
                        data["plc1_data"]["x7"] = not rx.bits[0]
                        data["plc1_data"]["x8"] = not rx.bits[1]
                        data["plc1_data"]["x9"] = not rx.bits[2]
                        data["plc1_data"]["x10"] = not rx.bits[3]

                    # Baca Y8 - Y11 (Coils, Address 8, count 4) - Logika NC
                    ry = self.plc1.read_coils(address=8, count=4)
                    if not ry.isError():
                        data["plc1_data"]["y8"] = not ry.bits[0]
                        data["plc1_data"]["y9"] = not ry.bits[1]
                        data["plc1_data"]["y10"] = not ry.bits[2]
                        data["plc1_data"]["y11"] = not ry.bits[3]

                    # Baca Holding Registers (V32, V102, V1004)
                    rv32 = self.plc1.read_holding_registers(address=32, count=1)
                    rv102 = self.plc1.read_holding_registers(address=102, count=1)
                    rv1004 = self.plc1.read_holding_registers(address=1004, count=1)
                    
                    if not rv32.isError(): data["plc1_data"]["v32"] = rv32.registers[0]
                    if not rv102.isError(): data["plc1_data"]["v102"] = rv102.registers[0]
                    if not rv1004.isError(): data["plc1_data"]["v1004"] = rv1004.registers[0]
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
                    # Baca M3008 - M3016 (Coils, Address 3008, count 9) - Asumsi NO (Normal)
                    rm = self.plc2.read_coils(address=3008, count=9)
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
        super().__init__(None, title="PLC Modbus TCP Monitor", size=(650, 550))
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
        self.lbl_status1 = wx.StaticText(panel, label="PLC 1 (192.168.1.112) - Terputus")
        self.lbl_status1.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox1.Add(self.lbl_status1, 0, wx.ALL, 10)

        # Daftar Boolean PLC 1 (NC)
        plc1_bools = [
            ("x7", "LS FWD 1 (X7, NC)"), ("x8", "LS FWD 2 (X8, NC)"),
            ("x9", "LS REV 1 (X9, NC)"), ("x10", "LS REV 2 (X10, NC)"),
            ("y8", "Indikator FWD (Y8, NC)"), ("y9", "Indikator REV (Y9, NC)"),
            ("y10", "Hoist UP (Y10, NC)"), ("y11", "Hoist DOWN (Y11, NC)")
        ]
        
        for key, label in plc1_bools:
            vbox1.Add(self.create_status_row(panel, key, label), 0, wx.EXPAND | wx.ALL, 5)

        vbox1.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Daftar Value PLC 1
        plc1_vals = [("v32", "RPM Value (V32)"), ("v102", "LOAD Value (V102)"), ("v1004", "Travel Value (V1004)")]
        for key, label in plc1_vals:
            vbox1.Add(self.create_value_row(panel, key, label), 0, wx.EXPAND | wx.ALL, 5)

        # ---- Kolom Kanan: PLC 2 ----
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        self.lbl_status2 = wx.StaticText(panel, label="PLC 2 (192.168.1.111) - Terputus")
        self.lbl_status2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox2.Add(self.lbl_status2, 0, wx.ALL, 10)

        plc2_bools = [
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
        hbox.Add(val, 0, wx.ALIGN_RIGHT)
        self.ui_elements[key] = val
        return hbox

    def create_value_row(self, panel, key, label_text):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(panel, label=label_text)
        val = wx.StaticText(panel, label="0")
        val.SetForegroundColour(wx.BLUE)
        
        hbox.Add(lbl, 1, wx.EXPAND)
        hbox.Add(val, 0, wx.ALIGN_RIGHT)
        self.ui_elements[key] = val
        return hbox

    def update_ui(self, data):
        """ Fungsi ini dipanggil secara thread-safe dari worker thread """
        
        # Update Status Koneksi PLC 1
        if data["plc1_connected"]:
            self.lbl_status1.SetLabel("PLC 1 (192.168.1.112) - TERHUBUNG")
            self.lbl_status1.SetForegroundColour(wx.Colour(0, 150, 0))
        else:
            self.lbl_status1.SetLabel("PLC 1 (192.168.1.112) - TERPUTUS")
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