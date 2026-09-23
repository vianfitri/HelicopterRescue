import datetime
import wx

class TitleBarControl(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, size=(-1, 46), style=wx.NO_BORDER)
        self.SetBackgroundColour(wx.Colour(23, 26, 32))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy)
        
        # Clock timer (updates UTC clock every second)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.timer.Start(1000)
        
        self._init_ui()

    def _on_destroy(self, event):
        if hasattr(self, 'timer') and self.timer.IsRunning():
            self.timer.Stop()
        event.Skip()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left Safety Orange Accent Pip
        accent_pip = wx.Panel(self, size=(4, 24), style=wx.NO_BORDER)
        accent_pip.SetBackgroundColour(wx.Colour(255, 94, 19))
        sizer.Add(accent_pip, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 16)

        # Title Label
        title_lbl = wx.StaticText(self, label="HELICOPTER RESCUE SIMULATOR")
        title_lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        title_lbl.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                False,
                "Segoe UI"
            )
        )
        sizer.Add(title_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        # Stretch spacer pushing status indicators to the right
        sizer.AddStretchSpacer(1)

        # Zulu Time Display
        self.time_lbl = wx.StaticText(self, label=self._get_zulu_time())
        self.time_lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        self.time_lbl.SetFont(
            wx.Font(
                9,
                wx.FONTFAMILY_TELETYPE,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                False,
                "Consolas"
            )
        )
        sizer.Add(self.time_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 18)
        
        self.SetSizer(sizer)

    def _get_zulu_time(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        return now.strftime("%H:%M:%S UTC")

    def _on_timer(self, event):
        self.time_lbl.SetLabel(self._get_zulu_time())
        self.Layout()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        w, h = self.GetClientSize()
        # Bottom border
        dc.SetPen(wx.Pen(wx.Colour(43, 49, 61), 1))
        dc.DrawLine(0, h - 1, w, h - 1)