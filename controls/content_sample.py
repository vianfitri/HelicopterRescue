import wx

class ContentArea(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Warna Latar Belakang Content Area (Terang / Off-White)
        self.SetBackgroundColour(wx.Colour(240, 242, 245))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Teks Konten Utama
        content_text = wx.StaticText(self, label="Selamat Datang di Area Konten Utama")
        content_text.SetForegroundColour(wx.Colour(30, 30, 30))
        
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        content_text.SetFont(font)
        
        sizer.Add(content_text, 0, wx.ALL, 20)
        self.SetSizer(sizer)