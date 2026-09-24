import wx
# Mengimpor modul/kelas terpisah
from controls.titlebar_sample import TitleBar
from controls.sidebar_sample import Sidebar
from controls.content_sample import ContentArea

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Main Window", size=(900, 600))
        
        # Panel Utama
        main_panel = wx.Panel(self)
        
        # Inisialisasi Komponen dari Kelas Terpisah
        self.title_bar = TitleBar(main_panel)
        self.sidebar = Sidebar(main_panel)
        self.content_area = ContentArea(main_panel)
        
        # Layout 1: Sizer Horizontal untuk menggabungkan Sidebar dan Content
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)
        body_sizer.Add(self.sidebar, 0, wx.EXPAND)  # Sidebar lebar tetap (proposi 0)
        body_sizer.Add(self.content_area, 1, wx.EXPAND)  # Content fleksibel (proposi 1)
        
        # Layout 2: Sizer Utama (Vertical) untuk menggabungkan TitleBar dan Body
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.title_bar, 0, wx.EXPAND)  # Titlebar tinggi otomatis
        main_sizer.Add(body_sizer, 1, wx.EXPAND)     # Body mengisi sisa ruang bawah
        
        main_panel.SetSizer(main_sizer)
        
        self.Centre()

class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True

if __name__ == "__main__":
    app = App()
    app.MainLoop()