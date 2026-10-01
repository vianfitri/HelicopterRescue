import sys
import threading
import time
import pygame

# Import pymodbus
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import asyncio

# ---------------------------------------------------------
# 1. KONFIGURASI MODBUS DATASTORE
# ---------------------------------------------------------
# Kita mendefinisikan datastore coil dari alamat 6080 hingga 6088 (9 item)
START_ADDRESS = 6080
COIL_COUNT = 9

# Inisialisasi blok data coil (Default: False/0)
store = ModbusSlaveContext(
    coils=ModbusSequentialDataBlock(START_ADDRESS, [False] * COIL_COUNT)
)
context = ModbusServerContext(slaves=store, single=True)

# Function untuk menjalankan Async Modbus Server
def run_modbus_server(host="0.0.0.0", port=502):
    async def main():
        print(f"[Modbus Server] Berjalan pada {host}:{port}")
        await StartAsyncTcpServer(context, address=(host, port))
    
    # Menjalankan loop asyncio tersendiri dalam thread terpisah
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

# ---------------------------------------------------------
# 2. DEFINISI ALAMAT KOIL & ITEM GUI
# ---------------------------------------------------------
COIL_ITEMS = [
    {"name": "M3008: IND DOWNWASH LOW",    "addr": 6080},
    {"name": "M3009: IND DOWNWASH HIGH",   "addr": 6081},
    {"name": "M3010: IND WAVE 1",          "addr": 6082},
    {"name": "M3011: IND WAVE 2",          "addr": 6083},
    {"name": "M3012: IND RAIN SLIGHT",     "addr": 6084},
    {"name": "M3013: IND RAIN MODERATE",   "addr": 6085},
    {"name": "M3014: IND RAIN HEAVY",      "addr": 6086},
    {"name": "M3015: IND WIND LOW",        "addr": 6087},
    {"name": "M3016: IND WIND HIGH",       "addr": 6088},
]

# Helper function untuk membaca dan menulis nilai coil pada Modbus Context
def get_coil_value(addr):
    # fx=1 mewakili Read Coils
    values = context[0x00].getValues(1, addr, count=1)
    return values[0] if values else False

def set_coil_value(addr, value):
    # fx=1 mewakili Write Coils
    context[0x00].setValues(1, addr, [value])

def toggle_coil_value(addr):
    current = get_coil_value(addr)
    set_coil_value(addr, not current)

# ---------------------------------------------------------
# 3. INTERFACE PYGAME GUI
# ---------------------------------------------------------
def run_gui():
    pygame.init()
    
    WINDOW_WIDTH = 520
    WINDOW_HEIGHT = 580
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Modbus TCP Server Simulator")
    
    clock = pygame.time.Clock()
    
    # Warna
    COLOR_BG = (30, 30, 36)
    COLOR_PANEL = (45, 45, 55)
    COLOR_TEXT = (240, 240, 240)
    COLOR_BTN_ON = (46, 204, 113)    # Hijau saat AKTIF
    COLOR_BTN_OFF = (231, 76, 60)   # Merah saat NON-AKTIF
    COLOR_INDICATOR_ON = (0, 255, 128)
    COLOR_INDICATOR_OFF = (100, 100, 100)
    
    font_title = pygame.font.SysFont("Arial", 22, bold=True)
    font_btn = pygame.font.SysFont("Arial", 14, bold=True)
    font_status = pygame.font.SysFont("Arial", 12)

    # Menentukan area/posisi tombol di layar
    button_rects = []
    start_y = 70
    button_height = 45
    spacing = 10
    
    for i, item in enumerate(COIL_ITEMS):
        y = start_y + i * (button_height + spacing)
        rect = pygame.Rect(30, y, 460, button_height)
        button_rects.append((rect, item))

    running = True
    while running:
        screen.fill(COLOR_BG)
        
        # Header GUI
        title_surface = font_title.render("MODBUS SERVER SIMULATOR (TCP:502)", True, COLOR_TEXT)
        screen.blit(title_surface, (30, 20))
        
        # Penanganan Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for rect, item in button_rects:
                    if rect.collidepoint(mouse_pos):
                        toggle_coil_value(item["addr"])

        # Render Tombol & Status Coil
        for rect, item in button_rects:
            addr = item["addr"]
            is_active = get_coil_value(addr)
            
            # Warna Tombol
            btn_color = COLOR_BTN_ON if is_active else COLOR_PANEL
            pygame.draw.rect(screen, btn_color, rect, border_radius=6)
            pygame.draw.rect(screen, (70, 70, 85), rect, width=2, border_radius=6)
            
            # Indikator Lampu (Lingkaran)
            ind_color = COLOR_INDICATOR_ON if is_active else COLOR_INDICATOR_OFF
            pygame.draw.circle(screen, ind_color, (rect.x + 25, rect.y + rect.height // 2), 10)
            
            # Teks Nama Coil & Alamat
            label_text = f"{item['name']} [Addr: {addr}]"
            text_color = (20, 20, 20) if is_active else COLOR_TEXT
            text_surface = font_btn.render(label_text, True, text_color)
            screen.blit(text_surface, (rect.x + 50, rect.y + 13))
            
            # Teks Status (ON / OFF)
            status_str = "ON" if is_active else "OFF"
            status_surface = font_status.render(f"STATUS: {status_str}", True, text_color)
            screen.blit(status_surface, (rect.x + rect.width - 100, rect.y + 15))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

# ---------------------------------------------------------
# 4. ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    MODBUS_PORT = 502  # Ganti ke 5020 jika berjalan tanpa sudo/root
    
    # Jalankan Modbus Server di background thread
    server_thread = threading.Thread(target=run_modbus_server, args=("0.0.0.0", MODBUS_PORT), daemon=True)
    server_thread.start()
    
    # Beri jeda sebentar agar server siap
    time.sleep(0.5)
    
    # Jalankan GUI di main thread
    run_gui()