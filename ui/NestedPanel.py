import wx
from pubsub import pub

class DeepNestedStatusPanel(wx.Panel):
    """Contoh komponen UI yang berada sangat dalam di hirarki aplikasi."""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.status_label = wx.StaticText(self, label="Status PLC1: UNKNOWN | PLC2: UNKNOWN")
        self.reconnect_btn = wx.Button(self, label="Reconnect PLC1 Manual")
        self.reconnect_btn.Bind(wx.EVT_BUTTON, self.on_reconnect)

        # 1. Subscribe ke Topik Status Koneksi
        pub.subscribe(self.on_status_update, "modbus.status")
        
        # 2. Subscribe ke Topik Data PLC1
        pub.subscribe(self.on_plc1_data, "modbus.data.plc1")
        
        # Safe cleanup ketika komponen dihancurkan
        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)

    def on_status_update(self, status1, status2):
        """Callback dipanggil otomatis dari Thread Worker via PubSub."""
        # Gunakan wx.CallAfter jika memanipulasi GUI langsung dari event pubsub thread
        wx.CallAfter(
            self.status_label.SetLabel, 
            f"PLC1: {status1} | PLC2: {status2}"
        )

    def on_plc1_data(self, data):
        """Menerima data terpisah dari PLC 1."""
        # Contoh akses nilai register:
        v32_val = data.get("V32", 0)
        x0_val = data.get("X0", False)
        # Process ke UI ...

    def on_reconnect(self, event):
        """Trigger percobaan koneksi manual dari UI."""
        # Panggil method worker thread melalui referensi global/app
        wx.GetApp().worker_thread.trigger_reconnect(server_num=1)

    def on_destroy(self, event):
        # Unsubscribe agar tidak memicu memory leak
        pub.unsubscribe(self.on_status_update, "modbus.status")
        pub.unsubscribe(self.on_plc1_data, "modbus.data.plc1")
        event.Skip()