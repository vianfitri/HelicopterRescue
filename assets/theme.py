import wx

class Theme:
    @staticmethod
    def get_font(size=10, weight=wx.FONTWEIGHT_NORMAL, family=wx.FONTFAMILY_SWISS, bold=False):
        """Creates a modern Segoe UI font or system fallback."""
        w = wx.FONTWEIGHT_BOLD if bold else weight
        font = wx.Font(
            size,
            family,
            wx.FONTSTYLE_NORMAL,
            w,
            False,
            "Segoe UI"
        )
        return font

    @staticmethod
    def get_mono_font(size=10, bold=False):
        """Monospaced font for telemetry, coordinates, and timestamps."""
        w = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
        font = wx.Font(
            size,
            wx.FONTFAMILY_TELETYPE,
            wx.FONTSTYLE_NORMAL,
            w,
            False,
            "Consolas"
        )
        return font
