"""
ОКФРС. Практика 5. Задание 12.
Многооконный интерфейс — кассетный магнитофон.
Премиум-стиль 2026.
"""
import tkinter as tk
import sys, os, math, random, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# ПАЛИТРА
# ============================================================
BG_DEEP    = "#08090f"
BG_GLASS   = "#131823"
BG_METAL   = "#1a1f2e"
BG_PANEL   = "#0d1017"
BORDER     = "#232a3d"

NEON_CYAN  = "#00f0ff"
NEON_GREEN = "#39ff88"
NEON_PINK  = "#ff3ea5"
NEON_PURP  = "#a066ff"
NEON_AMBER = "#ffb830"
NEON_RED   = "#ff4d5e"
NEON_BLUE  = "#4d8dff"

TEXT_MAIN  = "#e8f0ff"
TEXT_DIM   = "#5a6780"
TEXT_GLOW  = "#8fa4c4"

FONT_MONO  = ("Consolas", 13, "bold")
FONT_MONO_S= ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_LABEL_S = ("Segoe UI", 9)
FONT_VAL   = ("Consolas", 16, "bold")
FONT_BIG   = ("Consolas", 26, "bold")
FONT_LCD   = ("Consolas", 36, "bold")


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t))


def round_rect(canvas, x1, y1, x2, y2, r,
               fill=None, outline=None, width=1, tags=""):
    pts = []
    steps = 6
    for i in range(steps + 1):
        a = math.pi + (math.pi / 2) * (i / steps)
        pts.extend([x1 + r + r * math.cos(a), y1 + r + r * math.sin(a)])
    for i in range(steps + 1):
        a = -math.pi/2 + (math.pi / 2) * (i / steps)
        pts.extend([x2 - r + r * math.cos(a), y1 + r + r * math.sin(a)])
    for i in range(steps + 1):
        a = 0 + (math.pi / 2) * (i / steps)
        pts.extend([x2 - r + r * math.cos(a), y2 - r + r * math.sin(a)])
    for i in range(steps + 1):
        a = math.pi/2 + (math.pi / 2) * (i / steps)
        pts.extend([x1 + r + r * math.cos(a), y2 - r + r * math.sin(a)])
    return canvas.create_polygon(pts, fill=fill or "", outline=outline or "",
                                 width=width, smooth=False, tags=tags)


