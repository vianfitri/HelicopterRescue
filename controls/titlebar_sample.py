import wx

class TitleBar(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Warna Latar Belakang TitleBar (Dark Slate / Abu-abu Gelap)
        self.SetBackgroundColour(wx.Colour(35, 39, 42))
        
        # Sizer utama horizontal
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 1. Accent Bar Kotak (Orange)
        accent_bar = wx.Panel(self, size=(12, 28))
        accent_bar.SetBackgroundColour(wx.Colour(255, 127, 39))  # Warna Orange Accent
        
        # 2. Text Judul Titlebar
        title_text = wx.StaticText(self, label="Aplikasi Saya - Dashboard")
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))  # Warna Teks Putih
        
        # Mengatur Font Teks
        font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text.SetFont(font)
        
        # Menyusun elemen ke dalam Sizer
        main_sizer.Add(accent_bar, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        main_sizer.Add(title_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        
        self.SetSizer(main_sizer)