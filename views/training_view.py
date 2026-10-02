import wx

from pubsub import pub
from assets.theme import Theme
from controls.display_canvas import DisplayCanvas
from controls.horizontal_slider import HorizontalSlider

class VerticalSlider(wx.Panel):

    def __init__(
        self,
        parent,
        value=0.0,
        min_val=0.0,
        max_val=100.0,
        size=(40, 180),
        active_color=wx.Colour(45, 147, 226),
    ):
        super().__init__(
            parent, size=size, style=wx.NO_BORDER | wx.BG_STYLE_PAINT
        )
        self.SetDoubleBuffered(True)

        self._min_val = float(min_val)
        self._max_val = float(max_val)
        self._value = float(value)
        self._active_color = active_color
        self._track_color = wx.Colour(32, 38, 48)
        self._thumb_color = wx.Colour(255, 255, 255)

        self._is_dragging = False

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)

    def SetValue(self, val):
        # Transisi dan pembatasan nilai 0 - 100
        self._value = max(self._min_val, min(self._max_val, float(val)))
        self.Refresh()

    def GetValue(self):
        return self._value

    def _val_to_y(self, val, track_top, track_height):
        # Pergerakan dari ATAS (min_val = 0) ke BAWAH (max_val = 100)
        norm = (val - self._min_val) / (self._max_val - self._min_val)
        return track_top + norm * track_height

    def _y_to_val(self, y, track_top, track_height):
        norm = (y - track_top) / track_height
        norm = max(0.0, min(1.0, norm))
        return self._min_val + norm * (self._max_val - self._min_val)

    def _get_layout_bounds(self):
        w, h = self.GetClientSize()
        thumb_radius = 8
        track_w = 6
        track_x = (w - track_w) / 2
        track_top = thumb_radius + 4
        track_bottom = h - thumb_radius - 4
        track_height = max(1, track_bottom - track_top)
        return (
            w,
            h,
            track_x,
            track_top,
            track_w,
            track_height,
            thumb_radius,
        )

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        (
            w,
            h,
            track_x,
            track_top,
            track_w,
            track_height,
            thumb_radius,
        ) = self._get_layout_bounds()

        # Canvas background (sesuai warna card parent)
        gc.SetBrush(wx.Brush(wx.Colour(17, 19, 23)))
        gc.DrawRectangle(0, 0, w, h)

        # 1. Base Track (Rounded Rectangle background)
        gc.SetPen(wx.NullPen)
        gc.SetBrush(wx.Brush(self._track_color))
        gc.DrawRoundedRectangle(
            track_x, track_top, track_w, track_height, track_w / 2
        )

        # 2. Active Track Fill (dari atas ke posisi thumb)
        thumb_y = self._val_to_y(self._value, track_top, track_height)
        active_h = thumb_y - track_top
        if active_h > 0:
            gc.SetBrush(wx.Brush(self._active_color))
            gc.DrawRoundedRectangle(
                track_x, track_top, track_w, active_h, track_w / 2
            )

        # 3. Bulat Thumb (Knob)
        gc.SetBrush(wx.Brush(self._thumb_color))
        gc.SetPen(wx.Pen(self._active_color, 2))
        gc.DrawEllipse(
            w / 2 - thumb_radius,
            thumb_y - thumb_radius,
            thumb_radius * 2,
            thumb_radius * 2,
        )

    def _on_mouse_down(self, event):
        self._is_dragging = True
        self.CaptureMouse()
        self._update_from_mouse(event.GetPosition())

    def _on_mouse_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self._is_dragging = False

    def _on_mouse_move(self, event):
        if self._is_dragging and event.Dragging():
            self._update_from_mouse(event.GetPosition())

    def _update_from_mouse(self, pos):
        _, _, _, track_top, _, track_height, _ = (
            self._get_layout_bounds()
        )
        new_val = self._y_to_val(pos.y, track_top, track_height)
        self.SetValue(new_val)

