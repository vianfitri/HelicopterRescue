import asyncio
import math
import random
import sys
import pygame
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from pymodbus.datastore.store import ModbusSequentialDataBlock
from pymodbus.payload import BinaryPayloadBuilder, Endian
from pymodbus.server import StartAsyncTcpServer

# ==========================================
# ALAMAT REGISTER MODBUS (0-based indexing)
# ==========================================
ADDR_X7 = 7    # LS FWD1 (Discrete Input)
ADDR_X8 = 8    # LS FWD2
ADDR_X9 = 9    # LS REV1
ADDR_X10 = 10  # LS REV2

ADDR_Y0 = 1536  # IND FWD (Coil)
ADDR_Y1 = 1537  # IND REV

ADDR_M1102 = 4174  # IND HOIST UP (Coil)
ADDR_M1103 = 4175  # IND HOIST DOWN

ADDR_V32 = 544     # RPM VALUE (Float32, 2 registers: 544-545)
ADDR_V124 = 636    # HOIST POSITION (UInt32, 2 registers: 636-637)
ADDR_V1004 = 1516  # HELI POSITION / Travel (UInt32, 2 registers: 1516-1517)
ADDR_V1032 = 1544  # LOAD INDICATOR (Float32, 2 registers: 1544-1545)

# Helper konversi data ke 2 register 16-bit Big Endian
def pack_float32(value: float) -> list[int]:
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
    builder.add_32bit_float(value)
    return builder.to_registers()

def pack_uint32(value: int) -> list[int]:
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
    builder.add_32bit_uint(value)
    return builder.to_registers()

# State simulasi global
class SimulationState:
    def __init__(self):
        self.travel_pos = 0     # 0 - 100
        self.hoist_pos = 0      # 0 - 100
        self.travel_cmd = "stop"  # 'fwd', 'rev', 'stop'
        self.hoist_cmd = "stop"   # 'up', 'down', 'stop'
        self.rpm = 0.0
        self.load = 0.0

sim_state = SimulationState()

async def simulation_loop(context: ModbusServerContext):
    """Task latar belakang untuk memproses logika simulasi PLC dan pembaruan Modbus."""
    slave_id = 1

    while True:
        # 1. LOGIKA SIMULASI TRAVEL (0 - 100)
        if sim_state.travel_cmd == "fwd":
            if sim_state.travel_pos < 100:
                sim_state.travel_pos += 1
            context[slave_id].setValues(1, ADDR_Y0, [True])   # Y0 ON
            context[slave_id].setValues(1, ADDR_Y1, [False])  # Y1 OFF
            sim_state.rpm = random.uniform(6.0, 8.0)

        elif sim_state.travel_cmd == "rev":
            if sim_state.travel_pos > 0:
                sim_state.travel_pos -= 1
            context[slave_id].setValues(1, ADDR_Y0, [False])  # Y0 OFF
            context[slave_id].setValues(1, ADDR_Y1, [True])   # Y1 ON
            sim_state.rpm = random.uniform(6.0, 8.0)

        else:
            context[slave_id].setValues(1, ADDR_Y0, [False])  # Y0 OFF
            context[slave_id].setValues(1, ADDR_Y1, [False])  # Y1 OFF
            sim_state.rpm = 0.0

        # Logika Limit Switch (NC: True = Normal/Unpressed, False = Triggered)
        if sim_state.travel_pos == 0:
            ls_fwd = [True, True]    # X7, X8
            ls_rev = [False, False]  # X9, X10 (Triggered)
        elif sim_state.travel_pos == 100:
            ls_fwd = [False, False]  # X7, X8 (Triggered)
            ls_rev = [True, True]    # X9, X10
        else:
            ls_fwd = [True, True]
            ls_rev = [True, True]

        context[slave_id].setValues(2, ADDR_X7, ls_fwd)
        context[slave_id].setValues(2, ADDR_X9, ls_rev)
        context[slave_id].setValues(3, ADDR_V1004, pack_uint32(sim_state.travel_pos))
        context[slave_id].setValues(3, ADDR_V32, pack_float32(sim_state.rpm))

        # 2. LOGIKA SIMULASI HOIST (0 - 100)
        if sim_state.hoist_cmd == "up":
            if sim_state.hoist_pos < 100:
                sim_state.hoist_pos += 1
            context[slave_id].setValues(1, ADDR_M1102, [True])   # M1102 ON
            context[slave_id].setValues(1, ADDR_M1103, [False])  # M1103 OFF
            sim_state.load = random.uniform(100.0, 300.0)

        elif sim_state.hoist_cmd == "down":
            if sim_state.hoist_pos > 0:
                sim_state.hoist_pos -= 1
            context[slave_id].setValues(1, ADDR_M1102, [False])  # M1102 OFF
            context[slave_id].setValues(1, ADDR_M1103, [True])   # M1103 ON
            sim_state.load = random.uniform(100.0, 300.0)

        else:
            context[slave_id].setValues(1, ADDR_M1102, [False])  # M1102 OFF
            context[slave_id].setValues(1, ADDR_M1103, [False])  # M1103 OFF
            sim_state.load = 0.0

        context[slave_id].setValues(3, ADDR_V124, pack_uint32(sim_state.hoist_pos))
        context[slave_id].setValues(3, ADDR_V1032, pack_float32(sim_state.load))

        await asyncio.sleep(0.1)  # Kecepatan step simulasi (100 ms)


