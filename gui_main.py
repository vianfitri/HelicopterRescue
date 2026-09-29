import wx

from utils.modbus_worker0 import ModbusWorker

class ModbusFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None, 
            title="Modbus TCP PLC Monitor",
            size=(450, 400)
        )

        self.worker = None

        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # Configuration Input Form
        grid_sizer.Add(wx.StaticText(panel, label="IP Address PLC:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_ip = wx.TextCtrl(panel, value="127.0.0.1")
        grid_sizer.Add(self.txt_ip, 1, wx.EXPAND)
        
        grid_sizer.Add(wx.StaticText(panel, label="Port:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_port = wx.TextCtrl(panel, value="502")
        grid_sizer.Add(self.txt_port, 1, wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Slave ID:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_slave = wx.TextCtrl(panel, value="1")
        grid_sizer.Add(self.txt_slave, 1, wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Start Register Address"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_address = wx.TextCtrl(panel, value="0")
        grid_sizer.Add(self.txt_address, 1, wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Num Register:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_count = wx.TextCtrl(panel, value="5")
        grid_sizer.Add(self.txt_count, 1, wx.EXPAND)

        grid_sizer.AddGrowableCol(1, 1)

        # Control Button
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_connect = wx.Button(panel, label="Connect")
        self.btn_disconnect = wx.Button(panel, label="Disconnect")
        self.btn_disconnect.Disable()

        btn_sizer.Add(self.btn_connect, 1, wx.ALL, 5)
        btn_sizer.Add(self.btn_disconnect, 1, wx.ALL, 5)

        # Display Data & Status
        self.lbl_status = wx.StaticText(panel, label="Status:Idle")
        self.txt_data = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Layout Sizer
        main_sizer.Add(grid_sizer, 0, wx.ALL | wx.EXPAND, 15)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        main_sizer.Add(self.lbl_status, 0 , wx.ALL, 15)
        main_sizer.Add(self.txt_data, 1, wx.ALL | wx.EXPAND, 15)

        panel.SetSizer(main_sizer)

        # Binding Events
        self.btn_connect.Bind(wx.EVT_BUTTON, self.on_connect)
        self.btn_disconnect.Bind(wx.EVT_BUTTON, self.on_disconnect)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_connect(self, event):
        try:
            ip = self.txt_ip.GetValue().strip()
            port = int(self.txt_port.GetValue().strip())
            slave_id = int(self.txt_slave.GetValue().strip())
            start_addr = int(self.txt_address.GetValue().strip())
            count = int(self.txt_count.GetValue().strip())
        except ValueError:
            wx.MessageBox("Pastikan Port, Slave ID, Address, dan Count berupa angka!", "Error Input", wx.OK | wx.ICON_ERROR)
            return

        # Disable button to prevent multiple thread
        self.btn_connect.Disable()
        self.btn_disconnect.Enable()
        self.lbl_status.SetLabel("Status: Connecting...")

        # Running Modbus Worker in new Thread
        self.worker = ModbusWorker(
            host=ip,
            port=port,
            slave_id=slave_id,
            start_address=start_addr,
            count=count,
            update_callback=self.on_modbus_update,
            error_callback=self.on_modbus_error
        )

        self.worker.start()

    def on_disconnect(self, event):
        if self.worker:
            self.worker.stop()
            self.worker = None

        self.btn_connect.Enable()
        self.btn_disconnect.Disable()
        self.lbl_status.SetLabel("Status: Disconnected")

    def on_modbus_update(self, registers, status_msg):
        """Callback yang dipnggil dari thread worker via wx.CallAfter"""
        self.lbl_status.SetLabel(f"Status: {status_msg}")

        if registers is not None:
            #formatted_data = "\n".join([f"Register [{i + int(self.txt_address.GetValue())}]: {val}" for i, val in enumerate(registers)])
            #self.txt_data.SetValue(formatted_data)
            formatted_data = "\n".join([f"Input X[{i + int(self.txt_address.GetValue())}]: {'OFF (0)' if val else 'ON (1)'}" for i, val in enumerate(registers)])
            self.txt_data.SetValue(formatted_data)

    def on_modbus_error(self, error_msg):
        """ Callback saat terjadi error pada koneksi atau baca data"""
        self.lbl_status.SetLabel(f"Status: Error")
        self.txt_data.SetValue(f"ERROR: {error_msg}")
        self.on_disconnect(None)

    def on_close(self, event):
        # Hentikan worker thread jika jendela ditutup
        if self.worker:
            self.worker.stop()
        self.Destroy()

if __name__ == "__main__":
    app = wx.App()
    frame = ModbusFrame()
    frame.Show()
    app.MainLoop()