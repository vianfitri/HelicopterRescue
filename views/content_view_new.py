import wx

class ContentView(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent, style=wx.VSCROLL)
        
        # Kecepatan scroll vertikal (0 = no horizontal scroll, 20px per scroll step)
        self.SetScrollRate(0, 20)
        
        # Samakan warna background dengan tema gelap simulator
        self.SetBackgroundColour(wx.Colour(14, 23, 36))
        
        self._init_ui()

    def _init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # =========================================================
        # 1. AREA ATAS: TITLE PAGE (Lebar Memenuhi Screen/Page)
        # =========================================================
        self.title_panel = wx.Panel(self)
        self.title_panel.SetBackgroundColour(wx.Colour(20, 31, 46))
        
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.page_title = wx.StaticText(self.title_panel, label="RESCUE MISSION DASHBOARD")
        self.page_title.SetForegroundColour(wx.Colour(255, 255, 255))
        self.page_title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
               
        title_sizer.Add(self.page_title, 0, wx.BOTTOM, 4)

        self.title_panel.SetSizer(title_sizer)

        # Tambahkan Title Panel ke Main Sizer (Lebar Penuh)
        main_sizer.Add(self.title_panel, 0, wx.EXPAND | wx.ALL, 20)

        # =========================================================
        # 2. AREA BAWAH: 3 HORIZONTAL COLUMNS
        # =========================================================
        horizontal_body_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # ---------------------------------------------------------
        # A. KARTU KIRI (Fixed Width: 280px, Target Min Height: 850px)
        # ---------------------------------------------------------
        self.left_card = wx.Panel(self)
        self.left_card.SetMinSize((280, 850))
        self.left_card.SetMaxSize((280, -1))
        self.left_card.SetBackgroundColour(wx.Colour(23, 34, 50))
        
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_label = wx.StaticText(self.left_card, label="LEFT CONTROL CARD\n(Width: 280px)")
        left_label.SetForegroundColour(wx.Colour(180, 200, 220))
        left_sizer.Add(left_label, 0, wx.RIGHT, 16)
        self.left_card.SetSizer(left_sizer)

        # ---------------------------------------------------------
        # B. CANVAS TENGAH (Flexible Width, Target Min Height: 850px)
        # ---------------------------------------------------------
        self.canvas_panel = wx.Panel(self)
        self.canvas_panel.SetMinSize((-1, 850))
        self.canvas_panel.SetBackgroundColour(wx.Colour(8, 14, 22))
        
        canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        canvas_label = wx.StaticText(self.canvas_panel, label="CENTER CONTENT CANVAS\n(Flexible Width)")
        canvas_label.SetForegroundColour(wx.Colour(0, 200, 255))
        canvas_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        canvas_sizer.Add(canvas_label, 0, wx.ALL | wx.ALIGN_CENTER, 16)
        self.canvas_panel.SetSizer(canvas_sizer)

        # ---------------------------------------------------------
        # C. KARTU KANAN (Fixed Width: 280px, Target Min Height: 850px)
        # ---------------------------------------------------------
        self.right_card = wx.Panel(self)
        self.right_card.SetMinSize((280, 850))
        self.right_card.SetMaxSize((280, -1))
        self.right_card.SetBackgroundColour(wx.Colour(23, 34, 50))
        
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_label = wx.StaticText(self.right_card, label="RIGHT TELEMETRY CARD\n(Width: 280px)")
        right_label.SetForegroundColour(wx.Colour(180, 200, 220))
        right_sizer.Add(right_label, 0, wx.LEFT, 16)
        self.right_card.SetSizer(right_sizer)

        # Tambahkan ketiga area ke Horizontal Body Sizer
        horizontal_body_sizer.Add(self.left_card, 0, wx.EXPAND | wx.RIGHT, 20)
        horizontal_body_sizer.Add(self.canvas_panel, 1, wx.EXPAND)
        horizontal_body_sizer.Add(self.right_card, 0, wx.EXPAND | wx.LEFT, 20)

        # Masukkan area horizontal ke Main Sizer
        main_sizer.Add(horizontal_body_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 16)

        self.SetSizer(main_sizer)
        
        # Memastikan wx.ScrolledWindow menghitung total tinggi konten agar scrollbar aktif
        self.FitInside()