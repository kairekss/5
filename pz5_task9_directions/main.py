"""
ОКФРС. Практика 5. Задание 9.
Индикаторы направления — 5 стилей.
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
BORDER     = "#232a3d"

NEON_CYAN  = "#00f0ff"
NEON_GREEN = "#39ff88"
NEON_PINK  = "#ff3ea5"
NEON_PURP  = "#a066ff"
NEON_AMBER = "#ffb830"
NEON_RED   = "#ff4d5e"
NEON_BLUE  = "#4d8dff"
NEON_ORANGE= "#ff8c42"

TEXT_MAIN  = "#e8f0ff"
TEXT_DIM   = "#5a6780"
TEXT_GLOW  = "#8fa4c4"

FONT_MONO  = ("Consolas", 13, "bold")
FONT_MONO_S= ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_LABEL_S = ("Segoe UI", 9)
FONT_VAL   = ("Consolas", 16, "bold")
FONT_BIG   = ("Consolas", 26, "bold")


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
# СОСТОЯНИЕ
# ============================================================
class DirectionState:
    def __init__(self):
        self.angle = 0.0
        self.target = 0.0
        self.active_sector = None
        self.pulse_t = 0.0
        self.hover_sector = None

    def tick(self):
        diff = self.target - self.angle
        while diff > 180: diff -= 360
        while diff < -180: diff += 360
        if abs(diff) > 0.1:
            self.angle += diff * 0.2
        else:
            self.angle = self.target
        self.pulse_t += 0.06


# ============================================================
# 1. КОМПАС-СТРЕЛКА
# ============================================================
def draw_compass(canvas, cx, cy, r, st, label="КОМПАС"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0f1520",
                       outline=lerp(NEON_AMBER, "#000000", 0.5), width=3)

    inner_r = r - 20
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="#1a2030", width=1)

    for i in range(72):
        a = math.radians(90 - i * 5)
        is_major = (i % 9 == 0)
        is_medium = (i % 3 == 0)
        tick_len = 14 if is_major else (8 if is_medium else 4)
        col = TEXT_GLOW if is_major else ("#4a5360" if is_medium else "#2a3340")
        w = 2 if is_major else 1
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w)

    dirs = [("N", 90, NEON_RED), ("E", 0, NEON_GREEN),
            ("S", 270, TEXT_GLOW), ("W", 180, TEXT_GLOW)]
    for letter, adeg, col in dirs:
        a = math.radians(adeg)
        tx = cx + (inner_r - 42) * math.cos(a)
        ty = cy - (inner_r - 42) * math.sin(a)
        canvas.create_text(tx, ty, text=letter,
                           fill=col,
                           font=("Segoe UI", 16, "bold"))

    a = math.radians(90 - st.angle)
    canvas.create_polygon(cx, cy,
                          cx + 14 * math.cos(a + math.pi/2),
                          cy - 14 * math.sin(a + math.pi/2),
                          cx + (inner_r - 20) * math.cos(a),
                          cy - (inner_r - 20) * math.sin(a),
                          cx + 14 * math.cos(a - math.pi/2),
                          cy - 14 * math.sin(a - math.pi/2),
                          fill=NEON_RED, outline="#000000")
    a2 = a + math.pi
    canvas.create_polygon(cx, cy,
                          cx + 14 * math.cos(a2 + math.pi/2),
                          cy - 14 * math.sin(a2 + math.pi/2),
                          cx + (inner_r - 20) * math.cos(a2),
                          cy - (inner_r - 20) * math.sin(a2),
                          cx + 14 * math.cos(a2 - math.pi/2),
                          cy - 14 * math.sin(a2 - math.pi/2),
                          fill="#ffffff", outline="#000000")

    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill="#1a1f2e",
                       outline=NEON_AMBER, width=2)

    canvas.create_text(cx, cy + r + 30,
                       text=f"{int(st.angle)}°",
                       fill=NEON_AMBER, font=FONT_BIG)
    canvas.create_text(cx, cy + r + 58,
                       text="АЗИМУТ",
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# 2. ТЁМНЫЙ ДЖОЙСТИК
# ============================================================
def draw_dark_joystick(canvas, cx, cy, r, st, label="ДЖОЙСТИК"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    for i in range(8):
        k = i / 8
        rr = r - k * 4
        col = lerp("#2a3040", "#05070c", k)
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill=col, outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline="#3a4250", width=3)

    inner_r = r - 22
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="#1a2030", width=1)

    sectors = [
        ("up",    -90, "▲", NEON_GREEN),
        ("right",   0, "▶", NEON_CYAN),
        ("down",   90, "▼", NEON_AMBER),
        ("left",  180, "◀", NEON_PINK),
    ]

    pulse = 0.5 + 0.5 * math.sin(st.pulse_t)

    for name, adeg, glyph, col in sectors:
        a = math.radians(adeg)
        ax = cx + (inner_r - 30) * math.cos(a)
        ay = cy - (inner_r - 30) * math.sin(a)

        s_start = adeg - 45
        canvas.create_arc(cx - inner_r + 6, cy - inner_r + 6,
                          cx + inner_r - 6, cy + inner_r - 6,
                          start=s_start, extent=90,
                          style="arc",
                          outline="#1a2030", width=12)

        active = (st.active_sector == name) or (st.hover_sector == name)
        if active:
            canvas.create_arc(cx - inner_r + 6, cy - inner_r + 6,
                              cx + inner_r - 6, cy + inner_r - 6,
                              start=s_start, extent=90,
                              style="arc",
                              outline=col, width=12)

        size = 20 + int(4 * pulse) if active else 18
        canvas.create_text(ax, ay, text=glyph,
                           fill=col if active else TEXT_GLOW,
                           font=("Segoe UI", size, "bold"))

    canvas.create_oval(cx - 12, cy - 12, cx + 12, cy + 12,
                       fill="#1a1f2e",
                       outline="#3a4250", width=2)
    canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4,
                       fill=NEON_CYAN, outline="")

    direction_names = {None: "—", "up": "ВВЕРХ", "down": "ВНИЗ",
                       "left": "ВЛЕВО", "right": "ВПРАВО"}
    cur = st.active_sector
    txt = direction_names.get(cur, "—")
    col = NEON_GREEN if cur else TEXT_DIM
    canvas.create_text(cx, cy + r + 30,
                       text=txt, fill=col, font=FONT_BIG)


# ============================================================
# 3. СВЕТЛЫЙ ДЖОЙСТИК
# ============================================================
def draw_light_joystick(canvas, cx, cy, r, st, label="ГЕЙМПАД"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#f5f7ff",
                       outline=NEON_ORANGE, width=3)
    canvas.create_oval(cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
                       fill="#ffffff", outline="#e8ebf5", width=1)

    inner_r = r - 22
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#ffffff", outline="#d0d5e5", width=1)

    sectors = [
        ("up",    -90, "↑", NEON_ORANGE),
        ("right",   0, "→", NEON_ORANGE),
        ("down",   90, "↓", NEON_ORANGE),
        ("left",  180, "←", NEON_ORANGE),
    ]

    for name, adeg, glyph, col in sectors:
        a = math.radians(adeg)
        ax = cx + (inner_r - 32) * math.cos(a)
        ay = cy - (inner_r - 32) * math.sin(a)

        btn_r = 22
        active = (st.active_sector == name) or (st.hover_sector == name)

        canvas.create_oval(ax - btn_r + 2, ay - btn_r + 3,
                           ax + btn_r + 2, ay + btn_r + 3,
                           fill="#c8cfe0", outline="")

        if active:
            canvas.create_oval(ax - btn_r, ay - btn_r,
                               ax + btn_r, ay + btn_r,
                               fill=col, outline="#ffffff", width=2)
            canvas.create_text(ax, ay, text=glyph,
                               fill="#ffffff",
                               font=("Segoe UI", 18, "bold"))
        else:
            canvas.create_oval(ax - btn_r, ay - btn_r,
                               ax + btn_r, ay + btn_r,
                               fill="#ffffff", outline=col, width=2)
            canvas.create_text(ax, ay, text=glyph,
                               fill=col,
                               font=("Segoe UI", 18, "bold"))

    canvas.create_oval(cx - 18, cy - 18, cx + 18, cy + 18,
                       fill="#e8ebf5", outline="#c8cfe0", width=2)
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill=NEON_ORANGE, outline="")

    direction_names = {None: "—", "up": "ВВЕРХ", "down": "ВНИЗ",
                       "left": "ВЛЕВО", "right": "ВПРАВО"}
    cur = st.active_sector
    txt = direction_names.get(cur, "—")
    col = NEON_ORANGE if cur else TEXT_DIM
    canvas.create_text(cx, cy + r + 30,
                       text=txt, fill=col, font=FONT_BIG)


# ============================================================
# 4. СИНИЕ ТОЧКИ
# ============================================================
def draw_dot_compass(canvas, cx, cy, r, st, label="ТОЧКИ"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    for i in range(8):
        k = i / 8
        rr = r - k * 4
        col = lerp("#1a2540", "#05080f", k)
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill=col, outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=NEON_BLUE, width=3)

    inner_r = r - 22
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="#1a2030", width=1)

    for i in range(36):
        a = math.radians(90 - i * 10)
        is_major = (i % 9 == 0)
        tick_len = 8 if is_major else 4
        col = "#3a4560" if is_major else "#1a2030"
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=1)

    pulse = 0.5 + 0.5 * math.sin(st.pulse_t * 2)

    sectors = [
        ("up",    -90, NEON_GREEN),
        ("right",   0, NEON_CYAN),
        ("down",   90, NEON_AMBER),
        ("left",  180, NEON_PINK),
    ]

    dot_r_base = 10
    for name, adeg, col in sectors:
        a = math.radians(adeg)
        dx = cx + (inner_r - 28) * math.cos(a)
        dy = cy - (inner_r - 28) * math.sin(a)

        active = (st.active_sector == name) or (st.hover_sector == name)

        if active:
            for k in range(4, 0, -1):
                orad = dot_r_base + 4 + k * 3 + int(3 * pulse)
                canvas.create_oval(dx - orad, dy - orad,
                                   dx + orad, dy + orad,
                                   fill="", outline=lerp(col, BG_DEEP, k / 5),
                                   width=1)

        r_pt = dot_r_base + (3 if active else 0)
        canvas.create_oval(dx - r_pt, dy - r_pt,
                           dx + r_pt, dy + r_pt,
                           fill=col if active else lerp(col, BG_DEEP, 0.5),
                           outline="#ffffff" if active else col, width=2)
        canvas.create_oval(dx - 3, dy - 3, dx + 3, dy + 3,
                           fill="#ffffff", outline="")

        if active:
            canvas.create_line(cx, cy, dx, dy,
                               fill=col, width=2, dash=(4, 3))

    canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10,
                       fill="#1a1f2e", outline=NEON_BLUE, width=2)

    direction_names = {None: "—", "up": "СЕВЕР", "down": "ЮГ",
                       "left": "ЗАПАД", "right": "ВОСТОК"}
    cur = st.active_sector
    txt = direction_names.get(cur, "—")
    col = NEON_BLUE if cur else TEXT_DIM
    canvas.create_text(cx, cy + r + 30,
                       text=txt, fill=col, font=FONT_BIG)


# ============================================================
# 5. ФИОЛЕТОВЫЙ С СЕКТОРАМИ
# ============================================================
def draw_purple_compass(canvas, cx, cy, r, st, label="СЕКТОРЫ"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    for i in range(8):
        k = i / 8
        rr = r - k * 4
        col = lerp("#2a1f4a", "#0a0518", k)
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill=col, outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=NEON_PURP, width=3)

    inner_r = r - 20
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0518", outline="#2a1f4a", width=1)

    sectors = [
        ("up",    -90, "▲", NEON_GREEN),
        ("right",   0, "▶", NEON_CYAN),
        ("down",   90, "▼", NEON_AMBER),
        ("left",  180, "◀", NEON_PINK),
    ]

    pulse = 0.5 + 0.5 * math.sin(st.pulse_t)

    for name, adeg, glyph, col in sectors:
        active = (st.active_sector == name) or (st.hover_sector == name)
        s_start = adeg - 45 + 2
        extent = 90 - 4

        if active:
            for k in range(3, 0, -1):
                canvas.create_arc(cx - inner_r + 4 - k, cy - inner_r + 4 - k,
                                  cx + inner_r - 4 + k, cy + inner_r - 4 + k,
                                  start=s_start, extent=extent,
                                  style="arc",
                                  outline=lerp(col, BG_DEEP, k / 4),
                                  width=12 + k * 3)
            canvas.create_arc(cx - inner_r + 4, cy - inner_r + 4,
                              cx + inner_r - 4, cy + inner_r - 4,
                              start=s_start, extent=extent,
                              style="arc", outline=col, width=14)
        else:
            canvas.create_arc(cx - inner_r + 4, cy - inner_r + 4,
                              cx + inner_r - 4, cy + inner_r - 4,
                              start=s_start, extent=extent,
                              style="arc", outline="#2a1f4a", width=14)

        a = math.radians(adeg)
        gx = cx + (inner_r - 30) * math.cos(a)
        gy = cy - (inner_r - 30) * math.sin(a)
        size = 22 if active else 18
        canvas.create_text(gx, gy, text=glyph,
                           fill=col if active else lerp(col, "#000000", 0.6),
                           font=("Segoe UI", size, "bold"))

    canvas.create_oval(cx - 25, cy - 25, cx + 25, cy + 25,
                       fill="#0f0520",
                       outline=NEON_PURP, width=2)
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill=NEON_PURP, outline="")

    direction_names = {None: "—", "up": "СЕВЕР", "down": "ЮГ",
                       "left": "ЗАПАД", "right": "ВОСТОК"}
    cur = st.active_sector
    txt = direction_names.get(cur, "—")
    col = NEON_PURP if cur else TEXT_DIM
    canvas.create_text(cx, cy + r + 30,
                       text=txt, fill=col, font=FONT_BIG)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("🧭 Direction Indicators · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.st_compass = DirectionState()
        self.st_dark = DirectionState()
        self.st_light = DirectionState()
        self.st_dots = DirectionState()
        self.st_purple = DirectionState()

        self.all_states = [self.st_compass, self.st_dark, self.st_light,
                           self.st_dots, self.st_purple]

        self.centers = {}

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_motion)

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

        for i in range(40):
            y0 = int(i * h / 40)
            y1 = int((i + 1) * h / 40)
            col = lerp(BG_DEEP, "#0a0e18", i / 40)
            self.canvas.create_rectangle(0, y0, w, y1, fill=col, outline="")

        for x in range(0, w, 60):
            self.canvas.create_line(x, 0, x, h, fill="#0d1220")
        for y in range(0, h, 60):
            self.canvas.create_line(0, y, w, y, fill="#0d1220")

        self.canvas.create_text(60, 40, text="🧭",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="DIRECTION INDICATORS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(420, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        r = min(115, w * 0.062)
        col_x = [w * 0.17, w * 0.50, w * 0.83]
        row_y = [h * 0.30, h * 0.72]

        self._set_center("compass", col_x[0], row_y[0], r)
        draw_compass(self.canvas, col_x[0], row_y[0], r,
                     self.st_compass, "КОМПАС-СТРЕЛКА")

        self._set_center("dark", col_x[1], row_y[0], r)
        draw_dark_joystick(self.canvas, col_x[1], row_y[0], r,
                           self.st_dark, "ТЁМНЫЙ ДЖОЙСТИК")

        self._set_center("light", col_x[2], row_y[0], r)
        draw_light_joystick(self.canvas, col_x[2], row_y[0], r,
                            self.st_light, "СВЕТЛЫЙ ДЖОЙСТИК")

        self._set_center("dots", col_x[0], row_y[1], r)
        draw_dot_compass(self.canvas, col_x[0], row_y[1], r,
                         self.st_dots, "4 ТОЧКИ")

        self._set_center("purple", col_x[1], row_y[1], r)
        draw_purple_compass(self.canvas, col_x[1], row_y[1], r,
                            self.st_purple, "СЕКТОРЫ")

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _set_center(self, key, cx, cy, r):
        self.centers[key] = (cx, cy, r)

    def _which_sector(self, key, mx, my):
        if key not in self.centers:
            return None
        cx, cy, r = self.centers[key]
        dx = mx - cx
        dy = my - cy
        dist = math.hypot(dx, dy)
        if dist > r or dist < 15:
            return None
        ang = math.degrees(math.atan2(-dy, dx)) % 360
        if 45 <= ang < 135:
            return "up"
        elif ang < 45 or ang >= 315:
            return "right"
        elif 135 <= ang < 225:
            return "down"
        else:
            return "left"

    def _on_click(self, event):
        for key in self.centers.keys():
            sect = self._which_sector(key, event.x, event.y)
            if sect:
                st = self._state(key)
                if st:
                    st.active_sector = sect
                    if key == "compass":
                        angles = {"up": 0, "right": 90,
                                  "down": 180, "left": 270}
                        st.target = angles[sect]
                return

    def _on_motion(self, event):
        for key in self.centers.keys():
            sect = self._which_sector(key, event.x, event.y)
            st = self._state(key)
            if st:
                st.hover_sector = sect

    def _state(self, key):
        return {
            "compass": self.st_compass,
            "dark": self.st_dark,
            "light": self.st_light,
            "dots": self.st_dots,
            "purple": self.st_purple,
        }.get(key)

    def _simulate(self, dt):
        self.t += dt
        if self.st_compass.active_sector is None:
            self.st_compass.target = (self.st_compass.target + 0.3) % 360

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self._simulate(dt)
        for st in self.all_states:
            st.tick()

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()