import wx

class Sidebar(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Warna Latar Belakang Sidebar (Dark Gray)
        self.SetBackgroundColour(wx.Colour(47, 49, 54))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Contoh Item Menu Navigasi
        menus = ["Dashboard", "Laporan", "Pengaturan", "Profil"]
        
        for menu in menus:
            btn = wx.Button(self, label=menu, size=(-1, 40))
            # Styling tombol agar menyatu dengan sidebar
            btn.SetForegroundColour(wx.Colour(220, 221, 222))
            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)
            
        self.SetSizer(sizer)