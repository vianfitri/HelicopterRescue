import wx

from controls.sidebar_tabcontrol import SidebarTabControl
from utils.svg_utils import load_svg_as_bitmap

SVG_TRAINING = "assets/icons/helicopter-icon.svg"
SVG_HISTORY = "assets/icons/training-icon.svg"
SVG_SESSION = "assets/icons/gear-icon.svg"

class MainFrame(wx.Frame):
    def __init__(self):
        super(MainFrame, self).__init__(
            None,
            title="Helicopter Rescue Simulator",
            size=(1366, 768),
        )
        self.SetBackgroundColour(wx.Colour(18, 22, 28))

        # Main Layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Sidebar Control
        self.sidebar = SidebarTabControl(self, size=(200, -1))
        
        # Add Tab
        self.sidebar.AddTab("Training")
        self.sidebar.AddTab("History")
        self.sidebar.AddTab("Session")

        # Tab Change Event
        self.sidebar.Bind(wx.EVT_BUTTON, self.OnTabChanged)

        # Content Panel
        self.content_panel = wx.Panel(self)
        self.content_panel.SetBackgroundColour(wx.Colour(28, 33, 40))

        self.label_title = wx.StaticText(self.content_panel, label="SESSION DETAIL #014", pos=(20, 20))
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label_title.SetFont(font)
        self.label_title.SetForegroundColour(wx.Colour(255, 255, 255))

        # Layout
        main_sizer.Add(self.sidebar, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

    def OnTabChanged(self, event):
        selected_idx = event.GetInt()
        tab_name = self.sidebar.tabs[selected_idx]['label']
        self.label_title.SetLabel(f"Halaman: {tab_name.upper()}")

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()