async def pygame_gui_loop(context: ModbusServerContext):
    """Task utama untuk merender antarmuka Pygame dan menangani Event Keyboard/Mouse."""
    pygame.init()
    screen = pygame.display.set_mode((900, 580))
    pygame.display.set_caption("Haiwell PLC Server Simulator - Interactive Dashboard")

    font_title = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_body = pygame.font.SysFont("Consolas", 14, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 12)

    # Warna Tema
    COLOR_BG = (24, 28, 36)
    COLOR_PANEL = (35, 41, 53)
    COLOR_BORDER = (55, 65, 81)
    COLOR_TEXT = (230, 235, 240)
    COLOR_GREEN = (46, 204, 113)
    COLOR_RED = (231, 76, 60)
    COLOR_BLUE = (52, 152, 219)
    COLOR_GRAY = (100, 110, 120)
    COLOR_ACCENT = (241, 196, 15)

    slave_id = 1

    def draw_indicator(surface, x, y, label, is_active, active_color=COLOR_GREEN):
        """Helper untuk menggambar indikator status bundar."""
        color = active_color if is_active else COLOR_GRAY
        pygame.draw.circle(surface, color, (x, y), 9)
        pygame.draw.circle(surface, COLOR_BORDER, (x, y), 9, 2)
        txt = font_small.render(label, True, COLOR_TEXT)
        surface.blit(txt, (x + 15, y - 6))

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    sim_state.travel_cmd = "fwd"
                elif event.key == pygame.K_s:
                    sim_state.travel_cmd = "rev"
                elif event.key == pygame.K_a:
                    sim_state.travel_cmd = "stop"
                elif event.key == pygame.K_i:
                    sim_state.hoist_cmd = "up"
                elif event.key == pygame.K_k:
                    sim_state.hoist_cmd = "down"
                elif event.key == pygame.K_j:
                    sim_state.hoist_cmd = "stop"
                elif event.key == pygame.K_q:
                    running = False

        # Mode non-blocking redraw
        screen.fill(COLOR_BG)

        # -----------------------------------------------------------
        # 1. HEADER PANEL
        # -----------------------------------------------------------
        pygame.draw.rect(screen, COLOR_PANEL, (15, 15, 870, 45), border_radius=6)
        title_txt = font_title.render("HAIWELL PLC MODBUS TCP SERVER SIMULATOR", True, COLOR_ACCENT)
        screen.blit(title_txt, (30, 25))

        # -----------------------------------------------------------
        # 2. VISUALISASI PERGERAKAN (TRAVEL & HOIST)
        # -----------------------------------------------------------
        pygame.draw.rect(screen, COLOR_PANEL, (15, 70, 560, 360), border_radius=6)
        pygame.draw.rect(screen, COLOR_BORDER, (15, 70, 560, 360), width=2, border_radius=6)

        # Rail Travel (Horizontal)
        rail_y = 160
        rail_start_x = 60
        rail_end_x = 530
        pygame.draw.line(screen, COLOR_GRAY, (rail_start_x, rail_y), (rail_end_x, rail_y), 6)

        # Hitung Posisi Trolley berdasarkan Travel Position (0 - 100)
        trolley_x = rail_start_x + int((sim_state.travel_pos / 100.0) * (rail_end_x - rail_start_x))
        trolley_y = rail_y - 12

        # Draw Limit Switches pada Visual
        ls_fwd_active = not context[slave_id].getValues(2, ADDR_X7, 1)[0]
        ls_rev_active = not context[slave_id].getValues(2, ADDR_X9, 1)[0]
        draw_indicator(screen, rail_start_x, rail_y - 25, "LS REV (X9,X10)", ls_rev_active, COLOR_RED)
        draw_indicator(screen, rail_end_x - 100, rail_y - 25, "LS FWD (X7,X8)", ls_fwd_active, COLOR_RED)

        # Gambar Trolley
        pygame.draw.rect(screen, COLOR_BLUE, (trolley_x - 20, trolley_y, 40, 24), border_radius=4)

        # Kabel Hoist (Vertical)
        max_cable_len = 180
        cable_len = int((sim_state.hoist_pos / 100.0) * max_cable_len)
        hook_y = trolley_y + 24 + cable_len
        pygame.draw.line(screen, COLOR_ACCENT, (trolley_x, trolley_y + 24), (trolley_x, hook_y), 2)

        # Gambar Beban / Hook
        pygame.draw.rect(screen, COLOR_RED, (trolley_x - 12, hook_y, 24, 20), border_radius=3)

        # Data overlay pada visualizer
        txt_t_pos = font_body.render(f"TRAVEL POS (V1004): {sim_state.travel_pos}/100", True, COLOR_TEXT)
        txt_h_pos = font_body.render(f"HOIST POS  (V124) : {sim_state.hoist_pos}/100", True, COLOR_TEXT)
        screen.blit(txt_t_pos, (30, 370))
        screen.blit(txt_h_pos, (30, 395))

        # -----------------------------------------------------------
        # 3. MONITOR I/O & STATUS REGISTER
        # -----------------------------------------------------------
        pygame.draw.rect(screen, COLOR_PANEL, (590, 70, 295, 360), border_radius=6)
        pygame.draw.rect(screen, COLOR_BORDER, (590, 70, 295, 360), width=2, border_radius=6)

        lbl_io = font_title.render("REGISTER MONITOR", True, COLOR_TEXT)
        screen.blit(lbl_io, (605, 82))

        # Ambil status real-time dari DataStore Modbus
        y0_val = context[slave_id].getValues(1, ADDR_Y0, 1)[0]
        y1_val = context[slave_id].getValues(1, ADDR_Y1, 1)[0]
        m1102_val = context[slave_id].getValues(1, ADDR_M1102, 1)[0]
        m1103_val = context[slave_id].getValues(1, ADDR_M1103, 1)[0]

        start_y = 125
        gap = 28
        draw_indicator(screen, 605, start_y + 0 * gap, f"Y0    : IND FWD ({int(y0_val)})", y0_val)
        draw_indicator(screen, 605, start_y + 1 * gap, f"Y1    : IND REV ({int(y1_val)})", y1_val)
        draw_indicator(screen, 605, start_y + 2 * gap, f"M1102 : IND HOIST UP ({int(m1102_val)})", m1102_val)
        draw_indicator(screen, 605, start_y + 3 * gap, f"M1103 : IND HOIST DN ({int(m1103_val)})", m1103_val)

        # Floating Point Register Values
        txt_rpm = font_body.render(f"V32   (RPM) : {sim_state.rpm:.2f}", True, COLOR_ACCENT)
        txt_load = font_body.render(f"V1032 (LOAD): {sim_state.load:.2f}", True, COLOR_ACCENT)
        screen.blit(txt_rpm, (605, start_y + 5 * gap))
        screen.blit(txt_load, (605, start_y + 6 * gap))

        # -----------------------------------------------------------
        # 4. KONTROL KEYBOARD INSTRUCTION PANEL
        # -----------------------------------------------------------
        pygame.draw.rect(screen, COLOR_PANEL, (15, 440, 870, 125), border_radius=6)
        pygame.draw.rect(screen, COLOR_BORDER, (15, 440, 870, 125), width=2, border_radius=6)

        lbl_ctrl = font_title.render("KONTROL KEYBOARD SIMULASI", True, COLOR_TEXT)
        screen.blit(lbl_ctrl, (30, 450))

        c1 = font_small.render("[W] Travel Maju (FWD)   | [S] Travel Mundur (REV) | [A] Stop Travel", True, COLOR_TEXT)
        c2 = font_small.render("[I] Hoist Naik (UP)     | [K] Hoist Turun (DOWN)  | [J] Stop Hoist", True, COLOR_TEXT)
        c3 = font_small.render("[Q] Keluar Simulator", True, COLOR_RED)

        screen.blit(c1, (30, 480))
        screen.blit(c2, (30, 500))
        screen.blit(c3, (30, 520))

        pygame.display.flip()
        await asyncio.sleep(0.03)  # Render ~30 FPS

    pygame.quit()
    asyncio.get_event_loop().stop()


async def main():
    # Inisialisasi Alokasi Data Block Modbus (0-Based)
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [False] * 2000),
        co=ModbusSequentialDataBlock(0, [False] * 5000),
        hr=ModbusSequentialDataBlock(0, [0] * 2000),
        ir=ModbusSequentialDataBlock(0, [0] * 2000),
        zero_mode=True,
    )
    context = ModbusServerContext(slaves=store, single=True)

    # Jalankan simulasi logika & GUI dalam asyncio task bersamaan
    asyncio.create_task(simulation_loop(context))
    asyncio.create_task(pygame_gui_loop(context))

    # Jalankan Modbus TCP Server pada Port 502
    print("Memulai Modbus TCP Server di 0.0.0.0:502...")
    await StartAsyncTcpServer(context=context, address=("0.0.0.0", 502))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nSimulator Berhenti.")