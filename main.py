import wx

from controls.sidebar import SidebarControl
from controls.title_bar import TitleBarControl

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
        self.SetBackgroundColour(wx.Colour(17, 19, 23))
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