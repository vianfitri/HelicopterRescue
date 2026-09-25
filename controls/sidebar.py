import wx

from .tab_button import TabButton, EVT_TAB_SELECTED

class SidebarControl(wx.Panel):

    def __init__(self, parent, on_tab_changed=None):
        super().__init__(parent, id=wx.ID_ANY, style=wx.NO_BORDER)
        self.SetBackgroundColour(wx.Colour(8, 15, 25))
        #self.SetBackgroundColour(wx.Colour(0, 0, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetMinSize((210, -1))
        self.SetMaxSize((250, -1))

        self.on_tab_changed = on_tab_changed
        self.buttons = []
        self.active_tab_index = 0

        # load and prepare bitmap logo
        self.logo_bitmap = self._load_and_scale_logo("assets/images/PPS_logo.png", target_width = 100)

        self.Bind(wx.EVT_PAINT, self._on_paint)

        self._init_ui()

    def _load_and_scale_logo(self, image_path, target_width = 100):
        image = wx.Image(image_path, wx.BITMAP_TYPE_PNG)

        if not image.IsOk():
            return None

        # calculate height proportional based target_width
        orig_w, orig_h = image.GetWidth(), image.GetHeight()
        aspect_ratio = orig_h / orig_w
        target_height = int(target_width * aspect_ratio)

        # rescaling image
        scaled_image = image.Scale(target_width, target_height, wx.IMAGE_QUALITY_BOX_AVERAGE)
        return scaled_image.ConvertToBitmap()

    def _init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header Logo and Title Area
        header_panel = wx.Panel(self, style=wx.NO_BORDER)
        header_panel.SetBackgroundColour(wx.Colour(8, 15, 25))
        header_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top Spacing
        header_sizer.AddSpacer(16)

        # client Logo Canvas
        client_logo_canvas = wx.Panel(header_panel, size=(150, 150), style=wx.NO_BORDER)
        client_logo_canvas.SetBackgroundColour(wx.Colour(8, 15, 25))

        # inline paint Handler to draw logo
        def _on_canvas_paint(event):
            dc = wx.PaintDC(client_logo_canvas)
            gc = wx.GraphicsContext.Create(dc)
            if not gc:
                return
            
            if self.logo_bitmap and self.logo_bitmap.IsOk():
                cw, ch = client_logo_canvas.GetClientSize()
                bw, bh = self.logo_bitmap.GetWidth(), self.logo_bitmap.GetHeight()

                # calculate coordinat for center image
                x = (cw - bw) // 2
                y = (ch - bh) // 2

                # draw bitmap
                gc.DrawBitmap(self.logo_bitmap, x, y, bw, bh)

        client_logo_canvas.Bind(wx.EVT_PAINT, _on_canvas_paint)

        header_sizer.Add(client_logo_canvas, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # spacing
        header_sizer.AddSpacer(16)

        header_panel.SetSizer(header_sizer)
        main_sizer.Add(header_panel, 0, wx.EXPAND | wx.RIGHT, border=1)

        # Tab Buttons
        tab_definitions = [
            (0, "TRAINING", "flight"),
            (1, "SETTINGS", "gear"),
            (2, "LOGS", "list")
        ]

        tabs_sizer = wx.BoxSizer(wx.VERTICAL)
        for tab_id, label, icon_type in tab_definitions:
            btn = TabButton(self, tab_id=tab_id, label=label, icon_type=icon_type)
            btn.Bind(EVT_TAB_SELECTED, self._on_tab_click)
            self.buttons.append(btn)
            tabs_sizer.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        main_sizer.Add(tabs_sizer, 0, wx.EXPAND)

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