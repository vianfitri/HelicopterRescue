import wx

from pubsub import pub
from assets.theme import Theme
from controls.display_canvasnew import DisplayCanvas
from controls.horizontal_slider import HorizontalSlider
from controls.vertical_slider import VerticalSlider

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
            size=(-1, 300),
        )
        sizer.Add(
            self.hoist_slider,
            0,
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