class LongitudinalCard(wx.Panel):

    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.NO_BORDER
        )
        self.SetBackgroundColour(wx.Colour(17, 19, 23))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetMinSize((232, -1))

        self.Bind(wx.EVT_PAINT, self._on_paint)

        # subscribe data plc1
        #pub.subscribe(self.on_plc1_data, "modbus.data.plc1")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(12)

        # title label
        title_lbl = wx.StaticText(self, label="LONGITUDINAL POSITION")
        title_lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        title_lbl.SetFont(Theme.get_font(size=8, family=wx.FONTFAMILY_DEFAULT, bold=True))

        sizer.Add(title_lbl, 0, wx.LEFT | wx.RIGHT, 14)
        sizer.AddSpacer(14)

        # value label and unit
        val_lbl = wx.StaticText(self, label="2.35")
        val_lbl.SetForegroundColour(wx.Colour(255, 94, 19))
        val_lbl.SetFont(Theme.get_font(size=28, weight=wx.FONTWEIGHT_HEAVY, bold=True))

        unit_lbl = wx.StaticText(self, label="m")
        unit_lbl.SetForegroundColour(wx.Colour(255, 94, 19))
        unit_lbl.SetFont(Theme.get_font(size=11, family=wx.FONTFAMILY_DEFAULT, weight=wx.FONTWEIGHT_HEAVY))
        
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(val_lbl, 0, wx.ALIGN_BOTTOM, 0)
        row_sizer.Add(unit_lbl, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.BOTTOM, 3)
        
        sizer.Add(row_sizer, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 14)
        sizer.AddSpacer(12)

        # Slider Longitudinal
        longitudinal_slider = HorizontalSlider(self, value=5.0, min_val=0.0, max_val=10.0, size=(-1, 65))
        sizer.Add(longitudinal_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer(6)

        self.SetSizer(sizer)

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return
        w, h = self.GetClientSize()

        # Border
        gc.SetPen(wx.Pen(wx.Colour(43, 49, 61), 1))
        gc.SetBrush(wx.Brush(wx.Colour(17, 19, 23)))
        gc.DrawRoundedRectangle(0, 0, w - 1, h - 1, 6)
    
class HoistCard(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent, style=wx.NO_BORDER)

        self.SetBackgroundColour(wx.Colour(17, 19, 23))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetMinSize((180, -1))

        self.Bind(wx.EVT_PAINT, self._on_paint)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(12)

        # title label
        title_lbl = wx.StaticText(self, label="HOIST LENGTH")
        title_lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        title_lbl.SetFont(
            Theme.get_font(size=8, family=wx.FONTFAMILY_DEFAULT, bold=True)
        )

        sizer.Add(title_lbl, 0, wx.LEFT | wx.RIGHT, 14)
        sizer.AddSpacer(14)

        # value label and unit
        self.val_lbl = wx.StaticText(self, label="0.00")
        self.val_lbl.SetForegroundColour(wx.Colour(45, 147, 226))
        self.val_lbl.SetFont(
            Theme.get_font(
                size=28,
                family=wx.FONTFAMILY_DEFAULT,
                weight=wx.FONTWEIGHT_HEAVY,
            )
        )

        unit_lbl = wx.StaticText(self, label="m")
        unit_lbl.SetForegroundColour(wx.Colour(45, 147, 226))
        unit_lbl.SetFont(
            Theme.get_font(
                size=11,
                family=wx.FONTFAMILY_DEFAULT,
                weight=wx.FONTWEIGHT_HEAVY,
            )
        )

        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(self.val_lbl, 0, wx.ALIGN_BOTTOM, 0)
        row_sizer.Add(
            unit_lbl, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.BOTTOM, 3
        )

        sizer.Add(row_sizer, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 14)
        sizer.AddSpacer(12)

        # Vertical Slider (0 ke 100 dari Atas ke Bawah)
        self.hoist_slider = VerticalSlider(
            self,
            value=0.0,
            min_val=0.0,
            max_val=100.0,
            size=(-1, 120),
            active_color=wx.Colour(45, 147, 226),
        )
        sizer.Add(
            self.hoist_slider,
            1,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10,
        )

        self.SetSizer(sizer)

        # Subscribe ke data modbus plc1
        pub.subscribe(self.on_plc1_data, "modbus.data.plc1")

    def on_plc1_data(self, data):
        """Menerima data pubsub dari thread worker"""
        wx.CallAfter(self._update_ui, data)

    def _update_ui(self, data):
        """Mengupdate GUI di main UI thread"""
        if isinstance(data, dict) and "V124" in data:
            try:
                # Ambil persentase (0 - 100)
                percentage = float(data["V124"])
                percentage = max(0.0, min(100.0, percentage))

                # Update posisi slider
                self.hoist_slider.SetValue(percentage)

                # Hitung nilai panjang dalam meter (0% = 0.0m, 100% = 9.0m)
                length_m = (percentage / 100.0) * 9.0
                self.val_lbl.SetLabel(f"{length_m:.2f}")

                self.Layout()
            except (ValueError, TypeError):
                pass

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return
        w, h = self.GetClientSize()

        # Border
        gc.SetPen(wx.Pen(wx.Colour(43, 49, 61), 1))
        gc.SetBrush(wx.Brush(wx.Colour(17, 19, 23)))
        gc.DrawRoundedRectangle(0, 0, w - 1, h - 1, 6)

class DisplayCard(wx.Panel):
    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.NO_BORDER
        )

        self.SetBackgroundColour(wx.Colour(17, 19, 23))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)

        self.Bind(wx.EVT_PAINT, self._on_paint)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # helicopter canvas
        heli_canvas = DisplayCanvas(self)
        sizer.Add(heli_canvas, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()

        # Border
        gc.SetPen(wx.Pen(wx.Colour(43, 49, 61), 1))
        gc.SetBrush(wx.Brush(wx.Colour(17, 19, 23)))
        gc.DrawRoundedRectangle(0, 0, w - 1, h - 1, 6)

class TrainingView(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent, style=wx.NO_BORDER)
        self.SetBackgroundColour(wx.Colour(17, 19, 23))
        self.SetDoubleBuffered(True)

        self._init_ui()

    def _init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(18)

        # View Title Section
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_font = wx.Font(Theme.get_font(size=10, bold=True))

        bullet_lbl = wx.StaticText(self, label="●")
        bullet_lbl.SetForegroundColour(wx.Colour(255, 94, 19))
        bullet_lbl.SetFont(lbl_font)
        lbl_W, _ = bullet_lbl.GetTextExtent(" ")
        title_lbl = wx.StaticText(self, label="TRAINING VIEW")
        title_lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        title_lbl.SetFont(lbl_font)

        header_sizer.Add(bullet_lbl, 0, wx.LEFT, 24)
        header_sizer.AddSpacer(lbl_W)
        header_sizer.Add(title_lbl, 0, wx.RIGHT, 24)

        main_sizer.Add(header_sizer, 0, wx.EXPAND)
        main_sizer.AddSpacer(16)

        # Content
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_content_sizer = wx.BoxSizer(wx.VERTICAL)

        longitudinal_card = LongitudinalCard(self)
        left_content_sizer.Add(longitudinal_card, 1, wx.EXPAND | wx.RIGHT, 12)

        content_sizer.Add(left_content_sizer, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 24)

        panel_view = DisplayCard(self)
        content_sizer.Add(panel_view, 1, wx.EXPAND | wx.BOTTOM, 24)

        right_content_sizer = wx.BoxSizer(wx.VERTICAL)

        hoist_card = HoistCard(self)
        right_content_sizer.Add(hoist_card, 1, wx.EXPAND | wx.LEFT, 12)

        content_sizer.Add(right_content_sizer, 0, wx.EXPAND | wx.RIGHT | wx.BOTTOM, 24)

        main_sizer.Add(content_sizer, 1, wx.EXPAND)

        self.SetSizer(main_sizer)