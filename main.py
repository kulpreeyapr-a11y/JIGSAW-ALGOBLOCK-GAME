import pygame
import sys
from PIL import Image

import os

def resource_path(relative_path):
    """ หา Path จริงของไฟล์แม้อยู่ในไฟล์ .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==========================================
# 1. ตั้งค่าพื้นฐาน
# ==========================================
pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jigsaw CodeBlocks - Fullscreen GIF Menu")
clock = pygame.time.Clock()

# --- โทนสี ---
C_WHITE = (255, 255, 255) # สีขาวสำหรับตัวหนังสือเมนู
C_BG = (236, 240, 241)
C_WORKSPACE = (250, 252, 253)
C_GRID = (255, 255, 255)
C_WALL = (52, 73, 94)
C_PLAYER = (52, 152, 219)
C_GOAL = (241, 196, 15)
C_DOOR = (149, 165, 166)   
C_SWITCH = (231, 76, 60)   

C_START = (243, 156, 18)
C_UP = (231, 76, 60)
C_DOWN = (46, 204, 113)
C_LEFT = (155, 89, 182)
C_RIGHT = (41, 128, 185)
C_ACTION = (255, 105, 180)

def get_font(size, bold=False):
    try: return pygame.font.SysFont("tahoma", size, bold=bold)
    except: return pygame.font.Font(None, size + 10)

font_xl = get_font(70, True) # ปรับขนาดหัวข้อให้ใหญ่ขึ้น
font_l = get_font(32, True)
font_m = get_font(24, True)

# ==========================================
# 2. คลาสสำหรับเล่น GIF แบบเต็มจอ
# ==========================================
class SimpleGIF:
    def __init__(self, filename, target_size=(WIDTH, HEIGHT)):
        self.frames = []
        self.duration = 100
        try:
            pil_image = Image.open(filename)
            self.duration = pil_image.info.get('duration', 100)
            if self.duration < 20: self.duration = 100 # กันเหนียวถ้าไฟล์ตั้งค่ามาเร็วเกินไป
                
            try:
                while True:
                    frame = pil_image.convert('RGBA')
                    img_data = frame.tobytes()
                    img_size = frame.size
                    py_img = pygame.image.fromstring(img_data, img_size, 'RGBA')
                    # ปรับขนาดภาพให้เต็มจอ WIDTH, HEIGHT
                    py_img = pygame.transform.scale(py_img, target_size)
                    self.frames.append(py_img)
                    pil_image.seek(pil_image.tell() + 1)
            except EOFError:
                pass 
        except Exception as e:
            print(f"Error loading GIF: {e}")
            err_surf = pygame.Surface(target_size)
            err_surf.fill((50, 50, 50))
            self.frames.append(err_surf)

        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def draw(self, surface, x, y):
        if not self.frames: return
        now = pygame.time.get_ticks()
        if now - self.last_update > self.duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now
        surface.blit(self.frames[self.current_frame], (x, y))

# ==========================================
# 3. ฟังก์ชันวาดจิ๊กซอว์ & ปุ่มกด
# ==========================================
def get_jigsaw_points(x, y, w=200, h=45, is_start=False):
    tx, tw, th = 25, 30, 10 
    if is_start:
        return [(x+15, y), (x+w-15, y), (x+w, y+15), (x+w, y+h),
               (x+tx+tw, y+h), (x+tx+tw-5, y+h+th), (x+tx+5, y+h+th), (x+tx, y+h),
               (x, y+h), (x, y+15)]
    else:
        return [(x, y), (x+tx, y), (x+tx+5, y+th), (x+tx+tw-5, y+th), (x+tx+tw, y),
               (x+w, y), (x+w, y+h),
               (x+tx+tw, y+h), (x+tx+tw-5, y+h+th), (x+tx+5, y+h+th), (x+tx, y+h),
               (x, y+h)]

def draw_jigsaw_block(surface, x, y, text, color, is_start=False, alpha=255):
    pts = get_jigsaw_points(x, y, is_start=is_start)
    if alpha < 255:
        s = pygame.Surface((200, 55), pygame.SRCALPHA)
        offset_pts = [(px-x, py-y) for px, py in pts]
        pygame.draw.polygon(s, (*color, alpha), offset_pts)
        pygame.draw.polygon(s, (0,0,0, alpha), offset_pts, 2)
        txt_surf = font_m.render(text, True, (255, 255, 255))
        txt_surf.set_alpha(alpha)
        s.blit(txt_surf, (25, 10))
        surface.blit(s, (x, y))
    else:
        shadow = [(px+2, py+3) for px, py in pts]
        pygame.draw.polygon(surface, (0, 0, 0, 40), shadow)
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, (0,0,0), pts, 2)
        txt_surf = font_m.render(text, True, (255, 255, 255))
        surface.blit(txt_surf, (x + 25, y + 10))

def draw_jigsaw_outline(surface, x, y, index):
    pts = get_jigsaw_points(x, y)
    pygame.draw.polygon(surface, (235, 240, 245), pts)
    pygame.draw.polygon(surface, (200, 210, 220), pts, 2)
    txt = font_m.render(f"{index}.", True, (150, 160, 170))
    surface.blit(txt, (x - 30, y + 10))

class SimpleButton:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (0,0,0), self.rect, 3, border_radius=12)
        txt = font_m.render(self.text, True, (255,255,255))
        surface.blit(txt, txt.get_rect(center=self.rect.center))
    def check_click(self, pos):
        return self.rect.collidepoint(pos)

# ==========================================
# 4. ข้อมูล 10 ด่าน (0=ทาง, 1=กำแพง, 2=เริ่ม, 3=เป้าหมาย, 4=ประตู, 5=สวิตช์)
# ==========================================
LEVELS = [
    [[2, 0, 0, 0, 3]], # ด่าน 1
    [[2, 0, 0], [1, 1, 0], [1, 1, 3]], # ด่าน 2
    [[2, 1, 3], [0, 1, 0], [0, 0, 0]], # ด่าน 3
    [[2, 0, 5], [1, 1, 4], [1, 1, 3]], # ด่าน 4
    [[5, 0, 2, 0, 4, 3]], # ด่าน 5
    [[2, 0, 1, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 0, 1], [1, 1, 1, 0, 3]], # ด่าน 6
    [[2, 1, 0, 0, 3], [0, 1, 0, 1, 0], [0, 0, 0, 1, 0]], # ด่าน 7
    [[2, 0, 0], [1, 1, 0], [5, 4, 0], [1, 1, 3]], # ด่าน 8
    [[2, 0, 0, 1, 3], [1, 1, 0, 1, 4], [5, 0, 0, 0, 0]], # ด่าน 9
    [[5, 1, 0, 0, 3], [0, 1, 4, 1, 0], [0, 0, 2, 0, 0]] # ด่าน 10
]

# ==========================================
# 5. ระบบเกมหลัก
# ==========================================
class CodeGame:
    def __init__(self):
        self.state = "MAIN_MENU"
        self.current_level = 0
        
        # โหลดไฟล์ GIF แบบเต็มจอ 1000x750
        # จากเดิม
        # self.menu_gif = SimpleGIF("Image/Wallpaper.gif", (WIDTH, HEIGHT))
        self.menu_gif = SimpleGIF(resource_path("Image/Wallpaper.gif"), (WIDTH, HEIGHT))
        
        self.btn_start = SimpleButton(WIDTH//2 - 110, HEIGHT//2 + 80, 220, 70, "เข้าสู่การผจญภัย", (46, 204, 113))
        self.btn_run = SimpleButton(630, 680, 150, 50, "รันโปรแกรม", (46, 204, 113))
        self.btn_clear = SimpleButton(820, 680, 120, 50, "เคลียร์", (231, 76, 60))
        self.btn_next = SimpleButton(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "ด่านต่อไป >>", C_PLAYER)

        self.dragging_cmd = None
        self.mouse_x, self.mouse_y = 0, 0
        self.drag_offset_x, self.drag_offset_y = 0, 0
        self.scroll_y = 0

    def load_level(self):
        self.map_data = [row[:] for row in LEVELS[self.current_level]]
        self.rows, self.cols = len(self.map_data), len(self.map_data[0])
        for r in range(self.rows):
            for c in range(self.cols):
                if self.map_data[r][c] == 2: self.start_pos = (r, c)
                elif self.map_data[r][c] == 3: self.goal_pos = (r, c)
        
        self.sequence = []
        self.scroll_y = 0 
        self.reset_player()
        self.state = "BUILDING"

    def reset_player(self):
        self.p_row, self.p_col = self.start_pos
        self.exec_idx = 0
        self.last_move = 0
        self.map_data = [row[:] for row in LEVELS[self.current_level]]

    def draw_menu(self):
        # 1. วาด GIF พื้นหลังเต็มหน้าจอ
        self.menu_gif.draw(screen, 0, 0)
        
        # 2. วาด Layer มืดทับเบาๆ เพื่อให้ตัวอักษรอ่านง่ายขึ้น (Overlay)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 60)) # สีดำ โปร่งแสง 60
        screen.blit(overlay, (0, 0))
        
        # 3. วาดข้อความสีขาว
        txt_title = font_xl.render("10 LEVELS ADVENTURE", True, C_WHITE)
        rect_title = txt_title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
        
        # ใส่เงาเบาๆ ให้ตัวหนังสือ
        txt_shadow = font_xl.render("10 LEVELS ADVENTURE", True, (50, 50, 50))
        screen.blit(txt_shadow, rect_title.move(3, 3))
        screen.blit(txt_title, rect_title)
        
        txt_sub = font_m.render(f"ท้าทายความสามารถของคุณใน {len(LEVELS)} ด่านปริศนา", True, C_WHITE)
        screen.blit(txt_sub, txt_sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
        
        # 4. ปุ่มเริ่มเกม
        self.btn_start.draw(screen)

    def draw_map(self):
        map_w, map_h = self.cols * 80, self.rows * 80
        offset_x = max(50, 50 + (450 - map_w) // 2)
        offset_y = max(100, 100 + (300 - map_h) // 2)

        for r in range(self.rows):
            for c in range(self.cols):
                x, y = offset_x + c * 80, offset_y + r * 80
                rect = pygame.Rect(x, y, 80, 80)
                pygame.draw.rect(screen, C_GRID, rect)
                pygame.draw.rect(screen, (200,210,220), rect, 1)
                
                tile = self.map_data[r][c]
                if tile == 1: pygame.draw.rect(screen, C_WALL, rect.inflate(-10, -10), border_radius=8)
                elif tile == 3: pygame.draw.circle(screen, C_GOAL, rect.center, 25)
                elif tile == 4: 
                    pygame.draw.rect(screen, C_DOOR, rect.inflate(-10, -10))
                    pygame.draw.line(screen, (100,100,100), (x+20, y+10), (x+60, y+70), 3)
                    pygame.draw.line(screen, (100,100,100), (x+60, y+10), (x+20, y+70), 3)
                elif tile == 5:
                    pygame.draw.circle(screen, C_SWITCH, rect.center, 20)
                    pygame.draw.circle(screen, (150, 0, 0), rect.center, 15)

        px, py = offset_x + self.p_col * 80 + 40, offset_y + self.p_row * 80 + 40
        pygame.draw.circle(screen, C_PLAYER, (px, py), 30)
        pygame.draw.circle(screen, (255,255,255), (px-10, py-10), 6)
        pygame.draw.circle(screen, (255,255,255), (px+10, py-10), 6)

    def draw_ui(self):
        screen.blit(font_l.render(f"ด่านที่ {self.current_level + 1} / {len(LEVELS)}", True, (44, 62, 80)), (50, 40))
        pygame.draw.rect(screen, (220, 230, 235), (50, 400, 500, 320), border_radius=15)
        
        draw_jigsaw_block(screen, 70, 430, "เดินขึ้น", C_UP)
        draw_jigsaw_block(screen, 300, 430, "เดินซ้าย", C_LEFT)
        draw_jigsaw_block(screen, 70, 490, "เดินลง", C_DOWN)
        draw_jigsaw_block(screen, 300, 490, "เดินขวา", C_RIGHT)
        draw_jigsaw_block(screen, 70, 550, "กดสวิตช์", C_ACTION) 

        workspace_rect = pygame.Rect(580, 40, 400, 620)
        pygame.draw.rect(screen, C_WORKSPACE, workspace_rect, border_radius=15)
        
        old_clip = screen.get_clip()
        screen.set_clip(workspace_rect)
        start_x, start_y = 650, 80 + self.scroll_y
        
        for i in range(1, len(self.sequence) + 2):
            draw_jigsaw_outline(screen, start_x, start_y + (i * 45), i)

        for i, cmd in enumerate(self.sequence):
            y_pos = start_y + ((i + 1) * 45)
            c = C_UP if cmd=="UP" else C_DOWN if cmd=="DOWN" else C_LEFT if cmd=="LEFT" else C_RIGHT if cmd=="RIGHT" else C_ACTION
            txt = "เดินขึ้น" if cmd=="UP" else "เดินลง" if cmd=="DOWN" else "เดินซ้าย" if cmd=="LEFT" else "เดินขวา" if cmd=="RIGHT" else "กดสวิตช์"
            if self.state == "RUNNING" and i == self.exec_idx:
                c = (min(255, c[0]+70), min(255, c[1]+70), min(255, c[2]+70))
            draw_jigsaw_block(screen, start_x, y_pos, txt, c)

        draw_jigsaw_block(screen, start_x, start_y, "เมื่อเริ่มงาน", C_START, is_start=True)
        screen.set_clip(old_clip)

        self.btn_run.draw(screen)
        self.btn_clear.draw(screen)

        if self.dragging_cmd:
            c = {"UP":C_UP, "DOWN":C_DOWN, "LEFT":C_LEFT, "RIGHT":C_RIGHT, "ACTION":C_ACTION}[self.dragging_cmd]
            txt = {"UP":"เดินขึ้น", "DOWN":"เดินลง", "LEFT":"เดินซ้าย", "RIGHT":"เดินขวา", "ACTION":"กดสวิตช์"}[self.dragging_cmd]
            draw_jigsaw_block(screen, self.mouse_x - self.drag_offset_x, self.mouse_y - self.drag_offset_y, txt, c, alpha=180)

        if self.state in ["SUCCESS", "FAIL"]:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0, 180))
            screen.blit(s, (0,0))
            if self.state == "SUCCESS":
                txt = font_l.render("ด่านเคลียร์! สุดยอดไปเลย", True, (46, 204, 113))
                screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
                if self.current_level < len(LEVELS) - 1: self.btn_next.draw(screen)
                else:
                    txt2 = font_xl.render("🎉 ภารกิจสำเร็จครบทุกด่าน! 🎉", True, C_GOAL)
                    screen.blit(txt2, txt2.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
            else:
                txt = font_l.render("ลองวางแผนใหม่ดูนะ!", True, (231, 76, 60))
                screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

    def handle_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_x, self.mouse_y = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            if pygame.Rect(580, 40, 400, 620).collidepoint((self.mouse_x, self.mouse_y)):
                self.scroll_y = min(0, self.scroll_y + event.y * 30)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.state == "MAIN_MENU":
                if self.btn_start.check_click(pos): self.load_level()
                return
            if self.state in ["SUCCESS", "FAIL"]:
                if self.state == "SUCCESS" and self.current_level < len(LEVELS) - 1 and self.btn_next.check_click(pos):
                    self.current_level += 1
                    self.load_level()
                else: self.reset_player(); self.state = "BUILDING"
                return

            palette = {"UP":(70,430), "LEFT":(300,430), "DOWN":(70,490), "RIGHT":(300,490), "ACTION":(70,550)}
            for cmd, (x, y) in palette.items():
                if pygame.Rect(x, y, 200, 45).collidepoint(pos):
                    self.dragging_cmd = cmd
                    self.drag_offset_x, self.drag_offset_y = pos[0]-x, pos[1]-y
                    return
            
            start_x, start_y = 650, 80 + self.scroll_y
            if pygame.Rect(580, 40, 400, 620).collidepoint(pos):
                for i in range(len(self.sequence)):
                    if pygame.Rect(start_x, start_y + ((i + 1) * 45), 200, 45).collidepoint(pos):
                        self.dragging_cmd = self.sequence.pop(i)
                        self.drag_offset_x, self.drag_offset_y = pos[0]-start_x, pos[1]-(start_y+((i+1)*45))
                        return

            if self.btn_clear.check_click(pos): self.sequence = []; self.reset_player()
            if self.btn_run.check_click(pos) and self.sequence:
                self.reset_player(); self.state = "RUNNING"; self.last_move = pygame.time.get_ticks()

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_cmd:
                start_x, snap_y = 650, 80 + self.scroll_y + ((len(self.sequence) + 1) * 45)
                if abs(self.mouse_x - start_x) < 100 and abs(self.mouse_y - snap_y) < 60:
                    self.sequence.append(self.dragging_cmd)
                self.dragging_cmd = None

    def run_step(self):
        if self.exec_idx >= len(self.sequence):
            self.state = "SUCCESS" if (self.p_row, self.p_col) == self.goal_pos else "FAIL"
            return
        cmd, nr, nc = self.sequence[self.exec_idx], self.p_row, self.p_col
        if cmd == "UP": nr -= 1
        elif cmd == "DOWN": nr += 1
        elif cmd == "LEFT": nc -= 1
        elif cmd == "RIGHT": nc += 1
        elif cmd == "ACTION" and self.map_data[nr][nc] == 5:
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.map_data[r][c] == 4: self.map_data[r][c] = 0
            self.exec_idx += 1; return

        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.map_data[nr][nc] not in [1, 4]:
            self.p_row, self.p_col = nr, nc
            self.exec_idx += 1
        else: self.state = "FAIL"

    def update(self):
        if self.state == "MAIN_MENU": self.draw_menu()
        else:
            screen.fill(C_BG)
            self.draw_map(); self.draw_ui()
            if self.state == "RUNNING":
                now = pygame.time.get_ticks()
                if now - self.last_move > 500: self.run_step(); self.last_move = now

game = CodeGame()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        game.handle_events(event)
    game.update()
    pygame.display.flip()
    clock.tick(60)