import wx

from controls.title_bar_new import TitleBarControl
from controls.sidebar_new import SidebarControl

from views.content_view_new import ContentView

class MainFrame(wx.Frame):
    def __init__(self):
        target_width = 1720
        target_height = 1440

        super().__init__(None, title="Helicopter Rescue Simulator", size=(target_width, target_height))

        # Deteksi area kerja layar dev
        client_area = wx.Display().GetClientArea()
        max_w, max_h = client_area.GetWidth(), client_area.GetHeight()

        # Window dipasang ukuran maksimum monitor dev saat ini
        self.SetSize((min(target_width, max_w), min(target_height, max_h)))
        self.Center()

        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour(wx.Colour(5, 11, 20))

        # 1. TITLEBAR (Height: 70px)
        self.titlebar = TitleBarControl(main_panel)

        # 2. SIDEBAR (Width: 220px)
        self.sidebar = SidebarControl(main_panel, on_tab_changed=self._on_sidebar_tab_changed)

        # 3. KONTEN AREA (Menggunakan wx.ScrolledWindow)
        # =========================================================
        self.content_panel = ContentView(main_panel)

        # Layout Sizers
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)
        body_sizer.Add(self.sidebar, 0, wx.EXPAND)
        body_sizer.Add(self.content_panel, 1, wx.EXPAND)

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(self.titlebar, 0, wx.EXPAND)
        root_sizer.Add(body_sizer, 1, wx.EXPAND)

        main_panel.SetSizer(root_sizer)

    def _on_sidebar_tab_changed(self, tab_index: int):
        # Callback saat tab di sidebar diklik
        print(f"Sidebar active tab switched to index: {tab_index}")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()