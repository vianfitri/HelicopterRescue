import wx

class LongitudinalCard(wx.Panel):

    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.NO_BORDER
        )
        self.SetBackgroundColour(wx.Colour(17, 19, 23))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)

        self.Bind(wx.EVT_PAINT, self._on_paint)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(12)

    def _on_paint(self, event):
        pass
    
class TrainingView(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent, style=wx.NO_BORDER)
        self.SetBackgroundColour(wx.Colour(17, 19, 23))
        self.SetDoubleBuffered(True)

        self._init_ui()

    def _init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(18)

        # View Title Section
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_font = wx.Font(
            10,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            False,
            "Segoe UI"
        )
        bullet_lbl = wx.StaticText(self, label="●")
        bullet_lbl.SetForegroundColour(wx.Colour(255, 94, 19))
        bullet_lbl.SetFont(lbl_font)
        lbl_W, _ = bullet_lbl.GetTextExtent(" ")
        title_lbl = wx.StaticText(self, label="TRAINING VIEW")
        title_lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        title_lbl.SetFont(lbl_font)

        header_sizer.Add(bullet_lbl, 0, wx.LEFT, 24)
        header_sizer.AddSpacer(lbl_W)
        header_sizer.Add(title_lbl, 0, wx.RIGHT, 24)

        main_sizer.Add(header_sizer, 0, wx.EXPAND)
        main_sizer.AddSpacer(16)

        # Content
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_content_sizer = wx.BoxSizer(wx.VERTICAL)

        content_sizer.Add(left_content_sizer, 0, wx.LEFT, 24)


        

        self.SetSizer(main_sizer)