# ============================================================
# СОСТОЯНИЕ МАГНИТОФОНА
# ============================================================
class CassetteState:
    def __init__(self):
        self.mode = "STOP"       # STOP | PLAY | PAUSE | REC | REW | FF
        self.position = 0.0       # 0..1 (позиция ленты)
        self.spin_angle_left = 0.0
        self.spin_angle_right = 0.0
        self.time_sec = 0.0        # время воспроизведения
        self.level_l = 0.0
        self.level_r = 0.0
        self.peak_l = 0.0
        self.peak_r = 0.0
        self.track_index = 0
        self.tracks = [
            "01 · A-HA — Take On Me",
            "02 · DEPECHE MODE — Personal Jesus",
            "03 · THE CURE — Friday I'm In Love",
            "04 · NEW ORDER — Blue Monday",
            "05 · EURYTHMICS — Sweet Dreams",
            "06 · DURAN DURAN — Hungry Like the Wolf",
            "07 · BON JOVI — Livin' On A Prayer",
            "08 · QUEEN — Radio Ga Ga",
        ]
        self.pulse_t = 0.0
        self.history = []     # история проигрывания

    def tick(self, dt):
        self.pulse_t += dt

        # скорость вращения катушек
        if self.mode == "PLAY":
            speed = 2.5
            self.position += dt * 0.008
            self.time_sec += dt
        elif self.mode == "REC":
            speed = 2.5
            self.position += dt * 0.008
            self.time_sec += dt
        elif self.mode == "FF":
            speed = 15.0
            self.position += dt * 0.05
            self.time_sec += dt * 4
        elif self.mode == "REW":
            speed = -15.0
            self.position -= dt * 0.05
            self.time_sec = max(0, self.time_sec - dt * 4)
        elif self.mode == "PAUSE":
            speed = 0.0
        else:  # STOP
            speed = 0.0

        # вращение катушек
        self.spin_angle_left += speed * dt * 60
        self.spin_angle_right -= speed * dt * 60 * 0.8  # разная скорость

        # границы позиции
        self.position = max(0.0, min(1.0, self.position))
        if self.position >= 1.0 and self.mode in ("PLAY", "FF", "REC"):
            self.position = 0.0
            self.time_sec = 0.0
            self.track_index = (self.track_index + 1) % len(self.tracks)
            self.history.insert(0, self.tracks[self.track_index])
            if len(self.history) > 5:
                self.history.pop()

        # индикаторы уровня
        if self.mode in ("PLAY", "REC"):
            # динамический уровень
            t = self.pulse_t
            self.level_l = 0.55 + 0.35 * math.sin(t * 3.2) + random.uniform(-0.1, 0.1)
            self.level_r = 0.55 + 0.35 * math.sin(t * 3.2 + 0.7) + random.uniform(-0.1, 0.1)
            self.level_l = max(0.05, min(1.0, self.level_l))
            self.level_r = max(0.05, min(1.0, self.level_r))
        else:
            self.level_l *= 0.9
            self.level_r *= 0.9

        # пики
        if self.level_l > self.peak_l:
            self.peak_l = self.level_l
            self.peak_hold_l = 0.0
        else:
            self.peak_hold_l = getattr(self, "peak_hold_l", 0) + dt
            if self.peak_hold_l > 0.6:
                self.peak_l = max(self.level_l, self.peak_l - dt * 0.5)

        if self.level_r > self.peak_r:
            self.peak_r = self.level_r
            self.peak_hold_r = 0.0
        else:
            self.peak_hold_r = getattr(self, "peak_hold_r", 0) + dt
            if self.peak_hold_r > 0.6:
                self.peak_r = max(self.level_r, self.peak_r - dt * 0.5)

    def time_str(self):
        m = int(self.time_sec // 60)
        s = int(self.time_sec % 60)
        return f"{m:02d}:{s:02d}"


# ============================================================
# КАТУШКА
# ============================================================
def draw_reel(canvas, cx, cy, r, angle_deg, side="left", color=NEON_AMBER):
    """Рисует катушку с вращением."""
    # тень
    canvas.create_oval(cx - r - 3, cy - r + 4, cx + r + 3, cy + r + 8,
                       fill="#000000", outline="")

    # корпус катушки — тёмный
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#1a1f2e",
                       outline=lerp(color, "#000000", 0.5), width=3)
    canvas.create_oval(cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4,
                       fill="#0f1520",
                       outline=lerp(color, BG_DEEP, 0.4), width=1)

    # лента (внутреннее кольцо)
    inner_r = r - 12
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#3a2a15",
                       outline="#4a3520", width=1)

    # намотанная лента
    tape_r = inner_r - 4
    canvas.create_oval(cx - tape_r, cy - tape_r,
                       cx + tape_r, cy + tape_r,
                       fill="#2a1a05",
                       outline="#4a3520", width=1)

    # спицы катушки (вращаются)
    a_rad = math.radians(angle_deg)
    n_spokes = 6
    for i in range(n_spokes):
        ang = a_rad + i * (2 * math.pi / n_spokes)
        x1 = cx + 10 * math.cos(ang)
        y1 = cy - 10 * math.sin(ang)
        x2 = cx + (tape_r - 4) * math.cos(ang)
        y2 = cy - (tape_r - 4) * math.sin(ang)
        canvas.create_line(x1, y1, x2, y2,
                           fill=lerp(color, "#000000", 0.3),
                           width=3)

    # центральная втулка
    canvas.create_oval(cx - 15, cy - 15, cx + 15, cy + 15,
                       fill="#2a3040",
                       outline=color, width=2)
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill="#0a0d14",
                       outline=color, width=1)

    # центральная точка
    canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                       fill=color, outline="")


