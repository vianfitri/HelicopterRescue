import wx
import math

class SidebarTabControl(wx.Control):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.NO_BORDER    
    ):
        super(SidebarTabControl, self).__init__(parent, id, pos, size, style)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Data Tab
        self.tabs = []
        self.selected_index = 1 # default selected tab
        self.hover_index = -1

        self.item_height = 54
        self.padding_left = 16

        # Color Scheme
        #self.color_bg = wx.Colour(22, 27, 34)              # Sidebar Background
        self.color_bg = wx.Colour(8, 15, 25)              # Sidebar Background
        self.color_hover_bg = wx.Colour(35,42, 52)         # Highlight Background on hover
        self.color_text_normal = wx.Colour(191, 193, 193)  # Text & Icon normal
        self.color_text_active = wx.Colour(255, 255, 255)  # Active text
        self.color_text_hover = wx.Colour(210, 215, 226)   # Hover Text
        self.color_orange = wx.Colour(235, 130, 20)        # Line color & orange accent

        # Gradient colour active Tab
        #self.grad_start = wx.Colour(120, 55, 10, 180)      #
        self.grad_start = wx.Colour(112, 56, 11, 100)      # 
        #self.grad_end = wx.Colour(70, 30, 5, 60)
        self.grad_end = wx.Colour(22, 30, 41, 100)

        # Binding Event
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

    def AddTab(self, label, bitmap_normal=None, bitmap_hover=None, bitmap_active=None):
        """ Add Tab to sidenar """
        self.tabs.append({
            'label': label,
            'bmp_normal': bitmap_normal,
            'bmp_hover': bitmap_hover or bitmap_normal,
            'bmp_active': bitmap_active or bitmap_normal
        })
        self.Refresh()

    def SetSelection(self, index):
        """Mengubah tab terpilih berdasarkan indeks."""
        if 0 <= index < len(self.tabs) and index != self.selected_index:
            self.selected_index = index
            self.Refresh()
            
            # Post event perubah tab
            evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
            evt.SetInt(index)
            evt.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(evt)

    def GetSelection(self):
        return self.selected_index

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.color_bg))
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        width, height = self.GetClientSize()
        
        # Font setup
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, self.color_text_normal)

        for i, tab in enumerate(self.tabs):
            y = i * self.item_height
            rect = wx.Rect(0, y, width, self.item_height)
            is_selected = (i == self.selected_index)
            is_hover = (i == self.hover_index and not is_selected)

            # Draw Selected Tab Background & Accent
            if is_selected:
                # 1. Background Gradient Tab Aktif
                brush = gc.CreateLinearGradientBrush(
                    0, y, width - 8, y, 
                    self.grad_start, self.grad_end
                )
                gc.SetBrush(brush)
                gc.SetPen(wx.NullPen)
                gc.DrawRoundedRectangle(4, y + 2, width - 8, self.item_height - 4, 4)

                # 2. Garis Vertikal Orange di Kiri
                #gc.SetBrush(gc.CreateBrush(wx.Brush(self.color_orange)))
                #gc.DrawRoundedRectangle(4, y + 2, 4, self.item_height - 4, 4)

                # create path
                path = gc.CreatePath()
                path.MoveToPoint(4 + 4, y + 2)
                path.AddArc(4 + 4, y + 2 + 4, 4, 1.5 * math.pi, math.pi, False)
                path.AddLineToPoint(4, y + 2 + self.item_height - 8)
                path.AddArc(4 + 4, y + 2 + self.item_height - 8, 4, math.pi, .5 * math.pi, False)
                path.CloseSubpath()

                gc.SetBrush(gc.CreateBrush(wx.Brush(self.color_orange)))
                gc.FillPath(path)

            elif is_hover:
                # thin background highlight on hover
                gc.SetBrush(gc.CreateBrush(wx.Brush(self.color_hover_bg)))
                gc.SetPen(wx.NullPen)
                gc.DrawRoundedRectangle(4, y + 2, width - 8, self.item_height -4, 4)

            # Draw Bitmap / Icon (jika ada)
            if is_selected:
                bmp = tab['bmp_active']
            elif is_hover:
                bmp = tab['bmp_hover']
            else:
                bmp = tab['bmp_normal']

            x_offset = self.padding_left + 8
            
            if bmp and bmp.IsOk():
                gc.DrawBitmap(bmp, x_offset, y + (self.item_height - bmp.GetHeight()) // 2, bmp.GetWidth(), bmp.GetHeight())
                x_offset += bmp.GetWidth() + 12
            else:
                x_offset += 24  # Placeholder spasi jika tidak ada gambar

            # Draw Label Text
            if is_selected:
                text_color = self.color_text_active
            elif is_hover:
                text_color = self.color_text_hover
            else:
                text_color = self.color_text_normal

            gc.SetFont(font, text_color)
            
            # Vertically center text
            _, txt_h = dc.GetTextExtent(tab['label'])
            gc.DrawText(tab['label'], x_offset, y + (self.item_height - txt_h) / 2)

    def OnLeftDown(self, event):
        y = event.GetY()
        clicked_index = y // self.item_height
        if 0 <= clicked_index < len(self.tabs):
            self.SetSelection(clicked_index)

    def OnMouseMotion(self, event):
        y = event.GetY()
        new_hover_index = y // self.item_height

        if 0 <= new_hover_index < len(self.tabs):
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        else:
            new_hover_index = -1
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

        # Redraw if hover status changed
        if new_hover_index != self.hover_index:
            self.hover_index = new_hover_index
            self.Refresh()

    def OnMouseLeave(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        if self.hover_index != -1:
            self.hover_index = -1
            self.Refresh()

    def OnSize(self, event):
        self.Refresh()
        event.Skip()    