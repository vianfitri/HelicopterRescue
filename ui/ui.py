import wx
import config
from utils.modbus_worker import ModbusWorkerThread, EVT_MODBUS_DATA_ID

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Modbus TCP Multi-Server Controller", size=(1000, 700))
        self.SetMinSize((900, 600))
        
        self.cfg_data = config.load_config()
        
        self.init_ui()
        
        # Bind custom event dari thread
        self.Connect(-1, -1, EVT_MODBUS_DATA_ID, self.on_modbus_data_update)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Inisialisasi & jalankan Worker Thread
        self.worker = ModbusWorkerThread(self, self.cfg_data)
        self.worker.start()

    def init_ui(self):
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # -------------------------------------------------------------
        # 1. TOP TITLEBAR
        # -------------------------------------------------------------
        top_panel = wx.Panel(main_panel)
        top_panel.SetBackgroundColour(wx.Colour(30, 40, 55))
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title = wx.StaticText(top_panel, label="MODBUS TCP DUAL-SERVER CONFIGURATION & MONITORING")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        top_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 12)
        top_panel.SetSizer(top_sizer)

        # -------------------------------------------------------------
        # BODY AREA
        # -------------------------------------------------------------
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 2. LEFT SIDEBAR (Lebar 200px)
        sidebar_panel = wx.Panel(main_panel, size=(200, -1))
        sidebar_panel.SetMinSize((200, -1))
        sidebar_panel.SetMaxSize((200, -1))
        sidebar_panel.SetBackgroundColour(wx.Colour(240, 242, 245))

        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Status Server 1 ---
        sb1_title = wx.StaticText(sidebar_panel, label="SERVER 1 STATUS")
        sb1_title.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.badge_s1 = wx.StaticText(sidebar_panel, label=" NOT CONNECTED ", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.badge_s1.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.badge_s1.SetBackgroundColour(wx.Colour(220, 53, 69))
        self.badge_s1.SetForegroundColour(wx.Colour(255, 255, 255))
        self.lbl_s1_target = wx.StaticText(sidebar_panel, label="")

        # --- Status Server 2 ---
        sb2_title = wx.StaticText(sidebar_panel, label="SERVER 2 STATUS")
        sb2_title.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.badge_s2 = wx.StaticText(sidebar_panel, label=" NOT CONNECTED ", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.badge_s2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.badge_s2.SetBackgroundColour(wx.Colour(220, 53, 69))
        self.badge_s2.SetForegroundColour(wx.Colour(255, 255, 255))
        self.lbl_s2_target = wx.StaticText(sidebar_panel, label="")

        sidebar_sizer.Add(sb1_title, 0, wx.TOP | wx.LEFT | wx.RIGHT, 15)
        sidebar_sizer.Add(self.badge_s1, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        sidebar_sizer.Add(self.lbl_s1_target, 0, wx.ALL | wx.EXPAND, 5)

        sidebar_sizer.Add(wx.StaticLine(sidebar_panel), 0, wx.EXPAND | wx.ALL, 10)

        sidebar_sizer.Add(sb2_title, 0, wx.TOP | wx.LEFT | wx.RIGHT, 15)
        sidebar_sizer.Add(self.badge_s2, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        sidebar_sizer.Add(self.lbl_s2_target, 0, wx.ALL | wx.EXPAND, 5)

        sidebar_panel.SetSizer(sidebar_sizer)

        # 3. RIGHT MAIN CONTENT (SETTINGS PAGE)
        content_scroller = wx.ScrolledWindow(main_panel, style=wx.VSCROLL)
        content_scroller.SetScrollRate(0, 20)
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        self.form_inputs = {}

        # Form Server 1 & Server 2
        content_sizer.Add(self.create_server_setting_group(content_scroller, "Server 1 Settings", "server1", 1), 0, wx.ALL | wx.EXPAND, 15)
        content_sizer.Add(self.create_server_setting_group(content_scroller, "Server 2 Settings", "server2", 2), 0, wx.ALL | wx.EXPAND, 15)

        # Tombol Simpan
        btn_save = wx.Button(content_scroller, label="Simpan Semua Pengaturan", size=(200, 40))
        btn_save.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        btn_save.Bind(wx.EVT_BUTTON, self.on_save_all)
        content_sizer.Add(btn_save, 0, wx.LEFT | wx.BOTTOM, 15)

        content_scroller.SetSizer(content_sizer)

        # Gabungkan Layout Body & Utama
        body_sizer.Add(sidebar_panel, 0, wx.EXPAND)
        body_sizer.Add(content_scroller, 1, wx.EXPAND)

        main_sizer.Add(top_panel, 0, wx.EXPAND)
        main_sizer.Add(body_sizer, 1, wx.EXPAND)

        main_panel.SetSizer(main_sizer)
        self.update_sidebar_labels()

    def create_server_setting_group(self, parent, title, server_key, server_num):
        """Membuat group box form setting register per server."""
        box = wx.StaticBox(parent, label=title)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        cfg = self.cfg_data[server_key]
        self.form_inputs[server_key] = {}

        # 1. Network Config & Reconnect Button
        net_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        net_sizer.Add(wx.StaticText(box, label="IP:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        txt_ip = wx.TextCtrl(box, value=cfg["ip"], size=(120, -1))
        net_sizer.Add(txt_ip, 0, wx.RIGHT, 15)

        net_sizer.Add(wx.StaticText(box, label="Port:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        txt_port = wx.TextCtrl(box, value=str(cfg["port"]), size=(60, -1))
        net_sizer.Add(txt_port, 0, wx.RIGHT, 20)

        btn_conn = wx.Button(box, label=f"Hubungkan Manual S{server_num}")
        btn_conn.Bind(wx.EVT_BUTTON, lambda evt, s_num=server_num: self.on_manual_connect(s_num))
        net_sizer.Add(btn_conn, 0)

        self.form_inputs[server_key]["ip"] = txt_ip
        self.form_inputs[server_key]["port"] = txt_port

        sizer.Add(net_sizer, 0, wx.ALL, 10)
        sizer.Add(wx.StaticLine(box), 0, wx.EXPAND | wx.BOTTOM, 10)

        # 2. Register Configurations Grid
        grid = wx.FlexGridSizer(cols=4, vgap=10, hgap=15)

        options_nc_no = ["NO", "NC"]

        def add_digital_row(label, addr_key, def_key):
            grid.Add(wx.StaticText(box, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            txt_addr = wx.TextCtrl(box, value=str(cfg[addr_key]), size=(60, -1))
            grid.Add(txt_addr, 0)
            
            grid.Add(wx.StaticText(box, label="Default State:"), 0, wx.ALIGN_CENTER_VERTICAL)
            cmb_def = wx.ComboBox(box, choices=options_nc_no, style=wx.CB_READONLY, size=(60, -1))
            cmb_def.SetValue(cfg[def_key])
            grid.Add(cmb_def, 0)

            self.form_inputs[server_key][addr_key] = txt_addr
            self.form_inputs[server_key][def_key] = cmb_def

        # Holding Registers (Analog)
        grid.Add(wx.StaticText(box, label="Holding Reg 1 Addr:"), 0, wx.ALIGN_CENTER_VERTICAL)
        txt_hr1 = wx.TextCtrl(box, value=str(cfg["holding_reg_1"]), size=(60, -1))
        grid.Add(txt_hr1, 0)
        self.form_inputs[server_key]["holding_reg_1"] = txt_hr1
        grid.Add(wx.StaticText(box, label=""), 0) # Spacer
        grid.Add(wx.StaticText(box, label=""), 0)

        grid.Add(wx.StaticText(box, label="Holding Reg 2 Addr:"), 0, wx.ALIGN_CENTER_VERTICAL)
        txt_hr2 = wx.TextCtrl(box, value=str(cfg["holding_reg_2"]), size=(60, -1))
        grid.Add(txt_hr2, 0)
        self.form_inputs[server_key]["holding_reg_2"] = txt_hr2
        grid.Add(wx.StaticText(box, label=""), 0)
        grid.Add(wx.StaticText(box, label=""), 0)

        # Digital Registers (Coil, DI, DO)
        add_digital_row("Coil/Relay 1 Addr:", "coil_1_addr", "coil_1_default")
        add_digital_row("Coil/Relay 2 Addr:", "coil_2_addr", "coil_2_default")
        add_digital_row("Discrete Input 1 Addr:", "di_1_addr", "di_1_default")
        add_digital_row("Discrete Input 2 Addr:", "di_2_addr", "di_2_default")
        add_digital_row("Discrete Output 1 Addr:", "di_out_1_addr", "di_out_1_default")
        add_digital_row("Discrete Output 2 Addr:", "di_out_2_addr", "di_out_2_default")

        sizer.Add(grid, 0, wx.ALL, 10)
        return sizer

    def update_sidebar_labels(self):
        self.lbl_s1_target.SetLabel(f"Target: {self.cfg_data['server1']['ip']}:{self.cfg_data['server1']['port']}")
        self.lbl_s2_target.SetLabel(f"Target: {self.cfg_data['server2']['ip']}:{self.cfg_data['server2']['port']}")

    def on_manual_connect(self, server_num):
        self.worker.trigger_reconnect(server_num)
        wx.MessageBox(f"Memulai ulang koneksi ke Server {server_num}...", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_modbus_data_update(self, event):
        """Update indikator status koneksi di sidebar."""
        def update_badge(badge, status):
            if status == "CONNECTED":
                badge.SetLabel(" CONNECTED ")
                badge.SetBackgroundColour(wx.Colour(40, 167, 69))
            elif status == "CONNECTING":
                badge.SetLabel(" CONNECTING... ")
                badge.SetBackgroundColour(wx.Colour(255, 193, 7))
            else:
                badge.SetLabel(" NOT CONNECTED ")
                badge.SetBackgroundColour(wx.Colour(220, 53, 69))
            badge.Refresh()

        update_badge(self.badge_s1, event.status1)
        update_badge(self.badge_s2, event.status2)

    def on_save_all(self, event):
        """Membaca UI, memvalidasi, dan menyimpan ke file JSON."""
        new_cfg = {}
        for s_key in ["server1", "server2"]:
            new_cfg[s_key] = {}
            for key, ctrl in self.form_inputs[s_key].items():
                val = ctrl.GetValue().strip()
                if key in ["ip", "coil_1_default", "coil_2_default", "di_1_default", "di_2_default", "di_out_1_default", "di_out_2_default"]:
                    new_cfg[s_key][key] = val
                else:
                    if not val.isdigit():
                        wx.MessageBox(f"Nilai untuk {key} pada {s_key} harus berupa angka valid!", "Validation Error", wx.OK | wx.ICON_ERROR)
                        return
                    new_cfg[s_key][key] = int(val)

        if config.save_config(new_cfg):
            self.cfg_data = new_cfg
            self.update_sidebar_labels()
            self.worker.update_config(new_cfg)
            wx.MessageBox("Pengaturan berhasil disimpan!", "Success", wx.OK | wx.ICON_INFORMATION)

    def on_close(self, event):
        self.worker.stop()
        self.Destroy()