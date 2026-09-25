import wx

from controls.sidebar_tabcontrol import SidebarTabControl
from controls.sidebar import SidebarControl
from controls.title_bar import TitleBarControl
from utils.svg_utils import load_svg_as_bitmap

SVG_TRAINING = "assets/icons/helicopter.svg"
SVG_HISTORY = "assets/icons/clipboard-clock.svg"
SVG_SESSION = "assets/icons/gear-icon.svg"

class MainFrame(wx.Frame):
    def __init__(self):
        super(MainFrame, self).__init__(
            None,
            id=wx.ID_ANY,
            title="Helicopter Rescue Simulator",
            size=(1366, 768),
            style=wx.DEFAULT_FRAME_STYLE
        )

        self.SetMinSize((1024, 600))
        #self.SetBackgroundColour(wx.Colour(18, 22, 28))
        self.SetBackgroundColour(wx.Colour(17, 19, 23))
        #self.SetBackgroundColour(wx.Colour(0, 255, 0))
        #self.SetBackgroundColour(wx.Colour(8, 15, 25))
        self.Centre()

        self._init_ui()

    def _init_ui(self):
        # root panel
        root_panel = wx.Panel(self)

        # Vertical root sizer: Top Title Bar + Body
        root_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top Title Bar Control
        self.title_bar = TitleBarControl(root_panel)
        root_sizer.Add(self.title_bar, 0, wx.EXPAND)

        # Main Body: Horizontal split
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Right Content Area (Simplebook page swtcher)
        self.content_book = wx.Simplebook(root_panel, style=wx.NO_BORDER)
        self.content_book.SetBackgroundColour(wx.Colour(17, 19, 23))

        # Left sidebar
        self.sidebar = SidebarControl(root_panel, on_tab_changed=self._on_tab_changed)
        body_sizer.Add(self.sidebar, 0, wx.EXPAND)

        # ==== TAB PAGE ====
        # Main Layout
        #main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Sidebar Control
        #self.sidebar = SidebarTabControl(self, size=(200, -1))

        # Color Scheme for icon
        #HEX_NORMAL = "#A0A5AF"
        HEX_NORMAL = "#BFC1C1"
        HEX_HOVER = "#D2D7E1"
        #HEX_HOVER = "#BFC1C1"
        HEX_ACTIVE = "#FFFFFF"

        # Load svg tab
        bmp_tr_norm = load_svg_as_bitmap(SVG_TRAINING, HEX_NORMAL, size=(20, 20), is_file=True)
        bmp_tr_hover = load_svg_as_bitmap(SVG_TRAINING, HEX_HOVER, size=(20, 20), is_file=True)
        bmp_tr_active = load_svg_as_bitmap(SVG_TRAINING, HEX_ACTIVE, size=(20, 20), is_file=True)

        bmp_hs_norm = load_svg_as_bitmap(SVG_HISTORY, HEX_NORMAL, size=(20, 20), is_file=True)
        bmp_hs_hover = load_svg_as_bitmap(SVG_HISTORY, HEX_HOVER, size=(20, 20), is_file=True)
        bmp_hs_active = load_svg_as_bitmap(SVG_HISTORY, HEX_ACTIVE, size=(20, 20), is_file=True)

        bmp_ss_norm = load_svg_as_bitmap(SVG_SESSION, HEX_NORMAL, size=(20, 20), is_file=True)
        bmp_ss_hover = load_svg_as_bitmap(SVG_SESSION, HEX_HOVER, size=(20, 20), is_file=True)
        bmp_ss_active = load_svg_as_bitmap(SVG_SESSION, HEX_ACTIVE, size=(20, 20), is_file=True)
        
        # Add Tab
        #self.sidebar.AddTab("Training", bmp_tr_norm, bmp_tr_hover, bmp_tr_active)
        #self.sidebar.AddTab("History", bmp_hs_norm, bmp_hs_hover, bmp_hs_active)
        #self.sidebar.AddTab("Session", bmp_ss_norm, bmp_ss_hover, bmp_ss_active)

        # Tab Change Event
        #self.sidebar.Bind(wx.EVT_BUTTON, self.OnTabChanged)

        # Content Panel
        #self.content_panel = wx.Panel(self)
        #self.content_panel.SetBackgroundColour(wx.Colour(28, 33, 40))

        #self.label_title = wx.StaticText(self.content_panel, label="SESSION DETAIL #014", pos=(20, 20))
        #font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        #self.label_title.SetFont(font)
        #self.label_title.SetForegroundColour(wx.Colour(255, 255, 255))

        # Layout
        #main_sizer.Add(self.sidebar, 0, wx.EXPAND | wx.ALL, 0)
        #main_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 5)

        #self.SetSizer(main_sizer)
        
        # ==== === ==== ====

        #body_sizer.Add(self.content_book, 1, wx.EXPAND)

        root_sizer.Add(body_sizer, 1, wx.EXPAND)
        root_panel.SetSizer(root_sizer)
        self.Layout()

    def _on_tab_changed(self, tab_index: int):
        if hasattr(self, 'content_book') and 0 <= tab_index < self.content_book.GetPageCount():
            self.content_book.ChangeSelection(tab_index)

    #def OnTabChanged(self, event):
    #    selected_idx = event.GetInt()
    #    tab_name = self.sidebar.tabs[selected_idx]['label']
    #    self.label_title.SetLabel(f"Halaman: {tab_name.upper()}")

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()