"""
ОКФРС. Практика 5. Задание 4.
Индикатор GOOD/BAD + спидометр.
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
FONT_HUGE  = ("Consolas", 40, "bold")


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
class IndicatorData:
    def __init__(self, min_v=0, max_v=100, value=None):
        self.min_v = min_v
        self.max_v = max_v
        self.value = value if value is not None else (min_v + max_v) / 2
        self.target = self.value
        self.warn_lo = 30
        self.warn_hi = 70
        self.crit_lo = 15
        self.crit_hi = 85

    def status(self):
        v = self.value
        if v < self.crit_lo or v > self.crit_hi: return "CRIT"
        if v < self.warn_lo or v > self.warn_hi: return "WARN"
        return "OK"

    def status_color(self):
        return {"OK": NEON_GREEN, "WARN": NEON_AMBER,
                "CRIT": NEON_RED}[self.status()]

    def status_text(self):
        return {"OK": "ХОРОШО", "WARN": "ВНИМАНИЕ",
                "CRIT": "ПЛОХО"}[self.status()]

    def tick(self):
        diff = self.target - self.value
        if abs(diff) > 0.001:
            self.value += diff * 0.15
        else:
            self.value = self.target


# ============================================================
# 1. ПОЛОСАТЫЙ ИНДИКАТОР GOOD/BAD
# ============================================================
def draw_goodbad_bar(canvas, x, y, w, h, data, label="КАЧЕСТВО"):
    """
    Горизонтальная полоса с зонами:
    [BAD] [OK] [GOOD] [OK] [BAD]
    стрелка сверху показывает текущее значение.
    """
    # карточка
    round_rect(canvas, x - 20, y - 55, x + w + 20, y + h + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    # заголовок
    canvas.create_text(x + w / 2, y - 35, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # подписи GOOD / BAD
    canvas.create_text(x + 10, y - 10, anchor="w",
                       text="BAD", fill=NEON_RED, font=FONT_LABEL_S)
    canvas.create_text(x + w / 2, y - 10,
                       text="GOOD", fill=NEON_GREEN, font=FONT_LABEL_S)
    canvas.create_text(x + w - 10, y - 10, anchor="e",
                       text="BAD", fill=NEON_RED, font=FONT_LABEL_S)

    # зоны (5 сегментов)
    zones = [
        (0.00, 0.15, NEON_RED),
        (0.15, 0.35, NEON_AMBER),
        (0.35, 0.65, NEON_GREEN),
        (0.65, 0.85, NEON_AMBER),
        (0.85, 1.00, NEON_RED),
    ]
    # фон полосы
    round_rect(canvas, x, y, x + w, y + h, 6,
               fill="#0a0d14", outline=BORDER, width=1)

    for (k0, k1, col) in zones:
        x0 = x + 2 + k0 * (w - 4)
        x1 = x + 2 + k1 * (w - 4)
        round_rect(canvas, x0, y + 4, x1, y + h - 4, 4,
                   fill=col)

    # деления
    for i in range(11):
        k = i / 10
        xx = x + 2 + k * (w - 4)
        is_major = (i % 2 == 0)
        canvas.create_line(xx, y + h + 2, xx,
                           y + h + (8 if is_major else 4),
                           fill=TEXT_GLOW if is_major else TEXT_DIM,
                           width=2 if is_major else 1)
        if is_major:
            v = data.min_v + (data.max_v - data.min_v) * k
            canvas.create_text(xx, y + h + 22, text=f"{v:.0f}",
                               fill=TEXT_GLOW, font=FONT_MONO_S)

    # стрелка-маркер
    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    mx = x + 2 + k * (w - 4)
    col = data.status_color()

    # треугольник сверху
    canvas.create_polygon(mx - 10, y - 6,
                          mx + 10, y - 6,
                          mx, y + 6,
                          fill=col, outline="#ffffff", width=2)
    # вертикальная линия через полосу
    canvas.create_line(mx, y + 2, mx, y + h - 2,
                       fill="#ffffff", width=2)
    # свечение
    canvas.create_oval(mx - 5, y + h / 2 - 5,
                       mx + 5, y + h / 2 + 5,
                       fill="#ffffff", outline="")

    # значение
    canvas.create_text(x + w / 2, y + h + 55,
                       text=f"{data.value:.1f} %",
                       fill=col, font=FONT_BIG)
    canvas.create_text(x + w / 2, y + h + 78,
                       text="● " + data.status_text(),
                       fill=col, font=FONT_LABEL)


# ============================================================
# 2. ДУГОВОЙ ИНДИКАТОР GOOD/BAD
# ============================================================
def draw_goodbad_arc(canvas, cx, cy, r, data, label="СТАТУС"):
    """
    Полукруг с цветными зонами GOOD / OK / BAD и белым маркером.
    """
    # карточка
    round_rect(canvas, cx - r - 40, cy - r - 50,
               cx + r + 40, cy + r + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    # заголовок
    canvas.create_text(cx, cy - r - 28, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # зоны (от 180° до 0°)
    zones = [
        (0.00, 0.35, NEON_RED),
        (0.35, 0.65, NEON_AMBER),
        (0.65, 1.00, NEON_GREEN),
    ]
    for (k0, k1, col) in zones:
        s = 180 + 180 * k0
        e = 180 * (k1 - k0)
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                          start=s, extent=-e,
                          style="arc", outline=col, width=18)

    # внутренняя тёмная подложка
    inner_r = r - 28
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14",
                       outline=lerp(NEON_CYAN, BG_DEEP, 0.7), width=2)

    # подписи BAD / GOOD
    canvas.create_text(cx - r + 25, cy - r + 35, text="BAD",
                       fill=NEON_RED, font=FONT_LABEL_S)
    canvas.create_text(cx + r - 25, cy - r + 35, text="GOOD",
                       fill=NEON_GREEN, font=FONT_LABEL_S)

    # деления
    for i in range(11):
        k = i / 10
        a = math.radians(180 + 180 * k)
        x1 = cx + (r - 34) * math.cos(a)
        y1 = cy - (r - 34) * math.sin(a)
        x2 = cx + (r - 22) * math.cos(a)
        y2 = cy - (r - 22) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=TEXT_DIM, width=1)

    # белый маркер
    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    a = math.radians(180 + 180 * k)
    mx = cx + (r - 25) * math.cos(a)
    my = cy - (r - 25) * math.sin(a)

    # тень под маркером
    canvas.create_oval(mx - 12, my - 6, mx + 14, my + 16,
                       fill="#000000", outline="")
    # сам маркер (белая «капля»)
    canvas.create_oval(mx - 12, my - 12, mx + 12, my + 12,
                       fill="#ffffff", outline=lerp("#ffffff", BG_DEEP, 0.3),
                       width=2)
    # указатель к центру
    inner_x = cx + (r - 60) * math.cos(a)
    inner_y = cy - (r - 60) * math.sin(a)
    canvas.create_line(mx, my, inner_x, inner_y,
                       fill="#ffffff", width=3)

    # центральная точка
    canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10,
                       fill="#1a1f2e",
                       outline=lerp(NEON_CYAN, BG_DEEP, 0.4), width=2)
    canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                       fill=NEON_CYAN, outline="")

    # значение
    col = data.status_color()
    canvas.create_text(cx, cy + 35,
                       text=f"{data.value:.1f}",
                       fill=col, font=FONT_HUGE)
    canvas.create_text(cx, cy + 70,
                       text="%",
                       fill=TEXT_DIM, font=("Consolas", 14, "bold"))
    canvas.create_text(cx, cy + r + 30,
                       text="● " + data.status_text(),
                       fill=col, font=FONT_LABEL)


# ============================================================
# 3. СПИДОМЕТР
# ============================================================
class Speedometer:
    def __init__(self, cx, cy, r):
        self.cx = cx
        self.cy = cy
        self.r = r
        self.value = 0
        self.target = 0
        self.min_v = 0
        self.max_v = 240
        self.a_start = math.radians(225)
        self.a_end = math.radians(-45)
        self.history = []

    def _angle(self, v):
        k = (v - self.min_v) / (self.max_v - self.min_v)
        k = max(0.0, min(1.0, k))
        return self.a_start + (self.a_end - self.a_start) * k

    def tick(self, dt):
        diff = self.target - self.value
        if abs(diff) > 0.001:
            self.value += diff * 0.12
        else:
            self.value = self.target
        self.history.append(self.value)
        if len(self.history) > 100:
            self.history.pop(0)


def draw_speedometer(canvas, sp):
    cx, cy, r = sp.cx, sp.cy, sp.r

    # карточка
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    # заголовок
    canvas.create_text(cx, cy - r - 28, text="СПИДОМЕТР",
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # внешний обод
    canvas.create_oval(cx - r - 4, cy - r + 2, cx + r + 4, cy + r + 10,
                       fill="#000000", outline="")
    for i in range(10):
        k = i / 10
        rr = r - k * 6
        col = lerp("#2a3040", "#05070c", k)
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill=col, outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=lerp(NEON_PURP, "#000000", 0.6),
                       width=3)
    canvas.create_oval(cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5,
                       fill="", outline=lerp(NEON_PURP, BG_DEEP, 0.5),
                       width=1)

    inner_r = r - 18
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14",
                       outline=lerp(NEON_PURP, BG_DEEP, 0.4), width=1)

    # красная зона >180
    a_red_start = math.degrees(sp._angle(180))
    a_red_end = math.degrees(sp._angle(240))
    canvas.create_arc(cx - inner_r + 3, cy - inner_r + 3,
                      cx + inner_r - 3, cy + inner_r - 3,
                      start=a_red_end, extent=a_red_start - a_red_end,
                      style="arc", outline=NEON_RED, width=6)

    # деления
    for i in range(13):
        v = 0 + i * 20
        a = sp._angle(v)
        is_major = (i % 2 == 0)
        tick_len = 12 if is_major else 6
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        col = TEXT_GLOW if is_major else TEXT_DIM
        canvas.create_line(x1, y1, x2, y2, fill=col,
                           width=2 if is_major else 1)
        if is_major:
            tx = cx + (inner_r - 28) * math.cos(a)
            ty = cy - (inner_r - 28) * math.sin(a)
            canvas.create_text(tx, ty, text=str(v),
                               fill=TEXT_GLOW,
                               font=("Consolas", 10, "bold"))

    # стрелка
    a = sp._angle(sp.value)
    canvas.create_line(cx + 2, cy + 2,
                       cx + 2 + (inner_r - 20) * math.cos(a),
                       cy + 2 - (inner_r - 20) * math.sin(a),
                       fill="#000000", width=7)
    canvas.create_line(cx, cy,
                       cx + (inner_r - 20) * math.cos(a),
                       cy - (inner_r - 20) * math.sin(a),
                       fill=NEON_RED, width=4, capstyle="round")
    canvas.create_line(cx, cy,
                       cx - 25 * math.cos(a),
                       cy + 25 * math.sin(a),
                       fill=lerp(NEON_RED, "#000000", 0.4),
                       width=4, capstyle="round")

    # втулка
    canvas.create_oval(cx - 14, cy - 14, cx + 14, cy + 14,
                       fill="#1a1f2e",
                       outline=lerp(NEON_PURP, BG_DEEP, 0.4), width=3)
    canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6,
                       fill=NEON_PURP, outline="")

    # значение
    canvas.create_text(cx, cy + r - 55,
                       text=f"{sp.value:.0f}",
                       fill="#ffffff", font=FONT_HUGE)
    canvas.create_text(cx, cy + r - 20,
                       text="км/ч",
                       fill=TEXT_DIM, font=FONT_LABEL)

    # статус
    if sp.value > 200:
        col, txt = NEON_RED, "КРИТИЧНО"
    elif sp.value > 160:
        col, txt = NEON_AMBER, "ВЫСОКАЯ"
    else:
        col, txt = NEON_GREEN, "НОРМА"
    canvas.create_text(cx, cy + r + 40,
                       text="● " + txt, fill=col, font=FONT_LABEL)


# ============================================================
# 4. КОЛЬЦЕВОЙ ПРОГРЕСС
# ============================================================
def draw_ring_progress(canvas, cx, cy, r, data, label="ЗАПОЛНЕНИЕ"):
    """Круговой прогресс-бар с % в центре."""
    # карточка
    round_rect(canvas, cx - r - 30, cy - r - 50,
               cx + r + 30, cy + r + 90, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 28, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # фон трека
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline="#1a1f2e", width=16)

    # заполнение — от 90° (сверху) по часовой
    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    extent = -360 * k
    col = data.status_color()

    if k > 0.005:
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                          start=90, extent=extent,
                          style="arc", outline=col, width=16)

    # внутренняя подложка
    inner_r = r - 20
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="")

    # значение в центре
    canvas.create_text(cx, cy - 6,
                       text=f"{data.value:.0f}",
                       fill=col, font=("Consolas", 36, "bold"))
    canvas.create_text(cx, cy + 26,
                       text="%", fill=TEXT_DIM,
                       font=("Consolas", 14, "bold"))

    # статус
    canvas.create_text(cx, cy + r + 30,
                       text="● " + data.status_text(),
                       fill=col, font=FONT_LABEL)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("📊 Indicators & Speedometer · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # данные
        self.quality = IndicatorData(0, 100, 65)   # качество
        self.speed = Speedometer(0, 0, 130)
        self.speed.value = self.speed.target = 80.0

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # для перетаскивания
        self.drag_target = None
        self.drag_start_y = 0
        self.drag_start_v = 0
        # bbox для кликов (заполняется при отрисовке)
        self.hit_zones = {}

        self.root.update_idletasks()
        self._redraw_all()
        self._animate()

    def _on_resize(self, event):
        self._redraw_all()

    # ---------- ПЕРЕРИСОВКА ----------
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
        self.canvas.create_text(60, 40, text="📊",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="INDICATORS & SPEEDOMETER",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(500, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # === РАСПОЛОЖЕНИЕ ===
        # Верхний ряд:
        #   слева — полосатый GOOD/BAD
        #   центр — кольцевой прогресс
        #   справа — дуговой GOOD/BAD
        top_y = 200

        # 1. Полосатый GOOD/BAD — слева (широкий)
        bar_x = 60
        bar_w = w * 0.35
        bar_y = top_y + 60
        bar_h = 40
        draw_goodbad_bar(self.canvas, bar_x, bar_y, bar_w, bar_h,
                         self.quality, "КАЧЕСТВО СИСТЕМЫ")
        self.hit_zones["bar"] = (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h)

        # 2. Кольцевой прогресс — центр
        ring_cx = w * 0.52
        ring_cy = top_y + 110
        draw_ring_progress(self.canvas, ring_cx, ring_cy, 110,
                           self.quality, "ЗАГРУЗКА")
        self.hit_zones["ring"] = (ring_cx - 110, ring_cy - 110,
                                  ring_cx + 110, ring_cy + 110)

        # 3. Дуговой GOOD/BAD — справа
        arc_cx = w * 0.82
        arc_cy = top_y + 130
        draw_goodbad_arc(self.canvas, arc_cx, arc_cy, 130,
                         self.quality, "СТАТУС")
        self.hit_zones["arc"] = (arc_cx - 130, arc_cy - 130,
                                 arc_cx + 130, arc_cy + 130)

        # Нижний ряд — спидометр по центру
        sp_cx = w / 2
        sp_cy = h - 260
        self.speed.cx = sp_cx
        self.speed.cy = sp_cy
        self.speed.r = 150
        draw_speedometer(self.canvas, self.speed)
        self.hit_zones["speed"] = (sp_cx - 150, sp_cy - 150,
                                    sp_cx + 150, sp_cy + 150)

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

        # подсказка
        self.canvas.create_text(w / 2, 90,
                                text="Кликни и тяни мышью по любому индикатору",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

    # ---------- СИМУЛЯЦИЯ ----------
    def _simulate(self, dt):
        self.t += dt
        t = self.t
        # качество — плавно
        self.quality.target = 60 + 25 * math.sin(t * 0.4) + random.uniform(-2, 2)
        # скорость — резче
        self.speed.target = 110 + 90 * math.sin(t * 0.7) + random.uniform(-8, 8)

    # ---------- КЛИКИ / ПЕРЕТАСКИВАНИЕ ----------
    def _hit(self, x, y):
        for key, (x0, y0, x1, y1) in self.hit_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                return key
        return None

    def _on_click(self, event):
        hit = self._hit(event.x, event.y)
        if hit:
            self.drag_target = hit
            self.drag_start_y = event.y
            if hit in ("bar", "ring", "arc"):
                self.drag_start_v = self.quality.target
            elif hit == "speed":
                self.drag_start_v = self.speed.target

    def _on_drag(self, event):
        if not self.drag_target:
            return
        # тянем вверх — увеличиваем, вниз — уменьшаем
        k = -(event.y - self.drag_start_y) / 200.0
        if self.drag_target in ("bar", "ring", "arc"):
            self.quality.target = max(0, min(100,
                self.drag_start_v + k * 100))
            self.quality.value = self.quality.target
        elif self.drag_target == "speed":
            self.speed.target = max(0, min(240,
                self.drag_start_v + k * 240))
            self.speed.value = self.speed.target

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
        self.quality.tick()
        self.speed.tick(dt)

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()