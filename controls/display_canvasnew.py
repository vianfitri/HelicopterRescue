import wx
from pubsub import pub

class DisplayCanvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # PRESET SKALA BACKGROUND & POSISI ACUAN (REFERENCE)
        self.bg_scale_preset = 2.8 
        self.ref_bg_x = -450  # Posisi acuan X (bisa bernilai negatif)
        self.ref_bg_y = 0  # Posisi acuan Y (bisa bernilai negatif)

        # load background image
        self.bg_image = wx.Image("assets/images/background.png")

        # load helicopter image
        self.img_heli_ori = wx.Image("assets/images/heli_R.png")

        # load base track image
        self.img_base_ori = wx.Image("assets/images/base_track_R.png")

        # load base trolley image
        self.img_trolley_ori = wx.Image("assets/images/base_trolley_R.png")

        # Reference Constants
        self.ref_pixel = 1322
        self.ref_meter = 12

        # cache bitmap & off-screen background buffer
        self.bg_buffer = None
        self.fg_buffer = None
        self.bg_bitmap = None
        self.base_bitmap = None
        self.fence_bitmap = None
        self.heli_bitmap = None
        self.trolley_bitmap = None

        # State Trackbar Control (0)
        self.trackbar_value = 0
        self.is_dragging_trackbar = False

        # Variabel Garis Vertikal Dinamis
        self.vertical_line_length = 50  # Panjang garis awal (dalam piksel terskala / unit)
        self.heli_ref_offset_x = 200    # Offset X acuan relatif dari pojok kiri gambar heli
        self.heli_ref_offset_y = 100    # Offset y acuan relatif dari pojok atas gambar heli

        # Calculated positions
        self.bg_x, self.bg_y = 0, 0
        self.heli_x, self.heli_y = 0, 0
        self.trolley_x, self.trolley_y = 0, 0
        self.base_x, self.base_y = 0, 0
        self.fence_x, self.fence_y = 0, 0

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)

        # Mouse Events untuk Interaksi Trackbar
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)

        # Safe cleanup ketika komponen dihancurkan
        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)

        # subscribe data plc1
        pub.subscribe(self.on_plc1_data, "modbus.data.plc1")

    def calculate_positions_from_trackbar(self, scale):
        """Menghitung posisi X Helicopter & Trolley berdasarkan nilai Trackbar (0..100)."""
        max_offset_x = int(round(710 * scale))
        current_offset = int(round((self.trackbar_value / 100.0) * max_offset_x))

        base_trolley_x = self.base_x + int(round(392 * scale))
        base_heli_x = int(round(40 * scale))

        self.trolley_x = base_trolley_x + current_offset
        self.heli_x = base_heli_x + current_offset

    def update_background_buffer(self, canvas_w, canvas_h, scale):
        """Render elemen-elemen statis ke buffer agar efisien."""
        if canvas_w <= 0 or canvas_h <= 0:
            return

        self.bg_buffer = wx.Bitmap(canvas_w, canvas_h)
        mem_dc_bg = wx.MemoryDC(self.bg_buffer)
        gc_bg = wx.GraphicsContext.Create(mem_dc_bg)

        if gc_bg:
            # 1. Render Warna Dasar Canvas
            gc_bg.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
            gc_bg.DrawRectangle(0, 0, canvas_w, canvas_h)

            # 2. Render Gambar Background Statis pada Posisi X & Y terskala (Mendukung koordinat negatif)
            if self.bg_bitmap and self.bg_bitmap.IsOk():
                gc_bg.DrawBitmap(
                    self.bg_bitmap,
                    self.bg_x, self.bg_y,
                    self.bg_bitmap.GetWidth(), self.bg_bitmap.GetHeight()
                )

            # 3. Render Base Track (Di atas gambar background)
            if self.base_bitmap and self.base_bitmap.IsOk():
                gc_bg.DrawBitmap(
                    self.base_bitmap,
                    self.base_x, self.base_y,
                    self.base_bitmap.GetWidth(), self.base_bitmap.GetHeight()
                )

        mem_dc_bg.SelectObject(wx.NullBitmap)

    def on_resize(self, event):
        canvas_w, canvas_h = self.GetClientSize()

        if canvas_w > 0 and canvas_h > 0:
            self.scale = canvas_w / 2500.0

            # ======================================
            # Background Image Scaling & Position Calculation
            # ======================================
            effective_bg_scale = self.scale * self.bg_scale_preset
            scaled_bg_w = max(1, int(round(self.bg_image.GetWidth() * effective_bg_scale)))
            scaled_bg_h = max(1, int(round(self.bg_image.GetHeight() * effective_bg_scale)))
            
            img_bg_scaled = self.bg_image.Scale(
                scaled_bg_w, 
                scaled_bg_h, 
                wx.IMAGE_QUALITY_HIGH
            )
            self.bg_bitmap = wx.Bitmap(img_bg_scaled)

            # Hitung posisi X dan Y terskala (mendukung nilai negatif)
            self.bg_x = int(round(self.ref_bg_x * self.scale))
            self.bg_y = int(round(self.ref_bg_y * self.scale))

            # Base Track Image Scaling
            img_base = self.img_base_ori.Scale(
                max(1, int(round(self.img_base_ori.GetWidth() * self.scale))),
                max(1, int(round(self.img_base_ori.GetHeight() * self.scale))),
                wx.IMAGE_QUALITY_HIGH  
            )
            self.base_bitmap = wx.Bitmap(img_base)

            # Trolley Image Scaling
            img_trolley = self.img_trolley_ori.Scale(
                max(1, int(round(self.img_trolley_ori.GetWidth() * self.scale))),
                max(1, int(round(self.img_trolley_ori.GetHeight() * self.scale))),
                wx.IMAGE_QUALITY_HIGH
            )
            self.trolley_bitmap = wx.Bitmap(img_trolley)

            # Helicopter Image Scaling
            heli_pixel, heli_meter = 508, 5.05
            ref_scale = self.ref_pixel / self.ref_meter

            heli_w_meter = 1380 * heli_meter / heli_pixel
            heli_h_meter = 752 * heli_meter / heli_pixel

            new_heli_w = heli_w_meter * ref_scale
            new_heli_h = heli_h_meter * ref_scale

            img_heli = self.img_heli_ori.Scale(
                max(1, int(round(new_heli_w * self.scale))),
                max(1, int(round(new_heli_h * self.scale))),
                wx.IMAGE_QUALITY_HIGH
            )
            self.heli_bitmap = wx.Bitmap(img_heli)

            # Calculate Coordinate position
            self.base_x = int(round(467 * self.scale))
            self.base_y = int(round(309 * self.scale))
            self.trolley_x = self.base_x + int(round(412 * self.scale))
            self.trolley_y = self.base_y + int(round(319 * self.scale))
            self.heli_x = int(round(40 * self.scale))
            self.heli_y = 0

            # Hitung geometri Trackbar sesuai skala
            self.trackbar_x = self.base_x + int(round(592 * self.scale))
            self.trackbar_y = self.base_y + self.base_bitmap.GetHeight() + 15
            self.trackbar_length = int(round(710 * self.scale))

            # Hitung posisi X dinamis berdasarkan nilai trackbar
            self.calculate_positions_from_trackbar(self.scale)

            # Update Background Buffer Statis (Menggambar bg_bitmap + base_bitmap)
            self.update_background_buffer(canvas_w, canvas_h, self.scale)

        self.Refresh(False)
        event.Skip()

    # =======================================================
    # HELPER DYNAMIC CONFIGURATION
    # =======================================================
    def set_bg_config(self, preset_scale=None, ref_x=None, ref_y=None):
        """Method untuk mengubah konfigurasi background secara dinamis."""
        if preset_scale is not None:
            self.bg_scale_preset = float(preset_scale)
        if ref_x is not None:
            self.ref_bg_x = int(ref_x)
        if ref_y is not None:
            self.ref_bg_y = int(ref_y)

        canvas_w, canvas_h = self.GetClientSize()
        if canvas_w > 0 and canvas_h > 0:
            self.on_resize(wx.SizeEvent())

    # =======================================================
    # INTERAKSI MOUSE UNTUK TRACKBAR
    # =======================================================
    def get_thumb_rect(self):
        ratio = self.trackbar_value / 100.0
        thumb_center_x = self.trackbar_x + int(round(ratio * self.trackbar_length))
        radius = int(round(10 * getattr(self, 'scale', 1.0)))
        return wx.Rect(thumb_center_x - radius, self.trackbar_y - radius, radius * 2, radius * 2)

    def update_value_from_mouse(self, mouse_x):
        rel_x = mouse_x - self.trackbar_x
        rel_x = max(0, min(self.trackbar_length, rel_x))
        
        ratio = rel_x / float(self.trackbar_length) if self.trackbar_length > 0 else 0
        self.trackbar_value = int(round(ratio * 100))
        
        self.calculate_positions_from_trackbar(self.scale)
        self.Refresh(False)

    def on_mouse_down(self, event):
        pos = event.GetPosition()
        thumb_rect = self.get_thumb_rect()
        thumb_rect.Inflate(5, 5)
        
        if thumb_rect.Contains(pos):
            self.is_dragging_trackbar = True
            self.CaptureMouse()
        elif self.trackbar_x <= pos.x <= (self.trackbar_x + self.trackbar_length) and \
             abs(pos.y - self.trackbar_y) <= 15:
            self.is_dragging_trackbar = True
            if self.HasCapture():
                self.ReleaseMouse()
            self.CaptureMouse()
            self.update_value_from_mouse(pos.x)

    def on_mouse_move(self, event):
        if self.is_dragging_trackbar and event.Dragging():
            self.update_value_from_mouse(event.GetPosition().x)

    def on_mouse_up(self, event):
        if self.is_dragging_trackbar:
            self.is_dragging_trackbar = False
            if self.HasCapture():
                self.ReleaseMouse()

    def update_positions(self, heli_pos=None, trolley_pos=None):
        if heli_pos:
            self.heli_x, self.heli_y = heli_pos
        if trolley_pos:
            self.trolley_x, self.trolley_y = trolley_pos
            
        self.Refresh(False)

    # =======================================================
    # RENDERING GARIS VERTIKAL
    # =======================================================
    def draw_vertical_line(self, gc):
        """Menggambar garis vertikal yang menempel pada titik tertentu di Helikopter."""
        if not self.heli_bitmap or not self.heli_bitmap.IsOk():
            return

        scale = getattr(self, 'scale', 1.0)

        # Hitung titik awal X & Y berdasarkan offset posisi helikopter
        start_x = self.heli_x + int(round(self.heli_ref_offset_x * scale))
        start_y = self.heli_y + int(round(self.heli_ref_offset_y * scale))

        # Hitung titik akhir Y berdasarkan panjang garis terskala
        scaled_line_len = int(round(self.vertical_line_length * scale))
        end_y = start_y + scaled_line_len

        # Atur style garis (warna merah, ketebalan 2px)
        gc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))
        gc.StrokeLine(start_x, start_y, start_x, end_y)

    # =======================================================
    # RENDERING
    # =======================================================
    def draw_trackbar(self, gc):
        gc.SetPen(wx.Pen(wx.Colour(120, 140, 160), 4))
        gc.StrokeLine(self.trackbar_x, self.trackbar_y, self.trackbar_x + self.trackbar_length, self.trackbar_y)

        gc.SetPen(wx.Pen(wx.Colour(80, 90, 100), 2))
        tick_h = 8
        gc.StrokeLine(self.trackbar_x, self.trackbar_y - tick_h, self.trackbar_x, self.trackbar_y + tick_h)
        gc.StrokeLine(self.trackbar_x + self.trackbar_length, self.trackbar_y - tick_h, 
                      self.trackbar_x + self.trackbar_length, self.trackbar_y + tick_h)

        ratio = self.trackbar_value / 100.0
        thumb_x = self.trackbar_x + int(round(ratio * self.trackbar_length))
        radius = 10

        fill_color = wx.Colour(255, 128, 0) if self.is_dragging_trackbar else wx.Colour(0, 120, 215)
        gc.SetBrush(wx.Brush(fill_color))
        gc.SetPen(wx.Pen(wx.Colour(255, 255, 255), 2))
        gc.DrawEllipse(thumb_x - radius, self.trackbar_y - radius, radius * 2, radius * 2)

        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, wx.Colour(50, 50, 50))
        gc.DrawText("0 m", self.trackbar_x - 30, self.trackbar_y - 8)
        gc.DrawText("4.5 m", self.trackbar_x + self.trackbar_length + 10, self.trackbar_y - 8)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if not gc or not self.bg_buffer or not self.bg_buffer.IsOk():
            return

        # Render background buffer (sudah termasuk background.png di koordinat terskala dan base_track)
        gc.DrawBitmap(self.bg_buffer, 0, 0, self.bg_buffer.GetWidth(), self.bg_buffer.GetHeight())

        # Render objek bergerak (helicopter & trolley)
        if self.heli_bitmap and self.heli_bitmap.IsOk():
            gc.DrawBitmap(
                self.heli_bitmap,
                self.heli_x, self.heli_y,
                self.heli_bitmap.GetWidth(), self.heli_bitmap.GetHeight()
            )

        if self.trolley_bitmap and self.trolley_bitmap.IsOk():
            gc.DrawBitmap(
                self.trolley_bitmap,
                self.trolley_x, self.trolley_y,
                self.trolley_bitmap.GetWidth(), self.trolley_bitmap.GetHeight()
            )

        self.draw_vertical_line(gc)
        self.draw_trackbar(gc)

    def on_plc1_data(self, data):
        def _update():
            if "V1004" in data:
                travel_val = data["V1004"]
                self.trackbar_value = max(0, min(100, float(travel_val)))

                if hasattr(self, 'scale'):
                    self.calculate_positions_from_trackbar(self.scale)
                
                self.Refresh(False)

        wx.CallAfter(_update)

    def on_destroy(self, event):
        pub.unsubscribe(self.on_plc1_data, "modbus.data.plc1")
        event.Skip()