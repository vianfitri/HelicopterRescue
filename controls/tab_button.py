import math
import wx
import wx.lib.newevent
from utils.svg_utils import load_svg_as_bitmap
from pathlib import Path

#from Assets.theme import Theme
#from Assets.icons import IconRenderer

# Define custom tab event
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
        
        # Konfigurasi rendering untuk custom control
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetMinSize((200, 60))
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        # Color State Text and Icon
        HEX_NORMAL = "#BFC1C1"
        HEX_HOVER = "#D2D7E1"
        HEX_ACTIVE = "#FFFFFF"

        # load icon bitmap
        icon_base_dir = Path("assets/icons")
        icon_path = icon_base_dir / self.icon_type

        #print(icon_path)
        self.icon_size = (20,20)
        self.bitmap_norm = load_svg_as_bitmap(icon_path, HEX_NORMAL, size=self.icon_size, is_file=True)
        self.bitmap_hover = load_svg_as_bitmap(icon_path, HEX_HOVER, size=self.icon_size, is_file=True)
        self.bitmap_active = load_svg_as_bitmap(icon_path, HEX_ACTIVE, size=self.icon_size, is_file=True)

        # Event bindings
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_click)

    def DoGetBestSize(self):
        """Menentukan ukuran default kontrol jika tidak di-set oleh Sizer."""
        return wx.Size(200, 60)

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.Refresh()

    def _on_enter(self, event):
        self.is_hovered = True
        self.Refresh()
        event.Skip()

    def _on_leave(self, event):
        self.is_hovered = False
        self.Refresh()
        event.Skip()

    def _on_click(self, event):
        # Fire custom event to parent
        evt = TabSelectEvent(self.GetId(), tab_id=self.tab_id)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)
        event.Skip()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()

        # 1. Background color determination
        if self.is_selected:
            # Gradient Background Active Tab
            grad_start = wx.Colour(112, 56, 11, 170)
            grad_end = wx.Colour(22, 30, 41, 170)
            brush = gc.CreateLinearGradientBrush(
                4, 2, w - 8, 2,
                grad_start, grad_end
            )

        elif self.is_hovered:
            # Background brush hover tab
            bg_color = wx.Colour(35, 42, 52)
            brush = wx.Brush(bg_color)
        else:
            # Background brush normal tab
            bg_color = wx.Colour(21, 24, 30)
            brush = wx.Brush(bg_color)

        # Fill background with slightly rounded rect if hovered/selected
        gc.SetBrush(brush)
        gc.SetPen(wx.NullPen)
        gc.DrawRoundedRectangle(4, 2, w - 8, h - 4, 6)

        # 2. Left Active Indicator (Safety Orange Bar) and Right Arrow Active Indicator
        if self.is_selected:
            # create path left bar active indicator
            path = gc.CreatePath()
            path.MoveToPoint(10, 2)
            path.AddArc(10, 8, 6, 1.5 * math.pi, math.pi, False)
            path.AddLineToPoint(4, h - 16)
            path.AddArc(10, h - 8, 6, math.pi, .5 * math.pi, False)
            path.CloseSubpath()

            # draw fill path
            gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(255, 94, 19))))
            gc.FillPath(path)

            # active right arrow indicator
            gc.SetPen(wx.Pen(wx.Colour(255, 94, 19), 2))
            arrow_x = w - 18
            arrow_y = h / 2.0
            arrow_path = gc.CreatePath()
            arrow_path.MoveToPoint(arrow_x - 3, arrow_y - 4)
            arrow_path.AddLineToPoint(arrow_x + 1, arrow_y)
            arrow_path.AddLineToPoint(arrow_x - 3, arrow_y + 4)
            gc.StrokePath(arrow_path)

        # 3. Button Icon
        if self.is_selected:
            bmp = self.bitmap_active
        elif self.is_hovered:
            bmp = self.bitmap_hover
        else:
            bmp = self.bitmap_norm

        icon_w, icon_h = self.icon_size    
        icon_x = 22.0
        icon_y = (h - icon_h) / 2.0

        gc.DrawBitmap(bmp, icon_x, icon_y, icon_w, icon_h)


        #if self.is_selected:
        #    gc.SetPen(wx.NullPen)
        #    #gc.SetBrush(wx.Brush(Theme.ACCENT_ORANGE))
        #    gc.SetBrush(wx.Brush(wx.Colour(255, 94, 19)))
        #    gc.DrawRoundedRectangle(6, 8, 4, h - 16, 2)
        #elif self.is_hovered:
        #    # Subtle accent indicator on hover
        #    gc.SetPen(wx.NullPen)
        #    gc.SetBrush(wx.Brush(wx.Colour(
        #        #Theme.ACCENT_ORANGE.Red(),
        #        #Theme.ACCENT_ORANGE.Green(),
        #        #Theme.ACCENT_ORANGE.Blue(), 120
        #        255,
        #        94,
        #        19,
        #        120
        #    )))
        #    gc.DrawRoundedRectangle(6, 12, 3, h - 24, 1.5)

        # 3. Draw Vector Icon
        #icon_size = 24.0
        #icon_x = 22.0
        #icon_y = (h - icon_size) / 2.0

        #if self.is_selected:
        #    #icon_color = Theme.ACCENT_ORANGE
        #    icon_color = wx.Colour(255, 94, 19)
        #elif self.is_hovered:
        #    #icon_color = Theme.TEXT_PRIMARY
        #    icon_color = wx.Colour(255, 255, 255)
        #else:
        #    #icon_color = Theme.TEXT_MUTED
        #    icon_color = wx.Colour(129, 142, 155)

        #if self.icon_type == 'flight':
        #    IconRenderer.draw_flight_ops(gc, icon_x, icon_y, icon_size, icon_color)
        #elif self.icon_type == 'missions':
        #    IconRenderer.draw_missions(gc, icon_x, icon_y, icon_size, icon_color)
        #elif self.icon_type == 'fleet':
        #    IconRenderer.draw_fleet(gc, icon_x, icon_y, icon_size, icon_color)
        #elif self.icon_type == 'weather':
        #    IconRenderer.draw_weather(gc, icon_x, icon_y, icon_size, icon_color)

        # 4. Text Labels (Title & Subtitle)
        #text_x = 58.0
        
        # Primary Title
        #if self.is_selected or self.is_hovered:
        #    #title_font = Theme.get_font(size=10, bold=True)
        #    #title_color = Theme.TEXT_PRIMARY
        #    title_font = wx.Font(
        #        10,
        #        wx.FONTFAMILY_SWISS,
        #        wx.FONTSTYLE_NORMAL,
        #        wx.FONTWEIGHT_BOLD,
        #        False,
        #        "Segoe UI"
        #    )
        #    title_color = wx.Colour(255, 255, 255)
        #else:
        #    #title_font = Theme.get_font(size=10, bold=False)
        #    #title_color = Theme.TEXT_SECONDARY
        #    title_font = wx.Font(
        #        10,
        #        wx.FONTFAMILY_SWISS,
        #        wx.FONTSTYLE_NORMAL,
        #        wx.FONTWEIGHT_NORMAL,
        #        False,
        #        "Segoe UI"
        #    )
        #    title_color = wx.Colour(203, 213, 255)

        #gc.SetFont(title_font, title_color)
        #gc.DrawText(self.label, text_x, h / 2.0 - 16)

        # Subtitle
        #sub_font = Theme.get_font(size=8, bold=False)
        #sub_color = Theme.TEXT_MUTED if not self.is_selected else Theme.TEXT_SECONDARY
        #sub_font = wx.Font(
        #    8,
        #    wx.FONTFAMILY_SWISS,
        #    wx.FONTSTYLE_NORMAL,
        #    wx.FONTWEIGHT_NORMAL,
        #    False,
        #    "Segoe UI"
        #)
        
        #sub_color = wx.Colour(129, 142, 155) if not self.is_selected else wx.Colour(203, 213, 255)
        #gc.SetFont(sub_font, sub_color)
        #gc.DrawText(self.subtitle, text_x, h / 2.0 + 3)


