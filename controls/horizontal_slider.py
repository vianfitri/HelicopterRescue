import wx

class HorizontalSlider(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, value=5.0, min_val=0.0, max_val=10.0, pos=wx.DefaultPosition, size=(350, 60), style=wx.BORDER_NONE):
        super().__init__(parent, id, pos, size, style)

        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.value = float(
            max(self.min_val,
                min(value, self.max_val)
            )
        )

        # Styling Params
        self.track_height = 8
        self.thumb_radius = 10
        self.padding_x = 20

        self.track_bg = wx.Colour(220, 224, 230)
        #self.track_active = wx.Colour(99, 102, 241)     # Modern Indigo
        self.track_active = wx.Colour(255, 94, 19)
        self.thumb_color = wx.Colour(255, 255, 255)
        #self.thumb_border = wx.Colour(99, 102, 241)
        self.thumb_border = wx.Colour(255, 94, 19)
        self.tick_color = wx.Colour(160, 165, 175)
        self.text_color = wx.Colour(100, 110, 120)

        # Event Binding
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if not gc:
            return

        w, h = self.GetClientSize()

        # Background
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.GetParent().GetBackgroundColour())))
        gc.SetPen(gc.CreatePen(wx.NullPen))
        gc.DrawRectangle(0, 0, w, h)

        track_y = 20
        usable_width = w - (2 * self.padding_x)

        # 1. Draw Inactive Track
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.track_bg)))
        gc.DrawRoundedRectangle(self.padding_x, track_y - (self.track_height / 2),
                                usable_width, self.track_height, self.track_height / 2)

        # Calculate Thumb X Position
        if self.max_val > self.min_val:
            ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        else:
            ratio = 0.0
            
        ratio = max(0.0, min(1.0, ratio))
        thumb_x = self.padding_x + (ratio * usable_width)

        # 2. Draw Active Track (Fill)
        if ratio > 0:
            gc.SetBrush(gc.CreateBrush(wx.Brush(self.track_active)))
            gc.DrawRoundedRectangle(self.padding_x, track_y - (self.track_height / 2),
                                    thumb_x - self.padding_x, self.track_height, self.track_height / 2)

        # 3. Draw Ticks & Labels
        gc.SetFont(self.GetFont().MakeSmaller(), self.text_color)
        for i in range(int(self.min_val), int(self.max_val) + 1):
            tick_ratio = (i - self.min_val) / (self.max_val - self.min_val)
            tick_x = self.padding_x + (tick_ratio * usable_width)
            tick_y1 = track_y + 10
            tick_y2 = tick_y1 + 4

            # Draw Tick Line
            gc.SetPen(gc.CreatePen(wx.Pen(self.tick_color, 1)))
            gc.StrokeLine(tick_x, tick_y1, tick_x, tick_y2)

            # Draw Label
            lbl = str(i)
            text_w, _ = gc.GetTextExtent(lbl)
            gc.DrawText(lbl, tick_x - (text_w / 2), tick_y2 + 2)

        # 4. Draw Thumb (Pegangan Static)
        r = self.thumb_radius

        # Draw Thumb Shadow
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 20))))
        gc.DrawEllipse(thumb_x - r, track_y - r + 2, r * 2, r * 2)

        # Draw Thumb Body
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.thumb_color)))
        gc.SetPen(gc.CreatePen(wx.Pen(self.thumb_border, 3)))
        gc.DrawEllipse(thumb_x - r, track_y - r, r * 2, r * 2)

    def on_size(self, event):
        self.Refresh()
        event.Skip()

    def GetValue(self):
        return self.value

    def SetValue(self, val):
        """Memperbarui nilai dari luar dan memperbarui tampilan slider"""
        self.value = float(max(self.min_val, min(val, self.max_val)))
        self.Refresh()