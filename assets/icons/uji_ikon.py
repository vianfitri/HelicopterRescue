import wx
from icons import IconRenderer

class IconTestPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(wx.Colour(30, 30, 30))  # Latar gelap agar jelas
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if gc:
            # Uji menggambar dalam 3 ukuran berbeda
            #IconRenderer.draw_settings(gc, x=30, y=30, size=32, color=wx.Colour(255, 255, 255))
            #IconRenderer.draw_settings(gc, x=100, y=30, size=64, color=wx.Colour(0, 200, 255))
            #IconRenderer.draw_settings(gc, x=200, y=30, size=128, color=wx.Colour(255, 180, 0))
            IconRenderer.draw_plug(gc, x=300, y=30, size=100, color=wx.Colour(0, 255, 0))

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Uji Ikon Settings wxPython", size=(380, 220))
        IconTestPanel(self)
        self.Center()


if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()