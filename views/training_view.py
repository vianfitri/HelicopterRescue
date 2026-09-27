import wx

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
            12,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            False,
            "Segoe UI"
        )
        bullet_lbl = wx.StaticText(self, label="●")
        bullet_lbl.SetForegroundColour(wx.Colour(255, 94, 19))
        title_lbl = wx.StaticText(self, label="TRAINING VIEW")
        title_lbl.SetForegroundColour(wx.Colour(255, 255, 255))