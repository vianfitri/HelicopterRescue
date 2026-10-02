import math
import wx
import wx.lib.newevent
from utils.svg_utils import load_svg_as_bitmap
from pathlib import Path

TabSelectEvent, EVT_TAB_SELECTED = wx.lib.newevent.NewCommandEvent()


class TabButton(wx.Control):

    def __init__(self, parent, tab_id: int, label: str, icon_type: str):
        super().__init__(
            parent, 
            id=wx.ID_ANY, 
            style=wx.BORDER_NONE | wx.WANTS_CHARS
        )
        self.tab_id = tab_id
        self.label = label
        self.icon_type = icon_type
        
        self.is_selected = False
        self.is_hovered = False
        
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetMinSize((200, 60))
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        # Color Hex Constants
        self.HEX_NORMAL = "#BFC1C1"
        self.HEX_HOVER = "#D2D7E1"
        self.HEX_ACTIVE = "#FFFFFF"

        # Cache Font & Color Objects
        self.title_font = wx.Font(
            10,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            False,
            "Segoe UI"
        )
        self.color_normal = wx.Colour(self.HEX_NORMAL)
        self.color_hover = wx.Colour(self.HEX_HOVER)
        self.color_active = wx.Colour(self.HEX_ACTIVE)
        
        self.color_bg_hover = wx.Colour(35, 42, 52)
        self.color_bg_normal = wx.Colour(21, 24, 30)
        self.color_orange = wx.Colour(255, 94, 19)

        # Load Icon Bitmaps
        icon_base_dir = Path("assets/icons")
        icon_path = icon_base_dir / self.icon_type
        self.icon_size = (20, 20)

        self.bitmap_norm = load_svg_as_bitmap(icon_path, self.HEX_NORMAL, size=self.icon_size, is_file=True)
        self.bitmap_hover = load_svg_as_bitmap(icon_path, self.HEX_HOVER, size=self.icon_size, is_file=True)
        self.bitmap_active = load_svg_as_bitmap(icon_path, self.HEX_ACTIVE, size=self.icon_size, is_file=True)

        # Event Bindings
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_click)

    def DoGetBestSize(self):
        return wx.Size(200, 60)

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.Refresh(False)

    def _on_enter(self, event):
        if not self.is_hovered:
            self.is_hovered = True
            self.Refresh(False)
        event.Skip()

    def _on_leave(self, event):
        if self.is_hovered:
            self.is_hovered = False
            self.Refresh(False)
        event.Skip()

    def _on_click(self, event):
        evt = TabSelectEvent(self.GetId(), tab_id=self.tab_id)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)
        event.Skip()

    def _on_paint(self, event):
        # Menggunakan wx.PaintDC standar karena SetDoubleBuffered(True) & SetBackgroundStyle(wx.BG_STYLE_PAINT) aktif
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()
        if w <= 0 or h <= 0:
            return

        # Clear background dengan warna induk (sidebar)
        parent_bg = self.GetParent().GetBackgroundColour()
        gc.SetBrush(gc.CreateBrush(wx.Brush(parent_bg)))
        gc.SetPen(wx.NullPen)
        gc.DrawRectangle(0, 0, w, h)

        # 1. Background Tab Button
        if self.is_selected:
            grad_start = wx.Colour(112, 56, 11, 170)
            grad_end = wx.Colour(22, 30, 41, 170)
            brush = gc.CreateLinearGradientBrush(4, 2, w - 8, 2, grad_start, grad_end)
        elif self.is_hovered:
            brush = gc.CreateBrush(wx.Brush(self.color_bg_hover))
        else:
            brush = gc.CreateBrush(wx.Brush(self.color_bg_normal))

        gc.SetBrush(brush)
        gc.DrawRoundedRectangle(4, 2, w - 8, h - 4, 6)

        # 2. Indicator Aktif (Orange Bar + Right Arrow)
        if self.is_selected:
            # Bar Kiri
            path = gc.CreatePath()
            path.MoveToPoint(10, 2)
            path.AddArc(10, 8, 6, 1.5 * math.pi, math.pi, False)
            path.AddLineToPoint(4, h - 16)
            path.AddArc(10, h - 8, 6, math.pi, 0.5 * math.pi, False)
            path.CloseSubpath()

            gc.SetBrush(gc.CreateBrush(wx.Brush(self.color_orange)))
            gc.FillPath(path)

            # Arrow Kanan
            gc.SetPen(wx.Pen(self.color_orange, 2))
            arrow_x = w - 18
            arrow_y = h / 2.0
            arrow_path = gc.CreatePath()
            arrow_path.MoveToPoint(arrow_x - 3, arrow_y - 4)
            arrow_path.AddLineToPoint(arrow_x + 1, arrow_y)
            arrow_path.AddLineToPoint(arrow_x - 3, arrow_y + 4)
            gc.StrokePath(arrow_path)

        # 3. Icon
        if self.is_selected:
            bmp = self.bitmap_active
        elif self.is_hovered:
            bmp = self.bitmap_hover
        else:
            bmp = self.bitmap_norm

        if bmp and bmp.IsOk():
            icon_w, icon_h = self.icon_size    
            icon_x = 22.0
            icon_y = (h - icon_h) / 2.0
            gc.DrawBitmap(bmp, icon_x, icon_y, icon_w, icon_h)

        # 4. Text Label
        if self.is_selected:
            title_color = self.color_active
        elif self.is_hovered:
            title_color = self.color_hover
        else:
            title_color = self.color_normal

        gc.SetFont(self.title_font, title_color)
        _, txt_h = gc.GetTextExtent(self.label)
        title_x = 22.0 + self.icon_size[0] + 12
        title_y = (h - txt_h) / 2.0
        gc.DrawText(self.label, title_x, title_y)