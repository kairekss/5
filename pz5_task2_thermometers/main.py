"""
ОКФРС. Практика 5. Задание 2.
Вертикальные термометры 4 типов:
- Классический (воздух, -30..50°C)
- Электронный (процессор, 0..100°C, LCD)
- Криогенный (жидкий азот, -200..0°C)
- Инфракрасный (тело, 35..42°C)
Плюс — график изменения температуры за последние 60 с.
Премиум-стиль 2026.
"""
import tkinter as tk
import sys, os, math, random, time
from collections import deque

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
FONT_LCD   = ("Consolas", 28, "bold")


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
# ДАННЫЕ ТЕРМОМЕТРА
# ============================================================
class ThermoData:
    def __init__(self, title, unit, min_v, max_v, color,
                 warn_lo=None, warn_hi=None, crit_lo=None, crit_hi=None,
                 history_len=60):
        self.title = title
        self.unit = unit
        self.min_v = min_v
        self.max_v = max_v
        self.color = color
        self.value = (min_v + max_v) / 2
        self.target = self.value
        self.warn_lo = warn_lo
        self.warn_hi = warn_hi
        self.crit_lo = crit_lo
        self.crit_hi = crit_hi
        self.history = deque(maxlen=history_len)  # для графика

    def status(self):
        v = self.value
        if self.crit_lo is not None and v < self.crit_lo: return "CRIT"
        if self.crit_hi is not None and v > self.crit_hi: return "CRIT"
        if self.warn_lo is not None and v < self.warn_lo: return "WARN"
        if self.warn_hi is not None and v > self.warn_hi: return "WARN"
        return "OK"

    def status_color(self):
        return {"OK": NEON_GREEN, "WARN": NEON_AMBER, "CRIT": NEON_RED}[self.status()]

    def status_text(self):
        return {"OK": "НОРМА", "WARN": "ВНИМАНИЕ", "CRIT": "КРИТИЧНО"}[self.status()]

    def tick(self):
        diff = self.target - self.value
        if abs(diff) > 0.001:
            self.value += diff * 0.15
        else:
            self.value = self.target
        self.history.append(self.value)


# ============================================================
# КЛАССИЧЕСКИЙ ТЕРМОМЕТР
# ============================================================
def draw_classic_thermo(canvas, cx, cy, w, h, data):
    """
    Классический вертикальный термометр:
    стеклянная трубка, шарик снизу, деления, ртуть.
    """
    tube_x0 = cx - w/2
    tube_x1 = cx + w/2
    tube_y0 = cy - h/2
    tube_y1 = cy + h/2

    # внешняя колба-карточка
    round_rect(canvas, tube_x0 - 35, tube_y0 - 55,
               tube_x1 + 80, tube_y1 + 70, 18,
               fill=BG_GLASS, outline=BORDER, width=1)

    # заголовок
    canvas.create_text(cx, tube_y0 - 35, text=data.title,
                       fill=TEXT_GLOW, font=FONT_LABEL)
    canvas.create_text(cx, tube_y0 - 18, text="CLASSIC",
                       fill=TEXT_DIM, font=FONT_LABEL_S)

    # стеклянная трубка
    round_rect(canvas, tube_x0, tube_y0, tube_x1, tube_y1,
               w/2, fill="#0a0d14",
               outline=lerp(data.color, BG_DEEP, 0.5), width=2)

    # шарик снизу
    ball_r = w * 0.9
    canvas.create_oval(cx - ball_r, tube_y1 - ball_r/2,
                       cx + ball_r, tube_y1 + ball_r * 1.5,
                       fill=lerp(data.color, BG_DEEP, 0.3),
                       outline=data.color, width=2)

    # деления
    n = 9
    for i in range(n):
        k = i / (n - 1)
        y = tube_y1 - k * (tube_y1 - tube_y0)
        is_major = (i % 2 == 0)
        tick_len = 14 if is_major else 7
        canvas.create_line(tube_x1 + 6, y, tube_x1 + 6 + tick_len, y,
                           fill=TEXT_GLOW if is_major else TEXT_DIM,
                           width=2 if is_major else 1)
        if is_major:
            v = data.min_v + (data.max_v - data.min_v) * k
            canvas.create_text(tube_x1 + 6 + tick_len + 14, y,
                               text=f"{v:+.0f}",
                               fill=TEXT_GLOW,
                               font=("Consolas", 9, "bold"), anchor="w")

    # ртуть
    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    fill_y = tube_y1 - k * (tube_y1 - tube_y0)
    round_rect(canvas, tube_x0 + 4, fill_y, tube_x1 - 4, tube_y1 - 2,
               w/2 - 4, fill=data.color)

    # блик
    round_rect(canvas, tube_x0 + 6, tube_y0 + 6,
               tube_x0 + 11, tube_y1 - 6, 2,
               fill=lerp(data.color, "#FFFFFF", 0.5))

    # значение снизу
    canvas.create_text(cx, tube_y1 + 40,
                       text=f"{data.value:.1f} {data.unit}",
                       fill=data.status_color(), font=FONT_VAL)
    canvas.create_text(cx, tube_y1 + 60,
                       text=data.status_text(),
                       fill=data.status_color(), font=FONT_LABEL_S)


