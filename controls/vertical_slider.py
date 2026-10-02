import wx


class VerticalSlider(wx.Control):

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        value=0.0,
        min_val=0.0,
        max_val=100.0,
        pos=wx.DefaultPosition,
        size=(60, 200),
        style=wx.BORDER_NONE,
    ):
        super().__init__(parent, id, pos, size, style)

        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.value = float(max(self.min_val, min(value, self.max_val)))

        # Styling Params
        self.track_width = 8
        self.thumb_radius = 10
        self.padding_y = 20

        # Colors & Theme (Atur ke warna Biru sesuai permintaan)
        self.track_bg = wx.Colour(32, 38, 48)
        self.track_active = wx.Colour(45, 147, 226)  # Warna Biru
        self.thumb_color = wx.Colour(255, 255, 255)
        self.thumb_border = wx.Colour(45, 147, 226)  # Warna Biru
        self.tick_color = wx.Colour(160, 165, 175)
        self.text_color = wx.Colour(100, 110, 120)

        self.is_dragging = False

        # Event Binding
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_SIZE, self.on_size)

        # Mouse interaction events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if not gc:
            return

        w, h = self.GetClientSize()

        # Background
        gc.SetBrush(
            gc.CreateBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        )
        gc.SetPen(gc.CreatePen(wx.NullPen))
        gc.DrawRectangle(0, 0, w, h)

        # Track X diletakkan di tengah area kiri (memberi ruang label di kanan)
        track_x = 20
        usable_height = h - (2 * self.padding_y)

        # 1. Draw Inactive Track
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.track_bg)))
        gc.DrawRoundedRectangle(
            track_x - (self.track_width / 2),
            self.padding_y,
            self.track_width,
            usable_height,
            self.track_width / 2,
        )

        # Calculate Thumb Y Position (Dari Atas ke Bawah)
        if self.max_val > self.min_val:
            ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        else:
            ratio = 0.0

        ratio = max(0.0, min(1.0, ratio))
        thumb_y = self.padding_y + (ratio * usable_height)

        # 2. Draw Active Track (Fill dari Atas ke Thumb Y)
        if ratio > 0:
            gc.SetBrush(gc.CreateBrush(wx.Brush(self.track_active)))
            gc.DrawRoundedRectangle(
                track_x - (self.track_width / 2),
                self.padding_y,
                self.track_width,
                thumb_y - self.padding_y,
                self.track_width / 2,
            )

        # 3. Draw Ticks & Labels (Tick bertahap kelipatan 20)
        gc.SetFont(self.GetFont().MakeSmaller(), self.text_color)

        step = max(10, int((self.max_val - self.min_val) / 5))
        for i in range(int(self.min_val), int(self.max_val) + 1, step):
            tick_ratio = (i - self.min_val) / (self.max_val - self.min_val)
            tick_y = self.padding_y + (tick_ratio * usable_height)
            tick_x1 = track_x + 10
            tick_x2 = tick_x1 + 4

            # Draw Tick Line
            gc.SetPen(gc.CreatePen(wx.Pen(self.tick_color, 1)))
            gc.StrokeLine(tick_x1, tick_y, tick_x2, tick_y)

            # Draw Label
            lbl = str(i)
            _, text_h = gc.GetTextExtent(lbl)
            gc.DrawText(lbl, tick_x2 + 4, tick_y - (text_h / 2))

        # 4. Draw Thumb (Knob)
        r = self.thumb_radius

        # Draw Thumb Shadow
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 20))))
        gc.DrawEllipse(track_x - r, thumb_y - r + 2, r * 2, r * 2)

        # Draw Thumb Body
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.thumb_color)))
        gc.SetPen(gc.CreatePen(wx.Pen(self.thumb_border, 3)))
        gc.DrawEllipse(track_x - r, thumb_y - r, r * 2, r * 2)

    def _update_value_from_mouse(self, mouse_y):
        _, h = self.GetClientSize()
        usable_height = h - (2 * self.padding_y)

        if usable_height <= 0:
            return

        # Map y mouse position back to ratio (0.0 at top, 1.0 at bottom)
        ratio = (mouse_y - self.padding_y) / usable_height
        ratio = max(0.0, min(1.0, ratio))

        new_val = self.min_val + (ratio * (self.max_val - self.min_val))
        self.SetValue(new_val)

    def on_mouse_down(self, event):
        self.is_dragging = True
        self.CaptureMouse()
        self._update_value_from_mouse(event.GetY())

    def on_mouse_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.is_dragging = False

    def on_mouse_move(self, event):
        if self.is_dragging and event.Dragging():
            self._update_value_from_mouse(event.GetY())

    def on_size(self, event):
        self.Refresh()
        event.Skip()

    def GetValue(self):
        return self.value

    def SetValue(self, val):
        """Memperbarui nilai dari luar dan memperbarui tampilan slider"""
        self.value = float(max(self.min_val, min(val, self.max_val)))
        self.Refresh()