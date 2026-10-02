import datetime
import wx

class TitleBarControl(wx.Panel):
    def __init__(self, parent):
        # Set tinggi fixed 46px
        super().__init__(parent, id=wx.ID_ANY, size=(-1, 60), style=wx.NO_BORDER)
        
        self.SetMinSize((-1, 60))
        self.SetMaxSize((-1, 60))
        
        # Background utama panel
        self.bg_color = wx.Colour(8, 16, 25)
        self.SetBackgroundColour(self.bg_color)
        
        # Timer untuk jam UTC
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy)
        
        self._init_ui()
        self.timer.Start(1000)

    def _on_destroy(self, event):
        if hasattr(self, 'timer') and self.timer.IsRunning():
            self.timer.Stop()
        event.Skip()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 1. Left Accent Pip (Gunakan wx.Panel tipis dengan background color)
        accent_pip = wx.Panel(self, size=(4, 24), style=wx.NO_BORDER)
        accent_pip.SetBackgroundColour(wx.Colour(255, 94, 19))
        sizer.Add(accent_pip, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 16)

        # 2. Title Label
        title_lbl = wx.StaticText(self, label="HELICOPTER RESCUE SIMULATOR")
        title_lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        title_lbl.SetFont(
            wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Segoe UI")
        )
        sizer.Add(title_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        # Spacer fleksibel untuk mendorong jam ke kanan
        sizer.AddStretchSpacer(1)

        # 3. Zulu Time Display
        self.time_lbl = wx.StaticText(self, label=self._get_zulu_time())
        self.time_lbl.SetForegroundColour(wx.Colour(200, 210, 225))
        self.time_lbl.SetFont(
            wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Consolas")
        )
        sizer.Add(self.time_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 18)

        # 4. Garis Pembatas Bawah (Gunakan wx.StaticLine pengganti EVT_PAINT manual)
        # Menggantikan draw line manual agar tidak perlu EVT_PAINT
        bottom_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        bottom_line.SetForegroundColour(wx.Colour(43, 49, 61))

        # Bungkus sizer utama dan garis bawah
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(sizer, 1, wx.EXPAND)
        root_sizer.Add(bottom_line, 0, wx.EXPAND)

        self.SetSizer(root_sizer)

    def _get_zulu_time(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        return now.strftime("%H:%M:%S UTC")

    def _on_timer(self, event):
        # Cukup update teks label. Tidak perlu call self.Layout() tiap detik.
        self.time_lbl.SetLabel(self._get_zulu_time())