# ============================================================
# КНОПКА УПРАВЛЕНИЯ
# ============================================================
def draw_ctrl_button(canvas, x, y, w, h, label, color, active, key):
    # активная — подсвечена
    if active:
        # свечение
        for k in range(4, 0, -1):
            gcol = lerp(color, BG_DEEP, k / 5)
            round_rect(canvas, x - k, y - k, x + w + k, y + h + k,
                       8 + k, outline=gcol, width=1)
        round_rect(canvas, x, y, x + w, y + h, 8,
                   fill=lerp(color, BG_DEEP, 0.6),
                   outline=color, width=3)
        fg = color
    else:
        round_rect(canvas, x, y, x + w, y + h, 8,
                   fill=BG_METAL,
                   outline="#2a3040", width=2)
        fg = TEXT_GLOW

    # символ
    canvas.create_text(x + w / 2, y + h / 2 - 6,
                       text=label, fill=fg,
                       font=("Segoe UI", 18, "bold"))
    # подпись
    canvas.create_text(x + w / 2, y + h - 12,
                       text=key, fill=TEXT_DIM,
                       font=("Segoe UI", 7, "bold"))


# ============================================================
# ГЛАВНАЯ ОТРИСОВКА МАГНИТОФОНА
# ============================================================
def draw_tape_deck(canvas, x, y, w, h, st):
    """Рисует весь магнитофон."""
    # корпус
    round_rect(canvas, x, y, x + w, y + h, 20,
               fill=BG_METAL,
               outline=lerp(NEON_AMBER, "#000000", 0.7), width=2)

    # верхняя панель с брендом
    round_rect(canvas, x + 15, y + 15, x + w - 15, y + 65, 12,
               fill="#0f1520", outline="#2a3040", width=1)
    canvas.create_text(x + 35, y + 40, anchor="w",
                       text="⚡ CASSETTE DECK",
                       fill=NEON_AMBER, font=("Segoe UI", 16, "bold"))
    canvas.create_text(x + w - 35, y + 40, anchor="e",
                       text="MODEL CX-2026 · STEREO",
                       fill=TEXT_DIM, font=FONT_LABEL_S)

    # LED-индикатор питания
    canvas.create_oval(x + w - 130, y + 32, x + w - 118, y + 44,
                       fill=NEON_GREEN, outline="")
    canvas.create_text(x + w - 110, y + 38, anchor="w",
                       text="PWR", fill=NEON_GREEN,
                       font=("Consolas", 8, "bold"))

    # ═══════════════════════════════════════
    # ЛЕВАЯ ЧАСТЬ — окно с кассетой и катушками
    # ═══════════════════════════════════════
    case_x = x + 30
    case_y = y + 85
    case_w = (w - 100) * 0.62
    case_h = h - 220

    # корпус кассеты
    round_rect(canvas, case_x, case_y, case_x + case_w, case_y + case_h, 16,
               fill="#0a0d14",
               outline="#3a2a15", width=3)

    # надпись
    canvas.create_text(case_x + case_w/2, case_y + 22,
                       text="◉  NOW PLAYING  ◉",
                       fill=NEON_AMBER, font=FONT_LABEL_S)

    # 2 катушки
    reel_r = min(case_h * 0.32, case_w * 0.2)
    left_cx = case_x + case_w * 0.3
    right_cx = case_x + case_w * 0.7
    reel_cy = case_y + case_h * 0.5

    draw_reel(canvas, left_cx, reel_cy, reel_r,
              st.spin_angle_left, "left", NEON_AMBER)
    draw_reel(canvas, right_cx, reel_cy, reel_r,
              st.spin_angle_right, "right", NEON_AMBER)

    # лента между катушками
    tape_y_top = reel_cy - reel_r * 0.6
    tape_y_bot = reel_cy + reel_r * 0.6
    canvas.create_line(left_cx, tape_y_top, right_cx, tape_y_top,
                       fill="#4a3520", width=3)
    canvas.create_line(left_cx, tape_y_bot, right_cx, tape_y_bot,
                       fill="#4a3520", width=3)

    # заголовок кассеты (название трека)
    canvas.create_text(case_x + case_w/2, case_y + case_h - 30,
                       text=st.tracks[st.track_index],
                       fill=NEON_CYAN, font=FONT_LABEL)

    # ═══════════════════════════════════════
    # ПРАВАЯ ЧАСТЬ — LCD + индикаторы уровня
    # ═══════════════════════════════════════
    right_x = case_x + case_w + 20
    right_w = w - (right_x - x) - 30

    # ─── LCD-ДИСПЛЕЙ ───
    lcd_y = y + 85
    lcd_h = 100
    round_rect(canvas, right_x, lcd_y, right_x + right_w, lcd_y + lcd_h, 12,
               fill="#02060a",
               outline=lerp(NEON_GREEN, BG_DEEP, 0.4), width=2)

    # режим
    mode_colors = {"PLAY": NEON_GREEN, "REC": NEON_RED,
                   "PAUSE": NEON_AMBER, "FF": NEON_CYAN,
                   "REW": NEON_CYAN, "STOP": TEXT_DIM}
    mode_col = mode_colors.get(st.mode, NEON_GREEN)

    canvas.create_text(right_x + 20, lcd_y + 22, anchor="w",
                       text=f"▶ {st.mode}",
                       fill=mode_col,
                       font=("Consolas", 14, "bold"))

    # счётчик
    canvas.create_text(right_x + right_w / 2, lcd_y + 55,
                       text=st.time_str(),
                       fill=NEON_GREEN, font=FONT_LCD)

    # метка дорожки
    canvas.create_text(right_x + 20, lcd_y + lcd_h - 18, anchor="w",
                       text=f"TRACK {st.track_index + 1:02d} / {len(st.tracks):02d}",
                       fill=NEON_GREEN,
                       font=("Consolas", 10, "bold"))

    # прогресс-бар
    bar_w = right_w - 40
    bar_x = right_x + 20
    bar_y = lcd_y + lcd_h - 10
    round_rect(canvas, bar_x, bar_y, bar_x + bar_w, bar_y + 4, 2,
               fill="#0a1a0a", outline="")
    fill_w = bar_w * st.position
    if fill_w > 2:
        round_rect(canvas, bar_x, bar_y, bar_x + fill_w, bar_y + 4, 2,
                   fill=NEON_GREEN)

    # ─── ИНДИКАТОРЫ УРОВНЯ L / R ───
    lvl_y = lcd_y + lcd_h + 20

    for ch, value, peak, color in [("L", st.level_l, st.peak_l, NEON_GREEN),
                                    ("R", st.level_r, st.peak_r, NEON_CYAN)]:
        # метка
        canvas.create_text(right_x + 8, lvl_y + 10, anchor="w",
                           text=ch, fill=color,
                           font=("Consolas", 12, "bold"))

        # бар
        bar_x0 = right_x + 25
        bar_x1 = right_x + right_w - 10
        bar_y0 = lvl_y
        bar_y1 = lvl_y + 22
        round_rect(canvas, bar_x0, bar_y0, bar_x1, bar_y1, 5,
                   fill="#0a0d14", outline="#1a2030", width=1)

        # сегменты LED
        n_seg = 30
        seg_w = (bar_x1 - bar_x0 - 8) / n_seg
        for i in range(n_seg):
            k = i / (n_seg - 1)
            sx = bar_x0 + 4 + i * seg_w
            active = k < value
            if active:
                if k < 0.65:
                    col = NEON_GREEN
                elif k < 0.85:
                    col = NEON_AMBER
                else:
                    col = NEON_RED
            else:
                col = "#141a28"
            canvas.create_rectangle(sx, bar_y0 + 4,
                                    sx + seg_w - 1, bar_y1 - 4,
                                    fill=col, outline="")

        # пиковая метка
        peak_x = bar_x0 + 4 + peak * (bar_x1 - bar_x0 - 8)
        canvas.create_rectangle(peak_x, bar_y0 + 2,
                                peak_x + 3, bar_y1 - 2,
                                fill="#ffffff", outline="")

        lvl_y += 32

    # ═══════════════════════════════════════
    # НИЖНЯЯ ПАНЕЛЬ — КНОПКИ УПРАВЛЕНИЯ
    # ═══════════════════════════════════════
    btn_y = y + h - 105
    btn_h = 70
    btn_w = 90
    btn_gap = 12

    buttons = [
        ("◀◀", "REW", NEON_CYAN, "rew"),
        ("▶", "PLAY", NEON_GREEN, "play"),
        ("❚❚", "PAUSE", NEON_AMBER, "pause"),
        ("■", "STOP", NEON_RED, "stop"),
        ("▶▶", "FF", NEON_CYAN, "ff"),
        ("●", "REC", NEON_RED, "rec"),
    ]

    # центрируем кнопки
    total_w = len(buttons) * btn_w + (len(buttons) - 1) * btn_gap
    bx_start = x + (w - total_w) / 2

    zones = {}
    for i, (sym, key, col, mode) in enumerate(buttons):
        bx = bx_start + i * (btn_w + btn_gap)
        active = (st.mode == key)
        draw_ctrl_button(canvas, bx, btn_y, btn_w, btn_h,
                         sym, col, active, key)
        zones[mode] = (bx, btn_y, bx + btn_w, btn_y + btn_h)

    return zones


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("📼 Cassette Deck · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.st = CassetteState()
        self.st.history.insert(0, self.st.tracks[0])

        self.W, self.H = 1500, 950
        self.btn_zones = {}

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

        self.root.update_idletasks()
        self._redraw_all()
        self._animate()

    def _on_resize(self, event):
        self._redraw_all()

    def _redraw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        # фон
        for i in range(40):
            y0 = int(i * h / 40)
            y1 = int((i + 1) * h / 40)
            col = lerp(BG_DEEP, "#0a0e18", i / 40)
            self.canvas.create_rectangle(0, y0, w, y1, fill=col, outline="")

        # сетка
        for x in range(0, w, 60):
            self.canvas.create_line(x, 0, x, h, fill="#0d1220")
        for y in range(0, h, 60):
            self.canvas.create_line(0, y, w, y, fill="#0d1220")

        # заголовок
        self.canvas.create_text(60, 40, text="📼",
                                fill=NEON_AMBER,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="CASSETTE DECK",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(340, 44, text="· LAB SERIES 2026",
                                fill=NEON_AMBER, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # основной магнитофон
        deck_x = 40
        deck_y = 90
        deck_w = w - 80
        deck_h = h - 280

        self.btn_zones = draw_tape_deck(self.canvas, deck_x, deck_y,
                                        deck_w, deck_h, self.st)

        # история воспроизведения
        self._draw_history(w, h)

        # подсказка
        self.canvas.create_text(w / 2, h - 20,
                                text="Кликни по кнопкам ниже — управляй магнитофоном",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _draw_history(self, w, h):
        """Журнал проигранных треков."""
        x = 40
        y = h - 170
        ww = w - 80
        hh = 140

        round_rect(self.canvas, x, y, x + ww, y + hh, 14,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(x + 20, y + 24, anchor="w",
                                text="▸ ЖУРНАЛ ВОСПРОИЗВЕДЕНИЯ",
                                fill=NEON_CYAN, font=FONT_LABEL)
        self.canvas.create_text(x + ww - 20, y + 24, anchor="e",
                                text=f"{len(self.st.history)} записей",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        self.canvas.create_line(x + 15, y + 38, x + ww - 15, y + 38,
                                fill=BORDER)

        for i, track in enumerate(self.st.history[:5]):
            ty = y + 58 + i * 20
            color = NEON_AMBER if i == 0 else TEXT_GLOW
            marker = "▶" if i == 0 else " "
            self.canvas.create_text(x + 25, ty, anchor="w",
                                    text=marker,
                                    fill=NEON_GREEN,
                                    font=FONT_MONO_S)
            self.canvas.create_text(x + 50, ty, anchor="w",
                                    text=track,
                                    fill=color, font=FONT_MONO_S)

    def _on_click(self, event):
        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self._do_action(key)
                return

    def _do_action(self, action):
        if action == "play":
            if self.st.mode != "PLAY":
                self.st.mode = "PLAY"
                self.st.history.insert(0, self.st.tracks[self.st.track_index])
                if len(self.st.history) > 8:
                    self.st.history.pop()
        elif action == "pause":
            if self.st.mode == "PAUSE":
                self.st.mode = "PLAY"
            else:
                self.st.mode = "PAUSE"
        elif action == "stop":
            self.st.mode = "STOP"
            self.st.time_sec = 0.0
            self.st.position = 0.0
        elif action == "ff":
            self.st.mode = "FF"
        elif action == "rew":
            self.st.mode = "REW"
        elif action == "rec":
            self.st.mode = "REC"

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self.st.tick(dt)

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()