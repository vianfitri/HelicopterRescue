import wx
from PIL import Image, ImageDraw, ImageFilter


def prepare_splash_image(image_path, target_width=720, corner_radius=20):
    """Mempersiapkan gambar splash screen dengan skala proporsional

    dan sudut membulat (rounded corners) dengan pengaburan tepi yang halus.
    """
    # 1. Buka gambar
    img = Image.open(image_path).convert("RGBA")
    orig_w, orig_h = img.size

    # 2. Hitung tinggi proporsional berdasarkan target_width
    scale = target_width / orig_w
    target_height = int(orig_h * scale)
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # 3. Buat mask untuk sudut membulat (rounded corners)
    mask = Image.new("L", (target_width, target_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (target_width - 1, target_height - 1)],
        radius=corner_radius,
        fill=255,
    )

    # 4. Terapkan mask ke gambar
    output = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    output.paste(img_resized, (0, 0), mask)

    return output, target_width, target_height


class AppSplashScreen(wx.Frame):
    """Splash Screen dengan ukuran ringkas, sudut membulat, dan tanpa border."""

    def __init__(self, image_path, display_width=720, duration_ms=3000):
        super().__init__(
            None,
            style=wx.FRAME_NO_TASKBAR
            | wx.STAY_ON_TOP
            | wx.BORDER_NONE
            | wx.TRANSPARENT_WINDOW,
        )

        # Olah gambar & dapatkan dimensi proporsionalnya
        pil_img, w, h = prepare_splash_image(image_path, target_width=display_width)

        self.SetSize((w, h))
        self.Center()

        # Konversi PIL Image ke wx.Bitmap (mendukung transparansi/alpha channel)
        wx_img = wx.Image(w, h)
        wx_img.SetData(pil_img.convert("RGB").tobytes())
        wx_img.SetAlpha(pil_img.getchannel("A").tobytes())
        self.bitmap = wx_img.ConvertToBitmap()

        # Event binding
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_close)

        # Timer penutupan otomatis
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_close, self.timer)
        self.timer.Start(duration_ms, oneShot=True)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 0, 0, True)

    def on_close(self, event):
        if self.timer.IsRunning():
            self.timer.Stop()
        self.Destroy()


class MainApplicationFrame(wx.Frame):
    """Frame Utama Aplikasi dengan Resolusi 1720x1440."""

    def __init__(self):
        super().__init__(
            None,
            title="Sistem Monitoring Rescue Pelayaran - Politeknik Pelayaran Surabaya",
            size=(1720, 1440),
        )

        # Setel batas ukuran minimum & posisikan di tengah layar
        self.SetMinSize((1280, 720))
        self.Center()

        # Inisialisasi antarmuka utama
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 35, 45))  # Dark theme

        # Layout Sizer Utama
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header Title
        title = wx.StaticText(
            panel, label="SISTEM OPERASI RESCUE & PELAYARAN"
        )
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        title_font = wx.Font(
            20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        title.SetFont(title_font)

        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        # Area konten utama (1720x1440)
        content_box = wx.StaticBox(panel, label="Dashboard Utama")
        content_box.SetForegroundColour(wx.Colour(200, 200, 200))
        box_sizer = wx.StaticBoxSizer(content_box, wx.VERTICAL)

        status_lbl = wx.StaticText(
            panel,
            label="Aplikasi siap digunakan (Resolusi Layar Utama: 1720x1440)",
        )
        status_lbl.SetForegroundColour(wx.Colour(180, 220, 180))
        box_sizer.Add(status_lbl, 0, wx.ALL, 15)

        main_sizer.Add(box_sizer, 1, wx.EXPAND | wx.ALL, 20)
        panel.SetSizer(main_sizer)


class RescueApp(wx.App):

    def OnInit(self):
        IMAGE_FILE = "assets/images/poster.png"

        # 1. Tampilkan Splash Screen
        self.splash = AppSplashScreen(
            IMAGE_FILE, display_width=720, duration_ms=3500
        )
        self.splash.Show()

        # 2. Ketika splash ditutup, tampilkan Main Frame
        self.splash.Bind(wx.EVT_WINDOW_DESTROY, self.on_splash_closed)
        return True

    def on_splash_closed(self, event):
        self.main_frame = MainApplicationFrame()
        self.main_frame.Show()


if __name__ == "__main__":
    app = RescueApp()
    app.MainLoop()