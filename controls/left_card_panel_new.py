import wx

class RoundedCardPanel(wx.Panel):
    """
    Panel Card kustom dengan Rounded Corners (radius 6px), Border 1px,
    Background transparan/menyatu, serta Line Shadow pembatas Title.
    """
    def __init__(self, parent, title="", bg_color=wx.Colour(8, 16, 25), border_color=wx.Colour(40, 58, 82), radius=6):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)  # Cegah flickering saat repaint
        
        self.card_bg_color = bg_color
        self.card_border_color = border_color
        self.corner_radius = radius
        self.card_title = title
        
        # Sizer utama untuk isi di dalam card
        self.card_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 1. Judul Card (Title)
        self.title_text = wx.StaticText(self, label=self.card_title)
        self.title_text.SetForegroundColour(wx.Colour(220, 230, 242))
        self.title_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Inner padding Title (Atas, Kiri, Kanan)
        self.card_sizer.Add(self.title_text, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        
        # Space kosong setinggi 12px untuk area Line Shadow
        self.card_sizer.AddSpacer(12)
        
        # 2. Container Konten Card
        self.content_panel = wx.Panel(self)
        self.content_panel.SetBackgroundColour(self.card_bg_color)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        
        # Padding Konten (Bawah, Kiri, Kanan)
        self.card_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        
        self.SetSizer(self.card_sizer)
        
        # Event binding untuk custom drawing (Border, Rounded Corner & Line Shadow)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)

    def _on_erase_background(self, event):
        # mencegah OS membersihkan background dengan warna default (putih/grey bawaan)
        pass

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)

        # 2. Ambil warna background asli dari induk (parent) agar area sudut menyatu
        parent_bg = self.GetParent().GetBackgroundColour()
        dc.SetBackground(wx.Brush(parent_bg))
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return
            
        width, height = self.GetClientSize()
        if width <= 0 or height <= 0:
            return
            
        # --- A. Gambar Background Card dengan Rounded Rectangle ---
        path = gc.CreatePath()
        # Offset 0.5px agar garis border terlihat tajam (anti-aliasing)
        x, y, w, h = 0.5, 0.5, width - 1.0, height - 1.0
        path.AddRoundedRectangle(x, y, w, h, self.corner_radius)
        
        # Fill Background & Draw Border 1px
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.card_bg_color)))
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self.card_border_color).Width(1)))
        gc.DrawPath(path)
        
        # --- B. Gambar Line Shadow (Divider Bergradasi di Bawah Title) ---
        title_rect = self.title_text.GetRect()
        line_y = title_rect.Bottom + 6  # Tepat di bawah Title
        
        # Garis Utama (Line Brightness Netral)
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(45, 65, 90, 255)).Width(1)))
        gc.StrokeLine(12, line_y, width - 12, line_y)
        
        # Garis Bayangan / Soft Shadow di bawahnya (Semi Transparan)
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(10, 16, 26, 120)).Width(1)))
        gc.StrokeLine(12, line_y + 1, width - 12, line_y + 1)

    def get_content_panel(self):
        """Method pembantu untuk menambahkan widget/konten ke dalam card"""
        return self.content_panel


class LeftCardContent(wx.Panel):
    """
    Panel Container yang diletakkan di dalam self.left_card.
    Berisi 5 Vertical Rounded Cards.
    """
    def __init__(self, parent):
        super().__init__(parent)
        
        # Samakan warna background induk
        self.SetBackgroundColour(wx.Colour(8, 16, 25))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Skema Warna
        CARD_BG = wx.Colour(14, 25, 38)        # Sedikit lebih gelap agar terlihat kontras
        CARD_BORDER = wx.Colour(42, 60, 84)    # Border 1px subtle
        
        # Data 5 Card
        cards_data = [
            ("MISSION CONTROL", ["Status: ACTIVE", "Mode: AUTOMATIC", "Priority: HIGH"]),
            ("RESCUE TEAM", ["Units: 4 Active", "Personnel: 12 On Duty", "Leader: Alpha-1"]),
            ("ENVIRONMENTAL DATA", ["Temp: 24°C", "Humidity: 65%", "Wind: 12 km/h NE"]),
            ("COMMUNICATION", ["Signal: STABLE", "Freq: 433.500 MHz", "Latency: 14ms"]),
            ("SYSTEM HEALTH", ["Battery: 92%", "Storage: 128/512 GB", "Uptime: 04h 12m"])
        ]
        
        for idx, (title, items) in enumerate(cards_data):
            card = RoundedCardPanel(self, title=title, bg_color=CARD_BG, border_color=CARD_BORDER, radius=6)
            
            # Isi konten ke dalam card
            card_content = card.get_content_panel()
            content_sizer = card.content_sizer
            
            for item in items:
                txt = wx.StaticText(card_content, label=f"• {item}")
                txt.SetForegroundColour(wx.Colour(160, 180, 205))
                txt.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                content_sizer.Add(txt, 0, wx.BOTTOM, 4)
                
            # Tambahkan card ke sizer utama dengan gap vertical = 12px
            bottom_margin = 12 if idx < len(cards_data) - 1 else 0
            main_sizer.Add(card, 0, wx.EXPAND | wx.BOTTOM, bottom_margin)
            
        self.SetSizer(main_sizer)