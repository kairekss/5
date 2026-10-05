"""
ОКФРС. Практика 5. Задание 5.
Круглые шкалы с цифрами — 4 варианта.
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
# ДАННЫЕ ШКАЛЫ
# ============================================================
class DialData:
    def __init__(self, min_v, max_v, value=None, color=NEON_CYAN):
        self.min_v = min_v
        self.max_v = max_v
        self.value = value if value is not None else (min_v + max_v) / 2
        self.target = self.value
        self.color = color

    def tick(self):
        diff = self.target - self.value
        if abs(diff) > 0.001:
            self.value += diff * 0.15
        else:
            self.value = self.target

    def k(self):
        """Доля от 0 до 1."""
        return max(0.0, min(1.0,
            (self.value - self.min_v) / (self.max_v - self.min_v)))


# ============================================================
# 1. КЛАССИЧЕСКАЯ КРУГОВАЯ ШКАЛА (как на скрине)
# ============================================================
def draw_classic_dial(canvas, cx, cy, r, data, label="",
                      digits=9, red_zone_deg=None):
    """
    Круглая шкала с цифрами по кругу, тонкой стрелкой
    и красной рисой в углу.
    """
    # карточка
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    if label:
        canvas.create_text(cx, cy - r - 28, text=label,
                           fill=TEXT_GLOW, font=FONT_LABEL)

    # внешний обод
    canvas.create_oval(cx - r - 3, cy - r + 2, cx + r + 3, cy + r + 8,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0f1520",
                       outline=lerp(data.color, "#000000", 0.5), width=3)
    canvas.create_oval(cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4,
                       fill="#0a0d14",
                       outline=lerp(data.color, BG_DEEP, 0.4), width=1)

    # внутренний круг с точками (как на картинке)
    inner_r = r - 22
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="")

    # точки-декор
    for i in range(72):
        a = math.radians(i * 5)
        px = cx + (inner_r - 6) * math.cos(a)
        py = cy - (inner_r - 6) * math.sin(a)
        canvas.create_oval(px - 1, py - 1, px + 1, py + 1,
                           fill="#1a2030", outline="")

    # деления (полный круг, 360°)
    total_ticks = digits * 10  # например, 9 цифр → 90 делений
    for i in range(total_ticks):
        a = math.radians(90 - i * (360 / total_ticks))
        is_major = (i % 10 == 0)
        is_medium = (i % 5 == 0) and not is_major
        tick_len = 14 if is_major else (8 if is_medium else 4)
        col = TEXT_GLOW if is_major else (TEXT_DIM if is_medium else "#2a3340")
        w = 2 if is_major else 1
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w)

        # цифры у главных делений
        if is_major:
            digit_v = i // 10 * 10
            tx = cx + (inner_r - 32) * math.cos(a)
            ty = cy - (inner_r - 32) * math.sin(a)
            canvas.create_text(tx, ty, text=str(digit_v),
                               fill=TEXT_GLOW,
                               font=("Consolas", 10, "bold"))

    # красная риска (зона)
    if red_zone_deg is not None:
        a_start = math.radians(red_zone_deg[0])
        a_end = math.radians(red_zone_deg[1])
        x1 = cx + (r - 6) * math.cos(a_start)
        y1 = cy - (r - 6) * math.sin(a_start)
        x2 = cx + (r - 6) * math.cos(a_end)
        y2 = cy - (r - 6) * math.sin(a_end)
        canvas.create_line(x1, y1, x2, y2,
                           fill=NEON_RED, width=4)

    # стрелка
    angle_deg = 90 - data.k() * 360
    a = math.radians(angle_deg)
    canvas.create_line(cx + 2, cy + 2,
                       cx + 2 + (inner_r - 22) * math.cos(a),
                       cy + 2 - (inner_r - 22) * math.sin(a),
                       fill="#000000", width=4)
    canvas.create_line(cx, cy,
                       cx + (inner_r - 22) * math.cos(a),
                       cy - (inner_r - 22) * math.sin(a),
                       fill=NEON_RED, width=2, capstyle="round")
    canvas.create_line(cx, cy,
                       cx - 18 * math.cos(a),
                       cy + 18 * math.sin(a),
                       fill=lerp(NEON_RED, "#000000", 0.4),
                       width=2, capstyle="round")

    # втулка
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill="#1a1f2e",
                       outline=lerp(data.color, BG_DEEP, 0.4), width=2)
    canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                       fill=data.color, outline="")

    # значение под шкалой
    canvas.create_text(cx, cy + r + 30,
                       text=f"{data.value:.1f}",
                       fill="#ffffff", font=FONT_BIG)
    canvas.create_text(cx, cy + r + 58,
                       text=f"{data.min_v:.0f} … {data.max_v:.0f}",
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# 2. МНОГОШКАЛЬНЫЙ ПРИБОР
# ============================================================
def draw_multiscale_dial(canvas, cx, cy, r, dials, label=""):
    """
    Несколько концентрических шкал с разными стрелками.
    dials = [(data, color, radius), ...]
    """
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    if label:
        canvas.create_text(cx, cy - r - 28, text=label,
                           fill=TEXT_GLOW, font=FONT_LABEL)

    # внешний обод
    canvas.create_oval(cx - r - 3, cy - r + 2, cx + r + 3, cy + r + 8,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0f1520",
                       outline="#2a3340", width=3)

    # каждая шкала — своё кольцо
    for i, (data, col, rr) in enumerate(dials):
        # кольцо
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill="", outline="#1a2030", width=1)

        # деления
        for j in range(36):
            a = math.radians(90 - j * 10)
            is_major = (j % 3 == 0)
            tick_len = 8 if is_major else 4
            x1 = cx + (rr - 1) * math.cos(a)
            y1 = cy - (rr - 1) * math.sin(a)
            x2 = cx + (rr - 1 - tick_len) * math.cos(a)
            y2 = cy - (rr - 1 - tick_len) * math.sin(a)
            canvas.create_line(x1, y1, x2, y2,
                               fill=col if is_major else "#2a3340",
                               width=2 if is_major else 1)

        # цифры
        for j in range(12):
            a = math.radians(90 - j * 30)
            v = data.min_v + (data.max_v - data.min_v) * (j / 12)
            tx = cx + (rr - 20) * math.cos(a)
            ty = cy - (rr - 20) * math.sin(a)
            canvas.create_text(tx, ty, text=f"{v:.0f}",
                               fill=col,
                               font=("Consolas", 9, "bold"))

        # стрелка
        a = math.radians(90 - data.k() * 360)
        canvas.create_line(cx, cy,
                           cx + (rr - 20) * math.cos(a),
                           cy - (rr - 20) * math.sin(a),
                           fill=col, width=3, capstyle="round")

    # втулка
    canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10,
                       fill="#1a1f2e", outline="#2a3340", width=2)
    canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4,
                       fill=NEON_CYAN, outline="")

    # подписи
    ly = cy + r + 30
    for data, col, rr in dials:
        canvas.create_text(cx, ly,
                           text=f"{data.value:.1f}",
                           fill=col, font=FONT_VAL)
        ly += 22


# ============================================================
# 3. РАДИАЛЬНАЯ С МЕТКАМИ
# ============================================================
def draw_radial_dial(canvas, cx, cy, r, data, label=""):
    """
    Круглая шкала с крупными цифрами снаружи,
    3 уровнями делений и подписью по центру.
    """
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    if label:
        canvas.create_text(cx, cy - r - 28, text=label,
                           fill=TEXT_GLOW, font=FONT_LABEL)

    # обод
    canvas.create_oval(cx - r - 3, cy - r + 2, cx + r + 3, cy + r + 8,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0f1520",
                       outline=lerp(data.color, "#000000", 0.5), width=3)
    inner_r = r - 30
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14",
                       outline=lerp(data.color, BG_DEEP, 0.4), width=1)

    # деления 360°
    for i in range(120):
        a = math.radians(90 - i * 3)
        is_major = (i % 10 == 0)
        is_medium = (i % 5 == 0) and not is_major
        tick_len = 16 if is_major else (10 if is_medium else 4)
        col = data.color if is_major else (TEXT_GLOW if is_medium else "#2a3340")
        w = 3 if is_major else (2 if is_medium else 1)
        x1 = cx + (r - 6) * math.cos(a)
        y1 = cy - (r - 6) * math.sin(a)
        x2 = cx + (r - 6 - tick_len) * math.cos(a)
        y2 = cy - (r - 6 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w)

        # цифры (каждые 30°)
        if is_major:
            v = i / 120 * (data.max_v - data.min_v) + data.min_v
            tx = cx + (r - 40) * math.cos(a)
            ty = cy - (r - 40) * math.sin(a)
            canvas.create_text(tx, ty, text=f"{v:.0f}",
                               fill=data.color,
                               font=("Consolas", 11, "bold"))

    # стрелка
    a = math.radians(90 - data.k() * 360)
    canvas.create_line(cx + 2, cy + 2,
                       cx + 2 + (inner_r - 15) * math.cos(a),
                       cy + 2 - (inner_r - 15) * math.sin(a),
                       fill="#000000", width=6)
    canvas.create_line(cx, cy,
                       cx + (inner_r - 15) * math.cos(a),
                       cy - (inner_r - 15) * math.sin(a),
                       fill=data.color, width=3, capstyle="round")

    # центральный круг с цифрой
    canvas.create_oval(cx - 45, cy - 45, cx + 45, cy + 45,
                       fill="#0f1520",
                       outline=lerp(data.color, BG_DEEP, 0.5), width=2)
    canvas.create_text(cx, cy - 8,
                       text=f"{data.value:.1f}",
                       fill="#ffffff", font=FONT_BIG)
    canvas.create_text(cx, cy + 20,
                       text=f"{data.min_v:.0f}..{data.max_v:.0f}",
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# 4. КОМПАС-РОЗА
# ============================================================
def draw_compass(canvas, cx, cy, r, data, label="КОМПАС"):
    """
    Компас с N/S/E/W и шкалой 0..360°.
    """
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 28, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # обод
    canvas.create_oval(cx - r - 3, cy - r + 2, cx + r + 3, cy + r + 8,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0f1520",
                       outline=lerp(NEON_AMBER, "#000000", 0.5), width=3)

    # внутренние кольца
    inner_r = r - 20
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="")
    for rr in [r - 40, r - 60]:
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill="", outline="#1a2030", width=1)

    # деления 360°
    for i in range(72):
        a = math.radians(90 - i * 5)
        is_major = (i % 9 == 0)  # каждые 45°
        is_medium = (i % 3 == 0)
        tick_len = 14 if is_major else (8 if is_medium else 4)
        col = TEXT_GLOW if is_major else ("#4a5360" if is_medium else "#2a3340")
        w = 2 if is_major else 1
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w)

    # цифры 0..360 с шагом 30
    for i in range(12):
        a = math.radians(90 - i * 30)
        v = i * 30
        tx = cx + (inner_r - 24) * math.cos(a)
        ty = cy - (inner_r - 24) * math.sin(a)
        canvas.create_text(tx, ty, text=str(v),
                           fill=TEXT_GLOW,
                           font=("Consolas", 9, "bold"))

    # N/S/E/W
    dirs = [("N", 90, NEON_RED), ("E", 0, NEON_GREEN),
            ("S", 270, TEXT_GLOW), ("W", 180, TEXT_GLOW)]
    for letter, angle_deg, col in dirs:
        a = math.radians(angle_deg)
        tx = cx + (inner_r - 45) * math.cos(a)
        ty = cy - (inner_r - 45) * math.sin(a)
        canvas.create_text(tx, ty, text=letter,
                           fill=col,
                           font=("Segoe UI", 18, "bold"))

    # стрелка-компас (двухцветная: N — красная, S — белая)
    a = math.radians(90 - data.k() * 360)
    # север (красная половина)
    canvas.create_polygon(cx, cy,
                          cx + 14 * math.cos(a + math.pi/2),
                          cy - 14 * math.sin(a + math.pi/2),
                          cx + (inner_r - 20) * math.cos(a),
                          cy - (inner_r - 20) * math.sin(a),
                          cx + 14 * math.cos(a - math.pi/2),
                          cy - 14 * math.sin(a - math.pi/2),
                          fill=NEON_RED, outline="#000000")
    # юг (белая половина)
    a2 = a + math.pi
    canvas.create_polygon(cx, cy,
                          cx + 14 * math.cos(a2 + math.pi/2),
                          cy - 14 * math.sin(a2 + math.pi/2),
                          cx + (inner_r - 20) * math.cos(a2),
                          cy - (inner_r - 20) * math.sin(a2),
                          cx + 14 * math.cos(a2 - math.pi/2),
                          cy - 14 * math.sin(a2 - math.pi/2),
                          fill="#ffffff", outline="#000000")

    # центр
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill="#1a1f2e",
                       outline=NEON_AMBER, width=2)

    # значение
    canvas.create_text(cx, cy + r + 30,
                       text=f"{data.value:.0f}°",
                       fill=NEON_AMBER, font=FONT_BIG)
    canvas.create_text(cx, cy + r + 58,
                       text="АЗИМУТ",
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("🎯 Circular Dials · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # 4 шкалы
        self.d_classic = DialData(0, 90, 45, NEON_CYAN)
        self.d_multi1 = DialData(0, 100, 50, NEON_GREEN)
        self.d_multi2 = DialData(0, 300, 150, NEON_PINK)
        self.d_multi3 = DialData(0, 60, 30, NEON_PURP)
        self.d_radial = DialData(0, 100, 50, NEON_AMBER)
        self.d_compass = DialData(0, 360, 45, NEON_AMBER)

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

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
        self.canvas.create_text(60, 40, text="🎯",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="CIRCULAR DIALS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(340, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # Верхний ряд: 3 шкалы
        top_cy = 250
        r_top = min(140, w * 0.08)

        # 1. Классическая — слева
        draw_classic_dial(self.canvas, w * 0.18, top_cy, r_top,
                          self.d_classic, "КЛАССИЧЕСКАЯ",
                          digits=9,
                          red_zone_deg=(20, 60))

        # 2. Многошкальная — центр
        draw_multiscale_dial(self.canvas, w * 0.50, top_cy, r_top,
                             [(self.d_multi1, NEON_GREEN, r_top - 6),
                              (self.d_multi2, NEON_PINK, r_top - 30),
                              (self.d_multi3, NEON_PURP, r_top - 54)],
                             "МНОГОШКАЛЬНАЯ")

        # 3. Радиальная — справа
        draw_radial_dial(self.canvas, w * 0.82, top_cy, r_top,
                         self.d_radial, "РАДИАЛЬНАЯ")

        # Нижний ряд: компас по центру
        bottom_cy = h - 250
        r_bottom = min(150, w * 0.10)
        draw_compass(self.canvas, w * 0.5, bottom_cy, r_bottom,
                     self.d_compass, "КОМПАС")

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    # ---------- СИМУЛЯЦИЯ ----------
    def _simulate(self, dt):
        self.t += dt
        t = self.t
        self.d_classic.target = 45 + 35 * math.sin(t * 0.4) + random.uniform(-2, 2)
        self.d_multi1.target = 50 + 30 * math.sin(t * 0.5) + random.uniform(-1, 1)
        self.d_multi2.target = 150 + 100 * math.sin(t * 0.3 + 1) + random.uniform(-3, 3)
        self.d_multi3.target = 30 + 20 * math.sin(t * 0.7 + 2) + random.uniform(-1, 1)
        self.d_radial.target = 50 + 40 * math.sin(t * 0.45) + random.uniform(-2, 2)
        self.d_compass.target = (180 + 170 * math.sin(t * 0.2)) % 360

    # ---------- АНИМАЦИЯ ----------
    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self._simulate(dt)
        for d in (self.d_classic, self.d_multi1, self.d_multi2,
                  self.d_multi3, self.d_radial, self.d_compass):
            d.tick()

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()