import os
import wx
from PIL import Image, ImageFilter


def process_splash_image(image_path, target_height=768, fade_width=180):
    """Menskala gambar agar tingginya pas dengan panel splash (768px),

    lalu membuat efek fusi/gradasi transparan pada tepi sebelah kanan gambar.
    """
    # 1. Pastikan Path Gambar Valid
    if not os.path.exists(image_path):
        print(f"[WARNING] File gambar '{image_path}' tidak ditemukan!")
        # Buat dummy image jika file tidak ditemukan
        img = Image.new("RGBA", (848, 1264), (30, 50, 70, 255))
    else:
        img = Image.open(image_path).convert("RGBA")

    orig_w, orig_h = img.size

    # 2. Skalakan proporsional terhadap tinggi target (768px)
    scale = target_height / orig_h
    new_w = int(orig_w * scale)
    new_h = target_height

    img_scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 3. Buat Alpha Mask untuk pengaburan tepi kanan gambar
    mask = Image.new("L", (new_w, new_h), 255)

    for x in range(new_w):
        dist_from_right = new_w - 1 - x
        if dist_from_right < fade_width:
            alpha = int(255 * (dist_from_right / fade_width))
            for y in range(new_h):
                mask.putpixel((x, y), alpha)

    mask = mask.filter(ImageFilter.GaussianBlur(8))
    img_scaled.putalpha(mask)

    return img_scaled, new_w, new_h


