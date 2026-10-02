import wx
from .tab_button_new import TabButton, EVT_TAB_SELECTED

class CardStatus(wx.Control):
    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, style=wx.NO_BORDER)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetMinSize((200, 90))

        # Cache Font & Color agar tidak re-create di EVT_PAINT
        self.title_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.content_font = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.white_color = wx.Colour(255, 255, 255)
        self.green_color = wx.Colour(46, 204, 113)
        self.card_bg_color = wx.Colour(35, 42, 52)

        self.Bind(wx.EVT_PAINT, self._on_paint)

    def DoGetBestSize(self):
        return wx.Size(200, 90)

    def _on_paint(self, event):
        # Gunakan wx.PaintDC karena SetBackgroundStyle(wx.BG_STYLE_PAINT) & SetDoubleBuffered(True) aktif
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()
        if w <= 0 or h <= 0:
            return

        # Clear background warna sidebar
        bg_color = self.GetParent().GetBackgroundColour()
        gc.SetBrush(gc.CreateBrush(wx.Brush(bg_color)))
        gc.DrawRectangle(0, 0, w, h)

        # 1. Background Card
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.card_bg_color)))
        gc.SetPen(wx.NullPen)
        gc.DrawRoundedRectangle(4, 2, w - 8, h - 4, 6)

        padding_x = 16
        padding_y = 14

        # 2. Baris 1: DATA CONNECTION
        gc.SetFont(self.title_font, self.white_color)
        gc.DrawText("DATA CONNECTION", padding_x, padding_y)

        # 3. Baris 2: HELICOPTER (Kiri)
        row2_y = padding_y + 28
        gc.SetFont(self.content_font, self.white_color)
        gc.DrawText("HELICOPTER", padding_x, row2_y)

        # 4. Baris 2: CONNECTED (Kanan)
        status_text = "CONNECTED"
        gc.SetFont(self.content_font, self.green_color)
        status_w, _ = gc.GetTextExtent(status_text)
        status_x = w - padding_x - status_w
        gc.DrawText(status_text, status_x, row2_y)


class SidebarControl(wx.Panel):
    def __init__(self, parent, on_tab_changed=None):
        super().__init__(parent, id=wx.ID_ANY, style=wx.NO_BORDER)
        self.SetBackgroundColour(wx.Colour(8, 15, 25))
        self.SetDoubleBuffered(True)
        self.SetMinSize((210, -1))
        self.SetMaxSize((250, -1))

        self.on_tab_changed = on_tab_changed
        self.buttons = []
        self.active_tab_index = 0

        # Load Logo
        self.logo_bitmap = self._load_and_scale_logo("assets/images/PPS_logo.png", target_width=100)
        self.border_pen = wx.Pen(wx.Colour(43, 49, 61), 1)

        self._init_ui()
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def _load_and_scale_logo(self, image_path, target_width=100):
        image = wx.Image(image_path, wx.BITMAP_TYPE_PNG)
        if not image.IsOk():
            return None

        orig_w, orig_h = image.GetWidth(), image.GetHeight()
        aspect_ratio = orig_h / orig_w
        target_height = int(target_width * aspect_ratio)

        scaled_image = image.Scale(target_width, target_height, wx.IMAGE_QUALITY_BOX_AVERAGE)
        return scaled_image.ConvertToBitmap()

    def _init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header Logo menggunakan StaticBitmap langsung (lebih bersih dari Sub-Panel Paint)
        main_sizer.AddSpacer(20)
        if self.logo_bitmap and self.logo_bitmap.IsOk():
            logo_ctrl = wx.StaticBitmap(self, bitmap=self.logo_bitmap)
            main_sizer.Add(logo_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL)
        else:
            main_sizer.AddSpacer(60) # Spacer pengganti jika logo gagal load

        main_sizer.AddSpacer(20)

        # Tab Buttons
        tab_definitions = [
            (0, "TRAINING", "helicopter.svg"),
            (1, "SETTINGS", "gear-icon.svg"),
        ]

        for tab_id, label, icon_type in tab_definitions:
            btn = TabButton(self, tab_id=tab_id, label=label, icon_type=icon_type)
            btn.Bind(EVT_TAB_SELECTED, self._on_tab_click)
            self.buttons.append(btn)
            main_sizer.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        main_sizer.AddStretchSpacer(1)

        # Status Card
        self.status_card = CardStatus(self)
        main_sizer.Add(self.status_card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.SetSizer(main_sizer)
        self.select_tab(0)

    def _on_tab_click(self, event):
        self.select_tab(event.tab_id)

    def select_tab(self, index: int):
        self.active_tab_index = index
        for idx, btn in enumerate(self.buttons):
            btn.set_selected(idx == index)

        if self.on_tab_changed:
            self.on_tab_changed(index)

    def _on_paint(self, event):
        dc = wx.PaintDC(self)
        w, h = self.GetClientSize()

        # Garis pembatas vertikal sebelah kanan sidebar
        dc.SetPen(self.border_pen)
        dc.DrawLine(w - 1, 0, w - 1, h)