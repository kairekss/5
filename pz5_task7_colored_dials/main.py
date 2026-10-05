"""
ОКФРС. Практика 5. Задание 7.
Круглые приборы разных цветов и стилей — 4 варианта.
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
NEON_ORANGE = "#ff8c42"

TEXT_MAIN  = "#e8f0ff"
TEXT_DIM   = "#5a6780"
TEXT_GLOW  = "#8fa4c4"

FONT_MONO  = ("Consolas", 13, "bold")
FONT_MONO_S= ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_LABEL_S = ("Segoe UI", 9)
FONT_VAL   = ("Consolas", 16, "bold")
FONT_BIG   = ("Consolas", 26, "bold")
FONT_HUGE  = ("Consolas", 42, "bold")


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
# ДАННЫЕ
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
        return max(0.0, min(1.0,
            (self.value - self.min_v) / (self.max_v - self.min_v)))


# ============================================================
# ПРИБОР 1 — СВЕТЛЫЙ НЕОНОВЫЙ
# ============================================================
def draw_light_dial(canvas, cx, cy, r, data, label="ПРОЦЕНТ"):
    """Светлый прибор с цветной дугой и % в центре."""
    # карточка вокруг
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 70, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 28, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # тень под прибором
    canvas.create_oval(cx - r - 2, cy - r + 4, cx + r + 2, cy + r + 8,
                       fill="#000000", outline="")

    # светлый корпус
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#f5f7ff",
                       outline="#d0d5e5", width=3)
    canvas.create_oval(cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
                       fill="#ffffff", outline="#e8ebf5", width=1)

    inner_r = r - 22

    # трек дуги
    canvas.create_arc(cx - inner_r, cy - inner_r,
                      cx + inner_r, cy + inner_r,
                      start=90, extent=-360,
                      style="arc", outline="#e0e4f0", width=10)

    # цветная дуга заполнения
    k = data.k()
    extent = -360 * k
    if k > 0.005:
        canvas.create_arc(cx - inner_r, cy - inner_r,
                          cx + inner_r, cy + inner_r,
                          start=90, extent=extent,
                          style="arc", outline=data.color, width=10)

    # деления 36
    for i in range(36):
        a = math.radians(90 - i * 10)
        is_major = (i % 9 == 0)
        tick_len = 8 if is_major else 4
        col = "#8894b0" if is_major else "#c8cfe0"
        x1 = cx + (inner_r - 12) * math.cos(a)
        y1 = cy - (inner_r - 12) * math.sin(a)
        x2 = cx + (inner_r - 12 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 12 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col,
                           width=2 if is_major else 1)

    # значение в центре
    canvas.create_text(cx, cy - 10,
                       text=f"{data.value:.0f}",
                       fill=data.color, font=FONT_HUGE)
    canvas.create_text(cx, cy + 28,
                       text="%",
                       fill="#8894b0", font=("Consolas", 16, "bold"))

    # подпись-иероглиф
    canvas.create_text(cx, cy + 55,
                       text="数据统计",
                       fill="#a0a8c0",
                       font=("Microsoft YaHei", 11))


# ============================================================
# ПРИБОР 2 — ТЁМНЫЙ ЗЕЛЁНЫЙ
# ============================================================
def draw_dark_green_dial(canvas, cx, cy, r, data, label="УРОВЕНЬ"):
    """Тёмный прибор с зелёно-жёлто-красной шкалой и цифрой в центре."""
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 70, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 28, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # тень
    canvas.create_oval(cx - r - 3, cy - r + 4, cx + r + 3, cy + r + 8,
                       fill="#000000", outline="")

    # тёмный корпус
    for i in range(8):
        k = i / 8
        rr = r - k * 5
        col = lerp("#2a3040", "#05070c", k)
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill=col, outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline="#3a4250", width=3)

    inner_r = r - 26
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="#1a1f2e", width=1)

    # цветные зоны на дуге
    a_start = 90
    # зелёная 0..60%, жёлтая 60..80%, красная 80..100%
    zones = [
        (0.0, 0.6, NEON_GREEN),
        (0.6, 0.8, NEON_AMBER),
        (0.8, 1.0, NEON_RED),
    ]
    for (k0, k1, col) in zones:
        s = a_start - 360 * k0
        e = -360 * (k1 - k0)
        canvas.create_arc(cx - inner_r, cy - inner_r,
                          cx + inner_r, cy + inner_r,
                          start=s, extent=e,
                          style="arc", outline=col, width=8)

    # деления
    for i in range(36):
        a = math.radians(90 - i * 10)
        is_major = (i % 9 == 0)
        tick_len = 10 if is_major else 5
        col = TEXT_GLOW if is_major else "#4a5360"
        x1 = cx + (inner_r - 6) * math.cos(a)
        y1 = cy - (inner_r - 6) * math.sin(a)
        x2 = cx + (inner_r - 6 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 6 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col,
                           width=2 if is_major else 1)

    # стрелка
    a = math.radians(90 - data.k() * 360)
    canvas.create_line(cx + 2, cy + 2,
                       cx + 2 + (inner_r - 25) * math.cos(a),
                       cy + 2 - (inner_r - 25) * math.sin(a),
                       fill="#000000", width=5)
    canvas.create_line(cx, cy,
                       cx + (inner_r - 25) * math.cos(a),
                       cy - (inner_r - 25) * math.sin(a),
                       fill=NEON_GREEN, width=3, capstyle="round")

    # центр
    canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10,
                       fill="#1a1f2e", outline="#3a4250", width=2)

    # большая цифра
    canvas.create_text(cx, cy + 5,
                       text=f"{data.value:.0f}",
                       fill="#ffffff", font=FONT_HUGE)

    # маленькая подпись
    canvas.create_text(cx, cy + 42,
                       text="GOOD",
                       fill=NEON_GREEN,
                       font=("Consolas", 11, "bold"))


# ============================================================
# ПРИБОР 3 — СИНИЙ МИНИМАЛ
# ============================================================
def draw_blue_minimal(canvas, cx, cy, r, data, label="ЗНАЧЕНИЕ"):
    """Тёмный прибор с точкой на дуге и полоской-индикатором снизу."""
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 70, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 28, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # чёрный корпус
    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0a0d14",
                       outline="#1a2030", width=3)

    # тонкое кольцо
    ring_r = r - 15
    canvas.create_oval(cx - ring_r, cy - ring_r,
                       cx + ring_r, cy + ring_r,
                       fill="", outline="#252d40", width=1)

    # деления 72
    for i in range(72):
        a = math.radians(90 - i * 5)
        is_major = (i % 9 == 0)
        tick_len = 6 if is_major else 3
        col = "#3a4560" if is_major else "#1a2030"
        x1 = cx + (r - 8) * math.cos(a)
        y1 = cy - (r - 8) * math.sin(a)
        x2 = cx + (r - 8 - tick_len) * math.cos(a)
        y2 = cy - (r - 8 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=1)

    # маленькая яркая точка на текущем значении
    a = math.radians(90 - data.k() * 360)
    px = cx + ring_r * math.cos(a)
    py = cy - ring_r * math.sin(a)

    # свечение точки
    for k in range(5, 0, -1):
        col = lerp(NEON_CYAN, BG_DEEP, k / 6)
        canvas.create_oval(px - 8 - k, py - 8 - k,
                           px + 8 + k, py + 8 + k,
                           fill="", outline=col, width=1)
    # сама точка
    canvas.create_oval(px - 8, py - 8, px + 8, py + 8,
                       fill=NEON_CYAN, outline="#ffffff", width=2)
    # белая сердцевина
    canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                       fill="#ffffff", outline="")

    # большая цифра в центре
    canvas.create_text(cx, cy - 8,
                       text=f"{data.value:.1f}",
                       fill="#ffffff", font=FONT_HUGE)
    canvas.create_text(cx, cy + 30,
                       text="mA",
                       fill="#8894b0", font=("Consolas", 14, "bold"))

    # полоска-индикатор снизу
    bar_y = cy + r - 32
    bar_x0 = cx - r + 30
    bar_x1 = cx + r - 30
    round_rect(canvas, bar_x0, bar_y, bar_x1, bar_y + 8, 4,
               fill="#1a2030", outline="")
    fill_w = (bar_x1 - bar_x0) * data.k()
    if fill_w > 3:
        round_rect(canvas, bar_x0, bar_y, bar_x0 + fill_w, bar_y + 8, 4,
                   fill=NEON_BLUE, outline="")


# ============================================================
# ПРИБОР 4 — ВАННА С УРОВНЕМ
# ============================================================
def draw_tank_dial(canvas, cx, cy, r, data, label="БАК"):
    """Верхняя шкала + 'ванна' с цветной жидкостью."""
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 70, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 28, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # ВЕРХНЯЯ ШКАЛА (полукруг)
    top_r = r - 30
    top_cy = cy - r / 3

    # серый трек
    canvas.create_arc(cx - top_r, top_cy - top_r,
                      cx + top_r, top_cy + top_r,
                      start=180, extent=-180,
                      style="arc", outline="#2a3040", width=14)

    # цветная шкала (сегменты)
    for i in range(20):
        k0 = i / 20
        k1 = (i + 1) / 20
        if k0 < 0.5:
            col = lerp(NEON_GREEN, NEON_AMBER, k0 / 0.5)
        elif k0 < 0.75:
            col = lerp(NEON_AMBER, NEON_ORANGE, (k0 - 0.5) / 0.25)
        else:
            col = lerp(NEON_ORANGE, NEON_RED, (k0 - 0.75) / 0.25)
        s = 180 - k0 * 180
        e = -180 * (k1 - k0)
        canvas.create_arc(cx - top_r, top_cy - top_r,
                          cx + top_r, top_cy + top_r,
                          start=s, extent=e,
                          style="arc", outline=col, width=14)

    # деления сверху
    for i in range(11):
        a = math.radians(180 - i * 18)
        is_major = (i % 5 == 0)
        tick_len = 8 if is_major else 4
        x1 = cx + (top_r + 8) * math.cos(a)
        y1 = top_cy - (top_r + 8) * math.sin(a)
        x2 = cx + (top_r + 8 + tick_len) * math.cos(a)
        y2 = top_cy - (top_r + 8 + tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2,
                           fill=TEXT_GLOW if is_major else TEXT_DIM,
                           width=2 if is_major else 1)
        if is_major:
            v = data.min_v + (data.max_v - data.min_v) * i / 10
            tx = cx + (top_r + 22) * math.cos(a)
            ty = top_cy - (top_r + 22) * math.sin(a)
            canvas.create_text(tx, ty, text=f"{v:.0f}",
                               fill=TEXT_GLOW,
                               font=("Consolas", 8, "bold"))

    # стрелка на верхней шкале
    a = math.radians(180 - data.k() * 180)
    canvas.create_line(cx, top_cy,
                       cx + (top_r - 12) * math.cos(a),
                       top_cy - (top_r - 12) * math.sin(a),
                       fill=NEON_RED, width=3, capstyle="round")
    canvas.create_oval(cx - 6, top_cy - 6, cx + 6, top_cy + 6,
                       fill="#1a1f2e", outline=NEON_RED, width=2)

    # ВАННА (прямоугольник с жидкостью)
    tank_w = r * 1.4
    tank_h = r * 0.55
    tank_x0 = cx - tank_w / 2
    tank_y0 = cy + r * 0.1
    tank_x1 = cx + tank_w / 2
    tank_y1 = tank_y0 + tank_h

    # тень под ванной
    round_rect(canvas, tank_x0 + 2, tank_y1 - 4,
               tank_x1 + 2, tank_y1 + 8, 8, fill="#000000", outline="")

    # корпус ванны (белый/светлый)
    round_rect(canvas, tank_x0, tank_y0, tank_x1, tank_y1, 10,
               fill="#e8ecf5", outline="#c8cfe0", width=2)

    # внутренняя тёмная часть
    inner_x0 = tank_x0 + 6
    inner_y0 = tank_y0 + 6
    inner_x1 = tank_x1 - 6
    inner_y1 = tank_y1 - 6

    # тёмный фон внутри
    round_rect(canvas, inner_x0, inner_y0, inner_x1, inner_y1, 6,
               fill="#0a0d14", outline="")

    # ЖИДКОСТЬ заполнение (снизу вверх)
    k = data.k()
    fill_h = (inner_y1 - inner_y0) * k
    if fill_h > 2:
        liq_y0 = inner_y1 - fill_h
        # цвет жидкости по уровню
        if k < 0.4:
            col = NEON_BLUE
        elif k < 0.7:
            col = NEON_CYAN
        elif k < 0.9:
            col = NEON_GREEN
        else:
            col = NEON_AMBER

        # тело жидкости
        round_rect(canvas, inner_x0 + 1, liq_y0,
                   inner_x1 - 1, inner_y1 - 1, 5,
                   fill=col, outline="")
        # блеск сверху жидкости
        round_rect(canvas, inner_x0 + 3, liq_y0 + 1,
                   inner_x1 - 3, liq_y0 + 4, 2,
                   fill=lerp(col, "#ffffff", 0.4), outline="")
        # волны (две маленькие дуги)
        wave_y = liq_y0
        for i in range(3):
            wx = inner_x0 + 10 + i * (inner_x1 - inner_x0) / 4
            canvas.create_arc(wx - 8, wave_y - 3, wx + 8, wave_y + 3,
                              start=0, extent=180,
                              style="arc", fill="", outline=col, width=2)

    # отметки уровня на ванне
    for i in range(1, 5):
        my = inner_y0 + (inner_y1 - inner_y0) * i / 5
        canvas.create_line(inner_x1 + 2, my,
                           inner_x1 + 8, my,
                           fill=TEXT_DIM, width=1)

    # значение
    canvas.create_text(cx, tank_y1 + 30,
                       text=f"{data.value:.1f} %",
                       fill="#ffffff", font=FONT_VAL)
    canvas.create_text(cx, tank_y1 + 52,
                       text=f"мин {data.min_v:.0f} / макс {data.max_v:.0f}",
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("🎨 Colored Dials · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # 4 прибора
        self.d_light = DialData(0, 100, 88, NEON_PURP)
        self.d_dark = DialData(0, 100, 65, NEON_GREEN)
        self.d_blue = DialData(0, 100, 42.5, NEON_CYAN)
        self.d_tank = DialData(0, 100, 65, NEON_BLUE)

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
        self.canvas.create_text(60, 40, text="🎨",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="COLORED DIALS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(330, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # 4 прибора в ряд (2x2)
        r = min(140, w * 0.075)
        col_x = [w * 0.17, w * 0.50, w * 0.83]
        row_y = [h * 0.30, h * 0.72]

        # 1. Светлый
        draw_light_dial(self.canvas, col_x[0], row_y[0], r,
                        self.d_light, "ПРОЦЕНТ")

        # 2. Тёмный зелёный
        draw_dark_green_dial(self.canvas, col_x[1], row_y[0], r,
                             self.d_dark, "УРОВЕНЬ")

        # 3. Синий минимал
        draw_blue_minimal(self.canvas, col_x[2], row_y[0], r,
                          self.d_blue, "ЗНАЧЕНИЕ")

        # 4. Ванна — по центру нижнего ряда
        draw_tank_dial(self.canvas, col_x[1], row_y[1], r,
                       self.d_tank, "БАК")

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _simulate(self, dt):
        self.t += dt
        t = self.t
        self.d_light.target = 65 + 30 * math.sin(t * 0.4) + random.uniform(-2, 2)
        self.d_dark.target = 55 + 35 * math.sin(t * 0.5 + 1) + random.uniform(-2, 2)
        self.d_blue.target = 45 + 40 * math.sin(t * 0.6 + 2) + random.uniform(-1, 1)
        self.d_tank.target = 50 + 45 * math.sin(t * 0.35 + 0.5) + random.uniform(-2, 2)

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self._simulate(dt)
        for d in (self.d_light, self.d_dark, self.d_blue, self.d_tank):
            d.tick()

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()