class ReliableSplashPanel(wx.Panel):

    def __init__(self, parent, image_path):
        super().__init__(parent)

        self.SetDoubleBuffered(True)

        # Warna Tema
        self.bg_color = wx.Colour(20, 26, 35)
        self.text_main_color = wx.Colour(255, 255, 255)
        self.text_sub_color = wx.Colour(0, 168, 204)
        self.gauge_bg_color = wx.Colour(50, 60, 75)
        self.gauge_fill_color = wx.Colour(255, 100, 30)

        self.SetBackgroundColour(self.bg_color)

        # Olah Gambar PIL
        pil_img, self.img_w, self.img_h = process_splash_image(
            image_path, target_height=768, fade_width=180
        )

        # Konversi ke wx.Bitmap
        wx_img = wx.Image(self.img_w, self.img_h)
        wx_img.SetData(pil_img.convert("RGB").tobytes())
        wx_img.SetAlpha(pil_img.getchannel("A").tobytes())
        self.bitmap = wx_img.ConvertToBitmap()

        # Data Status
        self.progress_val = 20
        self.status_text = "Memuat komponen sistem..."

        # Bind Paint
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def update_status(self, progress, status):
        self.progress_val = progress
        self.status_text = status
        self.Refresh()

    def on_paint(self, event):
        pdc = wx.BufferedPaintDC(self)

        # 1. Bersihkan Canvas & Cat Latar Belakang Gelap
        pdc.SetBackground(wx.Brush(self.bg_color))
        pdc.Clear()

        # 2. Gambar Bitmap Langsung Menggunakan DC Standard (Aman dari Bug DPI Scaling)
        if self.bitmap.IsOk():
            pdc.DrawBitmap(self.bitmap, 0, 0, True)

        # 3. Gunakan GraphicsContext Hanya Untuk Teks & Gauge Grafis
        gc = wx.GraphicsContext.Create(pdc)
        if not gc:
            return

        # Ambil faktor skala DPI layar agar ukuran teks/gauge presisi
        dpi_scale = self.GetDPIScaleFactor()

        # Posisi Awal Sisi Kanan (Disesuaikan dengan Lebar Gambar)
        text_x_base = (self.img_w + 40) / dpi_scale
        text_y_base = 250 / dpi_scale

        # --- TERUJI: GAMBAR TEKS ---
        # Subtitle
        sub_font = wx.Font(
            12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        gc.SetFont(sub_font, self.text_sub_color)
        gc.DrawText("POLITEKNIK PELAYARAN SURABAYA", text_x_base, text_y_base)

        # Judul Utama
        main_font = wx.Font(
            28, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        gc.SetFont(main_font, self.text_main_color)
        gc.DrawText(
            "SEARCH & RESCUE", text_x_base, text_y_base + (35 / dpi_scale)
        )
        gc.DrawText(
            "OPERATIONAL SYSTEM", text_x_base, text_y_base + (80 / dpi_scale)
        )

        # Teks Status Loading
        status_font = wx.Font(
            10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL
        )
        gc.SetFont(status_font, wx.Colour(160, 175, 190))
        gc.DrawText(
            self.status_text, text_x_base, text_y_base + (170 / dpi_scale)
        )

        # --- TERUJI: GAMBAR PROGRESS GAUGE ---
        gauge_width = 420 / dpi_scale
        gauge_height = 8 / dpi_scale
        gauge_x = text_x_base
        gauge_y = text_y_base + (200 / dpi_scale)

        # Base Gauge
        gc.SetBrush(wx.Brush(self.gauge_bg_color))
        gc.SetPen(wx.NullPen)
        gc.DrawRoundedRectangle(gauge_x, gauge_y, gauge_width, gauge_height, 4)

        # Fill Gauge
        if self.progress_val > 0:
            fill_w = int(gauge_width * (self.progress_val / 100))
            if fill_w > gauge_width:
                fill_w = gauge_width
            gc.SetBrush(wx.Brush(self.gauge_fill_color))
            gc.DrawRoundedRectangle(gauge_x, gauge_y, fill_w, gauge_height, 4)


class SplashScreenFrame(wx.Frame):

    def __init__(self, image_path, size=(1360, 768), duration_ms=4500):
        super().__init__(
            None,
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE,
            size=size,
        )

        self.SetSize(size)
        self.Center()

        # Panel utama
        self.splash_panel = ReliableSplashPanel(self, image_path)

        # Timer Simulasi Loading
        self.progress_val = 20
        self.status_text = "Memuat komponen sistem..."

        self.progress_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_update, self.progress_timer)
        self.progress_timer.Start(40)

        self.close_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_close, self.close_timer)
        self.close_timer.Start(duration_ms, oneShot=True)

    def on_timer_update(self, event):
        if self.progress_val < 100:
            self.progress_val += 1

            if self.progress_val == 50:
                self.status_text = "Menghubungkan ke basis data..."
            elif self.progress_val == 85:
                self.status_text = "Menyiapkan antarmuka utama..."

            self.splash_panel.update_status(
                self.progress_val, self.status_text
            )

    def on_close(self, event):
        self.progress_timer.Stop()
        self.close_timer.Stop()
        self.Destroy()


class MainApplicationFrame(wx.Frame):

    def __init__(self):
        super().__init__(
            None,
            title="Aplikasi Rescue - Politeknik Pelayaran Surabaya",
            size=(1720, 1440),
        )
        self.SetMinSize((1280, 720))
        self.Center()

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 35, 45))

        lbl = wx.StaticText(
            panel,
            label="Aplikasi Utama Berhasil Dijalankan (1720x1440)",
            pos=(50, 50),
        )
        lbl.SetForegroundColour(wx.Colour(255, 255, 255))
        lbl.SetFont(
            wx.Font(
                18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
            )
        )


class RescueApp(wx.App):

    def OnInit(self):
        # Masukkan nama file gambar Anda di sini
        IMAGE_FILE = "assets/images/poster.png"

        self.splash = SplashScreenFrame(
            IMAGE_FILE, size=(1360, 768), duration_ms=4500
        )
        self.splash.Show()

        self.splash.Bind(wx.EVT_WINDOW_DESTROY, self.on_splash_closed)
        return True

    def on_splash_closed(self, event):
        self.main_frame = MainApplicationFrame()
        self.main_frame.Show()


if __name__ == "__main__":
    app = RescueApp()
    app.MainLoop()