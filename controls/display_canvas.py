import wx

from pubsub import pub

class DisplayCanvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

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
        self.base_bitmap = None
        self.fence_bitmap = None
        self.heli_bitmap = None
        self.trolley_bitmap = None

        # State Trackbar Control (0)
        self.trackbar_value = 0
        self.is_dragging_trackbar = False

        # default position
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
        # Rentang pergerakan horizontal (Offset X)
        # 0 = Kanan (posisi dasar), 100 = Kiri (bergeser sejauh jarak lintasan)
        max_offset_x = int(round(710 * scale))
        
        # Invert logika: 0 di kanan (offset = 0), 100 di kiri (offset = max_offset_x)
        current_offset = int(round((self.trackbar_value / 100.0) * max_offset_x))

        # Posisi dasar (Kanan)
        base_trolley_x = self.base_x + int(round(392 * scale))
        base_heli_x = int(round(40 * scale))

        # Geser ke kiri berdasarkan trackbar
        self.trolley_x = base_trolley_x + current_offset
        self.heli_x = base_heli_x + current_offset

    def update_background_buffer(self, canvas_w, canvas_h, scale):
        # render fence and base once at resize
        if canvas_w <= 0 or canvas_h <= 0:
            return

        self.bg_buffer = wx.Bitmap(canvas_w, canvas_h)
        mem_dc_bg = wx.MemoryDC(self.bg_buffer)
        gc_bg = wx.GraphicsContext.Create(mem_dc_bg)

        if gc_bg:
            # Render Background Color
            gc_bg.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
            gc_bg.DrawRectangle(0, 0, canvas_w, canvas_h)

            # Render Base Track (Statis Depan)
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

            img_base = self.img_base_ori.Scale(
                max(1, int(round(self.img_base_ori.GetWidth() * self.scale))),
                max(1, int(round(self.img_base_ori.GetHeight() * self.scale))),
                wx.IMAGE_QUALITY_HIGH  
            )
            self.base_bitmap = wx.Bitmap(img_base)

            img_trolley = self.img_trolley_ori.Scale(
                max(1, int(round(self.img_trolley_ori.GetWidth() * self.scale))),
                max(1, int(round(self.img_trolley_ori.GetHeight() * self.scale))),
                wx.IMAGE_QUALITY_HIGH
            )
            self.trolley_bitmap = wx.Bitmap(img_trolley)

            # helicopter resize calculate
            heli_pixel, heli_meter = 508, 5.05
            ref_scale = self.ref_pixel / self.ref_meter

            heli_w_meter = 1380 * heli_meter / heli_pixel
            heli_h_meter = 752 * heli_meter / heli_pixel

            new_heli_w = heli_w_meter * ref_scale
            new_heli_h = heli_h_meter * ref_scale

            # scale image heli
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
            self.trackbar_y = self.base_y + self.base_bitmap.GetHeight() + 15 # Di bawah base_track
            self.trackbar_length = int(round(710 * self.scale))

            # Hitung posisi X dinamis berdasarkan nilai trackbar
            self.calculate_positions_from_trackbar(self.scale)

            # Update Background Buffer Statis
            self.update_background_buffer(canvas_w, canvas_h, self.scale)

        self.Refresh(False)
        event.Skip()

    # =======================================================
    # INTERAKSI MOUSE UNTUK TRACKBAR
    # =======================================================
    def get_thumb_rect(self):
        """Mendapatkan bounding box dari tombol/thumb trackbar untuk deteksi klik."""
        # 0 = Kanan, 100 = Kiri
        ratio = self.trackbar_value / 100.0
        thumb_center_x = self.trackbar_x + int(round(ratio * self.trackbar_length))
        
        radius = int(round(10 * getattr(self, 'scale', 1.0)))
        return wx.Rect(thumb_center_x - radius, self.trackbar_y - radius, radius * 2, radius * 2)

    def update_value_from_mouse(self, mouse_x):
        """Memperbarui nilai trackbar (0-100) berdasarkan koordinat mouse."""
        rel_x = mouse_x - self.trackbar_x
        rel_x = max(0, min(self.trackbar_length, rel_x)) # Clamp nilai
        
        # 0 di kanan, 100 di kiri
        ratio = rel_x / float(self.trackbar_length) if self.trackbar_length > 0 else 0
        self.trackbar_value = int(round(ratio * 100))
        
        # Perbarui posisi gambar dinamis
        self.calculate_positions_from_trackbar(self.scale)
        self.Refresh(False)

    def on_mouse_down(self, event):
        pos = event.GetPosition()
        thumb_rect = self.get_thumb_rect()
        
        # Perbesar hit-area sedikit agar mudah di-klik
        thumb_rect.Inflate(5, 5)
        
        if thumb_rect.Contains(pos):
            self.is_dragging_trackbar = True
            self.CaptureMouse()
        elif self.trackbar_x <= pos.x <= (self.trackbar_x + self.trackbar_length) and \
             abs(pos.y - self.trackbar_y) <= 15:
            # Klik langsung pada garis trackbar
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

    def on_size(self, event):
        # Canvas size 
        canvas_w, canvas_h = self.GetClientSize()

        image_base = self.base_image
        image_trolley = self.base_trolley_image
        image_fence = self.base_fence_image
        image_heli = self.heli_image

        print(f"canvas w: {canvas_w}, canvas h: {canvas_h}")

        # image resize
        if canvas_w > 0 and canvas_h > 0:
            scale = canvas_w / 2500 # minimum lebar gambar dengan referensi base

            print(f"scale: {scale}")
            print(f"base w: {image_base.GetWidth()}, base h: {image_base.GetHeight()}")

            # ======================================
            # base image scaling
            image_base = image_base.Scale(
                int(round(image_base.GetWidth() * scale)),
                int(round(image_base.GetHeight() * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create base bitmap
            self.base_bitmap = wx.Bitmap(image_base)

            # set position of base bitmap image
            self.base_x = int(round(110 * scale)) # pos x jika lebar gambar max 2500
            self.base_y = int(round(309 * scale))

            # ======================================
            # trolley image scaling
            image_trolley = image_trolley.Scale(
                int(round(image_trolley.GetWidth() * scale)),
                int(round(image_trolley.GetHeight() * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create trolley bitmap
            self.trolley_bitmap = wx.Bitmap(image_trolley)

            # set position of trolley bitmap image
            self.trolley_x = self.base_x + int(round(1102 * scale))
            self.trolley_y = self.base_y + int(round(319 * scale))

            # ======================================
            # fence image scaling
            image_fence = image_fence.Scale(
                int(round(image_fence.GetWidth() * scale)),
                int(round(image_fence.GetHeight() * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create fence bitmap
            self.fence_bitmap = wx.Bitmap(image_fence)

            # set position of fence bitmap image
            self.fence_x = self.base_x + int(round(1182 * scale))
            self.fence_y = self.base_y + int(round(272 * scale))

            # ======================================
            # helicopter image scaling
            heli_pixel = 510
            heli_meter = 5.05

            ref_scale = self.ref_pixel / self.ref_meter
            heli_image_meter_width = 1408 * heli_meter / heli_pixel
            heli_image_meter_height = 768 * heli_meter / heli_pixel
            new_heli_width = heli_image_meter_width * ref_scale
            new_heli_height = heli_image_meter_height * ref_scale

            image_heli = image_heli.Scale(
                int(round(new_heli_width * scale)),
                int(round(new_heli_height * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create heli bitmap
            self.heli_bitmap = wx.Bitmap(image_heli)

            # set position of heli bitmap image
            self.heli_x = int(round(910 * scale))
            self.heli_y = 0
            
        self.Refresh()
        event.Skip()

    # =======================================================
    # RENDERING
    # =======================================================
    def draw_trackbar(self, gc):
        """Menggambar visual trackbar secara kustom menggunakan GraphicsContext."""
        # 1. Garis Lintasan Trackbar (Track Rail)
        gc.SetPen(wx.Pen(wx.Colour(120, 140, 160), 4))
        gc.StrokeLine(self.trackbar_x, self.trackbar_y, self.trackbar_x + self.trackbar_length, self.trackbar_y)

        # 2. Tanda Batas Kiri & Kanan (Ticks)
        gc.SetPen(wx.Pen(wx.Colour(80, 90, 100), 2))
        tick_h = 8
        gc.StrokeLine(self.trackbar_x, self.trackbar_y - tick_h, self.trackbar_x, self.trackbar_y + tick_h) # 100 (Kiri)
        gc.StrokeLine(self.trackbar_x + self.trackbar_length, self.trackbar_y - tick_h, 
                      self.trackbar_x + self.trackbar_length, self.trackbar_y + tick_h) # 0 (Kanan)

        # 3. Tombol Geser (Thumb Handle)
        # Ratio: 0 = Kanan, 100 = Kiri
        ratio = self.trackbar_value / 100.0
        thumb_x = self.trackbar_x + int(round(ratio * self.trackbar_length))
        radius = 10

        # Warna Tombol (Orange saat di-drag)
        fill_color = wx.Colour(255, 128, 0) if self.is_dragging_trackbar else wx.Colour(0, 120, 215)
        gc.SetBrush(wx.Brush(fill_color))
        gc.SetPen(wx.Pen(wx.Colour(255, 255, 255), 2))
        gc.DrawEllipse(thumb_x - radius, self.trackbar_y - radius, radius * 2, radius * 2)

        # 4. Teks Nilai Trackbar (Indikator 0..100)
        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, wx.Colour(50, 50, 50))
        gc.DrawText("0 m", self.trackbar_x - 30, self.trackbar_y - 8)
        gc.DrawText("4.5 m", self.trackbar_x + self.trackbar_length + 10, self.trackbar_y - 8)

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if not gc or not self.bg_buffer or not self.bg_buffer.IsOk():
            return

        # draw blit background cache
        gc.DrawBitmap(self.bg_buffer, 0, 0, self.bg_buffer.GetWidth(), self.bg_buffer.GetHeight())

        # draw helicopter image
        gc.DrawBitmap(
            self.heli_bitmap,
            self.heli_x, self.heli_y,
            self.heli_bitmap.GetWidth(), self.heli_bitmap.GetHeight()
        )

        # draw trolley
        gc.DrawBitmap(
            self.trolley_bitmap,
            self.trolley_x, self.trolley_y,
            self.trolley_bitmap.GetWidth(), self.trolley_bitmap.GetHeight()
        )

        self.draw_trackbar(gc)

    # event subscribe plc 1 data
    def on_plc1_data(self, data):
        travel_val = data.get("V1004", 0)
        self.trackbar_value = travel_val

    def on_destroy(self, event):
        # Unsubscribe agar tidak memicu memory leak
        pub.unsubscribe(self.on_plc1_data, "modbus.data.plc1")
        event.Skip()