# ============================================================
# ЭЛЕКТРОННЫЙ ТЕРМОМЕТР (LCD)
# ============================================================
def draw_lcd_thermo(canvas, cx, cy, w, h, data):
    """Электронный термометр с LCD-экраном и полоской заполнения."""
    x0 = cx - w/2
    y0 = cy - h/2
    x1 = cx + w/2
    y1 = cy + h/2

    # корпус
    round_rect(canvas, x0, y0, x1, y1, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    # заголовок
    canvas.create_text(cx, y0 + 22, text=data.title,
                       fill=TEXT_GLOW, font=FONT_LABEL)
    canvas.create_text(cx, y0 + 40, text="LCD · DIGITAL",
                       fill=TEXT_DIM, font=FONT_LABEL_S)

    # LCD-экран
    lcd_x0 = x0 + 14
    lcd_y0 = y0 + 60
    lcd_x1 = x1 - 14
    lcd_y1 = lcd_y0 + 90
    round_rect(canvas, lcd_x0, lcd_y0, lcd_x1, lcd_y1, 8,
               fill="#02060a",
               outline=lerp(data.color, BG_DEEP, 0.5), width=2)

    # цифры LCD
    canvas.create_text((lcd_x0 + lcd_x1) / 2, (lcd_y0 + lcd_y1) / 2,
                       text=f"{data.value:.2f}",
                       fill=data.color, font=FONT_LCD)
    # знак градусов
    canvas.create_text(lcd_x1 - 18, lcd_y0 + 25,
                       text="°" + data.unit,
                       fill=lerp(data.color, "#FFFFFF", 0.5),
                       font=("Consolas", 12, "bold"), anchor="e")

    # шкала-полоска
    bar_y0 = lcd_y1 + 20
    bar_y1 = bar_y0 + 60
    bar_x0 = x0 + 14
    bar_x1 = x1 - 14

    round_rect(canvas, bar_x0, bar_y0, bar_x1, bar_y1, 8,
               fill="#0a0d14", outline=BORDER, width=1)

    # деления
    for i in range(11):
        k = i / 10
        xx = bar_x0 + 4 + k * (bar_x1 - bar_x0 - 8)
        canvas.create_line(xx, bar_y1 - 10, xx, bar_y1 - 3,
                           fill=TEXT_DIM, width=1)

    # заполнение
    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    fill_w = (bar_x1 - bar_x0 - 8) * k
    if fill_w > 2:
        round_rect(canvas, bar_x0 + 4, bar_y0 + 4,
                   bar_x0 + 4 + fill_w, bar_y1 - 4, 6,
                   fill=data.color)

    # min/max подписи
    canvas.create_text(bar_x0, bar_y1 + 14, anchor="w",
                       text=f"{data.min_v:.0f}",
                       fill=TEXT_DIM, font=FONT_MONO_S)
    canvas.create_text(bar_x1, bar_y1 + 14, anchor="e",
                       text=f"{data.max_v:.0f} {data.unit}",
                       fill=TEXT_DIM, font=FONT_MONO_S)

    # статус
    canvas.create_text(cx, y1 - 18,
                       text="● " + data.status_text(),
                       fill=data.status_color(), font=FONT_LABEL)


# ============================================================
# КРИОГЕННЫЙ ТЕРМОМЕТР
# ============================================================
def draw_cryo_thermo(canvas, cx, cy, w, h, data):
    """Термометр для жидкого азота: -200..0°C, холодная палитра."""
    x0 = cx - w/2
    y0 = cy - h/2
    x1 = cx + w/2
    y1 = cy + h/2

    round_rect(canvas, x0, y0, x1, y1, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, y0 + 22, text=data.title,
                       fill=TEXT_GLOW, font=FONT_LABEL)
    canvas.create_text(cx, y0 + 40, text="CRYO · N₂",
                       fill=NEON_CYAN, font=FONT_LABEL_S)

    # горизонтальная шкала-бар
    bar_x0 = x0 + 20
    bar_x1 = x1 - 20
    bar_y = cy + 10
    bar_h = 60

    round_rect(canvas, bar_x0, bar_y - bar_h/2,
               bar_x1, bar_y + bar_h/2, 12,
               fill="#050810",
               outline=lerp(NEON_CYAN, BG_DEEP, 0.5), width=2)

    # градиент холода слева-направо
    n_segments = 30
    for i in range(n_segments):
        k0 = i / n_segments
        k1 = (i + 1) / n_segments
        xx0 = bar_x0 + 6 + k0 * (bar_x1 - bar_x0 - 12)
        xx1 = bar_x0 + 6 + k1 * (bar_x1 - bar_x0 - 12)
        col = lerp(NEON_BLUE, "#ffffff", k0)
        canvas.create_line(xx0, bar_y - bar_h/2 + 6,
                           xx1, bar_y + bar_h/2 - 6,
                           fill=lerp(col, BG_DEEP, 0.55), width=int((xx1 - xx0) + 1))

    # деления
    for i in range(9):
        k = i / 8
        xx = bar_x0 + 6 + k * (bar_x1 - bar_x0 - 12)
        is_major = (i % 2 == 0)
        canvas.create_line(xx, bar_y - bar_h/2 - 6, xx,
                           bar_y - bar_h/2 + 2,
                           fill=TEXT_GLOW if is_major else TEXT_DIM,
                           width=2 if is_major else 1)
        if is_major:
            v = data.min_v + (data.max_v - data.min_v) * k
            canvas.create_text(xx, bar_y - bar_h/2 - 14,
                               text=f"{v:.0f}",
                               fill=TEXT_GLOW,
                               font=("Consolas", 9, "bold"))

    # маркер
    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    mx = bar_x0 + 6 + k * (bar_x1 - bar_x0 - 12)
    canvas.create_line(mx, bar_y - bar_h/2 - 4,
                       mx, bar_y + bar_h/2 + 4,
                       fill="#ffffff", width=3)
    canvas.create_polygon(mx - 8, bar_y + bar_h/2 + 6,
                          mx + 8, bar_y + bar_h/2 + 6,
                          mx, bar_y + bar_h/2 + 18,
                          fill="#ffffff")

    # значение
    canvas.create_text(cx, y1 - 60,
                       text=f"{data.value:.2f} {data.unit}",
                       fill=NEON_CYAN, font=FONT_VAL)
    canvas.create_text(cx, y1 - 35,
                       text=data.status_text(),
                       fill=data.status_color(), font=FONT_LABEL)

    # символ снежинки
    canvas.create_text(x1 - 30, y0 + 22, text="❄",
                       fill=NEON_CYAN,
                       font=("Segoe UI Emoji", 18))


# ============================================================
# ИНФРАКРАСНЫЙ ТЕРМОМЕТР (тело)
# ============================================================
def draw_ir_thermo(canvas, cx, cy, w, h, data):
    """Инфракрасный термометр — температура тела, 35..42°C."""
    x0 = cx - w/2
    y0 = cy - h/2
    x1 = cx + w/2
    y1 = cy + h/2

    round_rect(canvas, x0, y0, x1, y1, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, y0 + 22, text=data.title,
                       fill=TEXT_GLOW, font=FONT_LABEL)
    canvas.create_text(cx, y0 + 40, text="INFRARED · BODY",
                       fill=NEON_PINK, font=FONT_LABEL_S)

    # большая цифра
    canvas.create_text(cx, cy - 20,
                       text=f"{data.value:.2f}",
                       fill=data.status_color(),
                       font=("Consolas", 38, "bold"))
    canvas.create_text(cx, cy + 18,
                       text="°C",
                       fill=TEXT_DIM, font=("Consolas", 16, "bold"))

    # горизонтальная полоска-индикатор
    bar_x0 = x0 + 20
    bar_x1 = x1 - 20
    bar_y = cy + 60

    # цветные зоны
    zones = [
        (0.00, 0.20, NEON_BLUE, "НОРМА"),
        (0.20, 0.55, NEON_GREEN, "НОРМА"),
        (0.55, 0.85, NEON_AMBER, "ЖАР"),
        (0.85, 1.00, NEON_RED, "ЖАР"),
    ]
    bar_h = 14
    for k0, k1, col, _l in zones:
        xx0 = bar_x0 + k0 * (bar_x1 - bar_x0)
        xx1 = bar_x0 + k1 * (bar_x1 - bar_x0)
        round_rect(canvas, xx0, bar_y - bar_h/2, xx1, bar_y + bar_h/2,
                   4, fill=lerp(col, BG_DEEP, 0.4))

    # маркер
    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    mx = bar_x0 + k * (bar_x1 - bar_x0)
    canvas.create_line(mx, bar_y - 14, mx, bar_y + 14,
                       fill="#ffffff", width=3)
    canvas.create_oval(mx - 6, bar_y - bar_h/2 - 12,
                       mx + 6, bar_y - bar_h/2 - 2,
                       fill="#ffffff", outline="")

    # подписи диапазона
    canvas.create_text(bar_x0, bar_y + 22, anchor="w",
                       text=f"{data.min_v:.1f}°C",
                       fill=TEXT_DIM, font=FONT_MONO_S)
    canvas.create_text(bar_x1, bar_y + 22, anchor="e",
                       text=f"{data.max_v:.1f}°C",
                       fill=TEXT_DIM, font=FONT_MONO_S)

    # статус
    canvas.create_text(cx, y1 - 20,
                       text="● " + data.status_text(),
                       fill=data.status_color(), font=FONT_LABEL)


# ============================================================
# ГРАФИК ИСТОРИИ
# ============================================================
def draw_history_chart(canvas, x, y, w, h, series):
    """
    Рисует график изменения значений.
    series = [(data, color, label), ...]
    """
    round_rect(canvas, x, y, x + w, y + h, 12,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(x + 16, y + 18, anchor="w",
                       text="▸ ДИНАМИКА ЗА 60 СЕК",
                       fill=NEON_CYAN, font=FONT_LABEL)

    # легенда
    lx = x + w - 16
    for data, color, label in reversed(series):
        canvas.create_text(lx, y + 18, anchor="e", text=label,
                           fill=color, font=FONT_LABEL_S)
        lx -= 100
        canvas.create_oval(lx + 4, y + 14, lx + 12, y + 22,
                           fill=color, outline="")
        lx -= 16

    # сетка
    gx0 = x + 40
    gy0 = y + 40
    gx1 = x + w - 20
    gy1 = y + h - 20

    for i in range(5):
        gy = gy0 + i * (gy1 - gy0) / 4
        canvas.create_line(gx0, gy, gx1, gy,
                           fill="#1a1f2e", width=1)

    canvas.create_line(gx0, gy1, gx1, gy1, fill=BORDER)
    canvas.create_line(gx0, gy0, gx0, gy1, fill=BORDER)

    # для каждого ряда — свой график в своём масштабе
    for data, color, label in series:
        hist = list(data.history)
        if len(hist) < 2:
            continue
        mn, mx = data.min_v, data.max_v
        span = mx - mn if mx != mn else 1
        n = len(hist)
        step = (gx1 - gx0) / max(n - 1, 1)

        # свечение под линией
        pts_glow = []
        pts = []
        for i, v in enumerate(hist):
            k = (v - mn) / span
            k = max(0.0, min(1.0, k))
            px = gx0 + i * step
            py = gy1 - k * (gy1 - gy0)
            pts.append((px, py))
            pts_glow.append((px, py))

        # линия
        if len(pts) >= 2:
            flat = []
            for (px, py) in pts:
                flat.extend([px, py])
            canvas.create_line(*flat, fill=lerp(color, BG_DEEP, 0.7),
                               width=6, smooth=True)
            canvas.create_line(*flat, fill=color, width=2, smooth=True)

            # точка на конце
            last_x, last_y = pts[-1]
            canvas.create_oval(last_x - 4, last_y - 4,
                               last_x + 4, last_y + 4,
                               fill=color, outline="")


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("🌡 Multi-Thermometer Station · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # ---- 4 термометра ----
        # Классический (воздух)
        self.th_air = ThermoData(
            "ВОЗДУХ", "°C", -30, 50, NEON_RED,
            warn_lo=-20, warn_hi=35, crit_lo=-25, crit_hi=42)

        # Электронный (процессор)
        self.th_cpu = ThermoData(
            "ПРОЦЕССОР", "°C", 0, 100, NEON_GREEN,
            warn_hi=75, crit_hi=90)

        # Криогенный (жидкий азот)
        self.th_cryo = ThermoData(
            "ЖИДКИЙ АЗОТ", "°C", -200, 0, NEON_CYAN,
            warn_hi=-150, crit_hi=-100)

        # Инфракрасный (тело)
        self.th_body = ThermoData(
            "ТЕЛО", "°C", 35, 42, NEON_PINK,
            warn_hi=37.5, crit_hi=38.5)

        # начальные значения
        self.th_air.value = self.th_air.target = 22.0
        self.th_cpu.value = self.th_cpu.target = 55.0
        self.th_cryo.value = self.th_cryo.target = -196.0
        self.th_body.value = self.th_body.target = 36.6

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        self.root.update_idletasks()
        self._redraw_all()
        self._animate()

    def _on_resize(self, event):
        self._redraw_all()

    # ---------- ПОЛНАЯ ПЕРЕРИСОВКА ----------
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
            self.canvas.create_rectangle(0, y0, w, y1,
                                         fill=col, outline="")

        # заголовок
        self.canvas.create_text(60, 40, text="🌡",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="MULTI-THERMOMETER STATION",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(480, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # 4 термометра в ряд
        top_y = 320
        cx_positions = [w * 0.14, w * 0.36, w * 0.58, w * 0.80]

        # 1. Классический
        draw_classic_thermo(self.canvas, cx_positions[0], top_y,
                            38, 320, self.th_air)

        # 2. Электронный
        draw_lcd_thermo(self.canvas, cx_positions[1], top_y,
                        240, 400, self.th_cpu)

        # 3. Криогенный
        draw_cryo_thermo(self.canvas, cx_positions[2], top_y,
                         240, 260, self.th_cryo)

        # 4. Инфракрасный
        draw_ir_thermo(self.canvas, cx_positions[3], top_y,
                       240, 260, self.th_body)

        # график внизу
        draw_history_chart(self.canvas, 40, h - 240, w - 80, 200,
                           [(self.th_air, NEON_RED, "Воздух"),
                            (self.th_cpu, NEON_GREEN, "CPU"),
                            (self.th_cryo, NEON_CYAN, "N₂"),
                            (self.th_body, NEON_PINK, "Тело")])

        # FPS
        self.canvas.create_text(w - 60, 37,
                                text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S,
                                anchor="e")

    # ---------- СИМУЛЯЦИЯ ----------
    def _simulate(self, dt):
        self.t += dt
        t = self.t

        # воздух — медленно колеблется вокруг 22°
        self.th_air.target = 22 + 6 * math.sin(t * 0.15) + random.uniform(-0.3, 0.3)

        # процессор — зависит от нагрузки (быстрые колебания)
        self.th_cpu.target = 55 + 20 * math.sin(t * 0.8) + random.uniform(-1, 1)

        # азот — почти стабилен, чуть дрейфует
        self.th_cryo.target = -196 + 2 * math.sin(t * 0.1) + random.uniform(-0.3, 0.3)

        # тело — почти стабильно, иногда поднимается (жар)
        base = 36.6 + 0.4 * math.sin(t * 0.3)
        # случайный "приступ жара" раз в 20 секунд
        if int(t) % 30 < 5:
            base += 1.5
        self.th_body.target = base + random.uniform(-0.05, 0.05)

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

        for th in (self.th_air, self.th_cpu, self.th_cryo, self.th_body):
            th.tick()

        self._redraw_all()
        self.root.after(33, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()