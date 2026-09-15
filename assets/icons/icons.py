import math
import wx
#from .theme import Theme

class IconRenderer:
    @staticmethod
    def draw_data_connect(gc: wx.GraphicsContext, x: float, y: float, size: float, color: wx.Colour):
        pass

    @staticmethod
    def draw_settings(gc: wx.GraphicsContext, x: float, y: float, size: float, color: wx.Colour):
        """Draws a 8-tooth Settings / Gear icon."""
        gc.SetPen(wx.Pen(color, 2))
        gc.SetBrush(wx.NullBrush)
        
        cx, cy = x + size / 2.0, y + size / 2.0
        
        # Proporsi ukuran gear
        r_inner_hole = size * 0.15  # Jari-jari lubang tengah
        r_base = size * 0.28        # Jari-jari lingkaran dalam gigi
        r_outer = size * 0.42       # Jari-jari puncak gigi
        
        # 1. Gambar lubang di tengah gear
        gc.DrawEllipse(cx - r_inner_hole, cy - r_inner_hole, r_inner_hole * 2, r_inner_hole * 2)
        
        # 2. Buat path untuk bentuk gigi (8 gigi)
        num_teeth = 8
        path = gc.CreatePath()
        
        angle_per_step = (2 * math.pi) / num_teeth
        tooth_width_angle = angle_per_step * 0.35  # Lebar puncak gigi
        
        for i in range(num_teeth):
            start_angle = i * angle_per_step
            
            # Sudut untuk 4 titik pada setiap gigi
            a1 = start_angle - tooth_width_angle / 2
            a2 = start_angle + tooth_width_angle / 2
            a3 = start_angle + angle_per_step / 2 - tooth_width_angle / 2
            a4 = start_angle + angle_per_step / 2 + tooth_width_angle / 2
            
            # Konversi sudut ke koordinat X, Y
            x1, y1 = cx + r_base * math.cos(a1), cy + r_base * math.sin(a1)
            x2, y2 = cx + r_outer * math.cos(a2), cy + r_outer * math.sin(a2)
            x3, y3 = cx + r_outer * math.cos(a3), cy + r_outer * math.sin(a3)
            x4, y4 = cx + r_base * math.cos(a4), cy + r_base * math.sin(a4)
            
            if i == 0:
                path.MoveToPoint(x1, y1)
            else:
                path.AddLineToPoint(x1, y1)
                
            path.AddLineToPoint(x2, y2)
            path.AddLineToPoint(x3, y3)
            path.AddLineToPoint(x4, y4)
            
        path.CloseSubpath()
        gc.StrokePath(path)

    @staticmethod
    def draw_plug(gc: wx.GraphicsContext, x: float, y: float, size: float, color: wx.Colour, connected: bool = True):
        """
        Draws a power plug icon diagonally at a 45-degree angle.
        """
        gc.PushState()  # Simpan state kanvas sebelum melakukan transformasi (translasi & rotasi)
        
        cx, cy = x + size / 2.0, y + size / 2.0
        
        # Pindahkan koordinat lokal (0,0) ke titik tengah ikon, lalu rotasi -45 derajat (-pi/4)
        gc.Translate(cx, cy)
        gc.Rotate(-math.pi / 4)  # Rotasi miring ke atas (45 derajat)
        
        gc.SetPen(wx.Pen(color, 2))
        gc.SetBrush(wx.NullBrush)

        plug_w = size * 0.26
        plug_h = size * 0.22
        r = plug_h / 2.0
        pin_len = size * 0.14
        wire_len = size * 0.18
        
        gap = 0.0 if connected else size * 0.16
        
        # ------------------------------------------------------------------
        # 1. Colokan Kiri (Diukur dari pusat lokal 0,0)
        # ------------------------------------------------------------------
        left_front_x = -gap / 2.0
        left_back_x = left_front_x - plug_w
        
        path_l = gc.CreatePath()
        path_l.MoveToPoint(left_front_x, -r)
        path_l.AddLineToPoint(left_back_x, -r)
        path_l.AddArc(left_back_x, 0, r, -math.pi / 2, math.pi / 2, True)
        path_l.AddLineToPoint(left_front_x, r)
        path_l.CloseSubpath()
        
        # Pin colokan
        path_l.MoveToPoint(left_front_x, -r * 0.45)
        path_l.AddLineToPoint(left_front_x + pin_len, -r * 0.45)
        path_l.MoveToPoint(left_front_x, r * 0.45)
        path_l.AddLineToPoint(left_front_x + pin_len, r * 0.45)
        
        # Kabel belakang kiri
        path_l.MoveToPoint(left_back_x - r, 0)
        path_l.AddLineToPoint(left_back_x - r - wire_len, 0)
        gc.StrokePath(path_l)

        # ------------------------------------------------------------------
        # 2. Colokan Kanan (Diukur dari pusat lokal 0,0)
        # ------------------------------------------------------------------
        right_front_x = gap / 2.0
        right_back_x = right_front_x + plug_w
        
        path_r = gc.CreatePath()
        path_r.MoveToPoint(right_front_x, -r)
        path_r.AddLineToPoint(right_back_x, -r)
        path_r.AddArc(right_back_x, 0, r, -math.pi / 2, math.pi / 2, False)
        path_r.AddLineToPoint(right_front_x, r)
        path_r.CloseSubpath()
        
        # Kabel belakang kanan
        path_r.MoveToPoint(right_back_x + r, 0)
        path_r.AddLineToPoint(right_back_x + r + wire_len, 0)
        gc.StrokePath(path_r)

        gc.PopState()  # Kembalikan state kanvas ke semula