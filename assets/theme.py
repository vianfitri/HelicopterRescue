import wx

class Theme:
    # =========================================================================
    # 60% DOMINANT (Structural Backgrounds)
    # =========================================================================
    BG_APP          = wx.Colour(5, 11, 20)      # #050B14 - Deep Void (Window Utama)
    BG_TITLEBAR     = wx.Colour(8, 16, 26)     # #08101A - Top Navigation Header
    BG_SIDEBAR      = wx.Colour(10, 20, 36)    # #0A1424 - Left Navigation Panel
    BG_CARD         = wx.Colour(15, 28, 46)     # #0F1C2E - Elevated Card Panel
    
    # =========================================================================
    # 30% SECONDARY (Typography & Structural Dividers)
    # =========================================================================
    TEXT_PRIMARY    = wx.Colour(226, 238, 249)  # #E2EEF9 - Ice White (Headings & Telemetry)
    TEXT_SECONDARY  = wx.Colour(140, 164, 192)  # #8CA4C0 - Muted Slate (Labels & Subtitles)
    
    BORDER_CARD     = wx.Colour(34, 53, 77)     # #22354D - Tactical Slate Border (1px)
    DIVIDER_LINE    = wx.Colour(45, 65, 90)     # Line Divider di bawah Title Card
    
    # =========================================================================
    # 10% ACCENTS & SAFETY ORANGE (Action Points & Statuses)
    # =========================================================================
    # --- Primary Accent: Safety Orange ---
    ORANGE_NORMAL   = wx.Colour(255, 85, 0)     # #FF5500 - Safety Orange Murni
    ORANGE_HOVER    = wx.Colour(255, 110, 35)   # #FF6E23 - Hover State
    ORANGE_PRESSED  = wx.Colour(215, 65, 0)     # #D74100 - Active / Click State
    ORANGE_BORDER   = wx.Colour(255, 160, 80)    # #FFA050 - High-Contrast Edge Highlight
    ORANGE_GLOW     = wx.Colour(255, 85, 0, 60) # Translucent Glow Effect
    
    # --- Secondary Avionics Accent ---
    ACCENT_CYAN     = wx.Colour(0, 210, 255)    # #00D2FF - Radar / GPS Highlight
    
    # --- Status Indicators ---
    STATUS_OK       = wx.Colour(0, 230, 161)    # #00E6A1 - Active / Normal / Stable
    STATUS_WARN     = wx.Colour(255, 184, 0)    # #FFB800 - Caution / Amber
    STATUS_ALERT    = wx.Colour(255, 42, 0)     # #FF2A00 - Emergency / Cut Cable / Alert

    # =========================================================================
    # HELPER FONTS
    # =========================================================================
    @staticmethod
    def FontTitle():
        return wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

    @staticmethod
    def FontBody():
        return wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

    @staticmethod
    def FontTelemetry():
        """Font Monospace untuk angka/koordinat agar tidak bergeser saat update real-time"""
        return wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    
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
