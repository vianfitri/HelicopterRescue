import wx

from controls.title_bar_new import TitleBarControl
from controls.sidebar_new import SidebarControl

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
        main_panel.SetBackgroundColour(wx.Colour(8, 16, 25))

        # 1. TITLEBAR (Height: 70px)
        self.titlebar = TitleBarControl(main_panel)

        # 2. SIDEBAR (Width: 220px)
        self.sidebar = SidebarControl(main_panel, on_tab_changed=self._on_sidebar_tab_changed)

        # 3. KONTEN AREA (Menggunakan wx.ScrolledWindow)
        # =========================================================
        self.content_panel = wx.ScrolledWindow(main_panel, style=wx.VSCROLL)
        self.content_panel.SetScrollRate(0, 20) # Kecepatan scroll vertikal (0 = no horiz, 20px per step)
        self.content_panel.SetBackgroundColour(wx.Colour(14, 23, 36)) # Match tema gelap simulator

        self._build_demo_content()

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

    def _build_demo_content(self):
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        header_text = wx.StaticText(self.content_panel, label="RESCUE MISSION DASHBOARD")
        header_text.SetForegroundColour(wx.Colour(255, 255, 255))
        header_text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        content_sizer.Add(header_text, 0, wx.ALL, 20)

        for i in range(1, 25):
            card = wx.Panel(self.content_panel, size=(-1, 50))
            card.SetBackgroundColour(wx.Colour(23, 32, 48) if i % 2 == 0 else wx.Colour(18, 26, 38))

            card_sizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(card, label=f"Item / Form Input / Card Ke-{i}")
            label.SetForegroundColour(wx.Colour(200, 210, 220))
            card_sizer.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
            card.SetSizer(card_sizer)

            content_sizer.Add(card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        self.content_panel.SetSizer(content_sizer)
        self.content_panel.FitInside()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()