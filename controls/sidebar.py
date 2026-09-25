import wx


class SidebarControl(wx.Panel):

    def __init__(self, parent, on_tab_changed=None):
        super().__init__(parent, id=wx.ID_ANY, style=wx.NO_BORDER)
        self.SetBackgroundColour(wx.Colour(8, 15, 25))
        #self.SetBackgroundColour(wx.Colour(0, 0, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetMinSize((200, -1))
        self.SetMaxSize((250, -1))

        self.on_tab_changed = on_tab_changed
        self.buttons = []
        self.active_tab_index = 0

        self.Bind(wx.EVT_PAINT, self._on_paint)

        self._init_ui()

    def _init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header Logo and Title Area
        header_panel = wx.Panel(self, style=wx.NO_BORDER)
        header_panel.SetBackgroundColour(wx.Colour(8, 15, 25))
        header_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top Spacing
        header_sizer.AddSpacer(16)

        # spacing
        header_sizer.AddSpacer(16)

        # Tab Buttons
        tab_definitions = []

        tabs_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(main_sizer)

        # Activate initial tab (0)
        self.select_tab(0)

    def _create_connection_status_card(self):
        pass

    def _on_tab_click(self, event):
        tab_id = event.tab_id
        self.select_tab(tab_id)

    def select_tab(self, index: int):
        self.active_tab_index = index
        for idx, btn in enumerate(self.buttons):
            btn.set_selected(idx == index)
        if self.on_tab_changed:
            self.on_tab_changed(index)

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(8, 15, 25)))
        #dc.SetBackground(wx.Brush(wx.Colour(0, 0, 255)))
        dc.Clear()

        # Right border line separating sidebar from content
        w, h = self.GetClientSize()
        dc.SetPen(wx.Pen(wx.Colour(43, 49, 61), 1))
        dc.DrawLine(w - 1, 0, w - 1, h)