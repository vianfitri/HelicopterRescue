import wx

from controls.sidebar_tabcontrol import SidebarTabControl
from utils.svg_utils import load_svg_as_bitmap

SVG_TRAINING = "assets/icons/helicopter.svg"
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

        # Color Scheme for icon
        HEX_NORMAL = "#A0A5AF"
        HEX_HOVER = "#D2D7E1"
        HEX_ACTIVE = "#EB8214"

        # Load svg tab
        bmp_tr_norm = load_svg_as_bitmap(SVG_TRAINING, HEX_NORMAL, size=(24, 24), is_file=True)
        bmp_tr_hover = load_svg_as_bitmap(SVG_TRAINING, HEX_HOVER, size=(24, 24), is_file=True)
        bmp_tr_active = load_svg_as_bitmap(SVG_TRAINING, HEX_ACTIVE, size=(24, 24), is_file=True)

        bmp_hs_norm = load_svg_as_bitmap(SVG_HISTORY, HEX_NORMAL, size=(24, 24), is_file=True)
        bmp_hs_hover = load_svg_as_bitmap(SVG_HISTORY, HEX_HOVER, size=(24, 24), is_file=True)
        bmp_hs_active = load_svg_as_bitmap(SVG_HISTORY, HEX_ACTIVE, size=(24, 24), is_file=True)

        bmp_ss_norm = load_svg_as_bitmap(SVG_SESSION, HEX_NORMAL, size=(24, 24), is_file=True)
        bmp_ss_hover = load_svg_as_bitmap(SVG_SESSION, HEX_HOVER, size=(24, 24), is_file=True)
        bmp_ss_active = load_svg_as_bitmap(SVG_SESSION, HEX_ACTIVE, size=(24, 24), is_file=True)
        
        # Add Tab
        self.sidebar.AddTab("Training", bmp_tr_norm, bmp_tr_hover, bmp_tr_active)
        self.sidebar.AddTab("History", bmp_hs_norm, bmp_hs_hover, bmp_hs_active)
        self.sidebar.AddTab("Session", bmp_ss_norm, bmp_ss_hover, bmp_ss_active)

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