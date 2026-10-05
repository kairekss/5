"""
ОКФРС. Практика 5. Задание 1.
Приборная панель промышленной установки.
5 датчиков + журнал событий + статус-бар.
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

TEXT_MAIN  = "#e8f0ff"
TEXT_DIM   = "#5a6780"
TEXT_GLOW  = "#8fa4c4"

FONT_MONO  = ("Consolas", 13, "bold")
FONT_MONO_S= ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_LABEL_S = ("Segoe UI", 9)
FONT_VAL   = ("Consolas", 16, "bold")


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
# СОСТОЯНИЕ (данные приборов)
# ============================================================
class GaugeData:
    """Только данные, без рисования."""
    def __init__(self, label, unit, min_v, max_v, color,
                 tick_step, arc_zones, fmt,
                 warn_lo=None, warn_hi=None, crit_lo=None, crit_hi=None):
        self.label = label
        self.unit = unit
        self.min_v = min_v
        self.max_v = max_v
        self.color = color
        self.tick_step = tick_step
        self.arc_zones = arc_zones
        self.fmt = fmt
        self.warn_lo = warn_lo
        self.warn_hi = warn_hi
        self.crit_lo = crit_lo
        self.crit_hi = crit_hi
        self.value = (min_v + max_v) / 2
        self.target = self.value

    def status(self):
        v = self.value
        if self.crit_lo is not None and v < self.crit_lo: return "CRIT"
        if self.crit_hi is not None and v > self.crit_hi: return "CRIT"
        if self.warn_lo is not None and v < self.warn_lo: return "WARN"
        if self.warn_hi is not None and v > self.warn_hi: return "WARN"
        return "OK"

    def status_color(self):
        return {"OK": NEON_GREEN, "WARN": NEON_AMBER, "CRIT": NEON_RED}[self.status()]

    def tick(self):
        diff = self.target - self.value
        if abs(diff) > 0.001:
            self.value += diff * 0.15
        else:
            self.value = self.target


# ============================================================
# ОТРИСОВКА ПРИБОРОВ (чистые функции)
# ============================================================
def draw_round_gauge(canvas, cx, cy, r, data, tag="gauge"):
    """Рисует круглый прибор со стрелкой по текущему значению data.value."""
    a_start = math.radians(225)
    a_end = math.radians(-45)

    def v_to_a(v):
        k = (v - data.min_v) / (data.max_v - data.min_v)
        k = max(0.0, min(1.0, k))
        return a_start + (a_end - a_start) * k

    # обод
    canvas.create_oval(cx - r - 3, cy - r + 2, cx + r + 3, cy + r + 8,
                       fill="#000000", outline="", tags=tag)
    for i in range(8):
        k = i / 8
        rr = r - k * 6
        col = lerp("#2a3040", "#05070c", k)
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill=col, outline="", tags=tag)
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=lerp(data.color, "#000000", 0.6),
                       width=3, tags=tag)
    canvas.create_oval(cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5,
                       fill="", outline=lerp(data.color, BG_DEEP, 0.6),
                       width=1, tags=tag)

    inner_r = r - 18
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14",
                       outline=lerp(data.color, BG_DEEP, 0.5),
                       width=1, tags=tag)

    # цветные зоны
    for (z_from, z_to, z_col) in data.arc_zones:
        a1 = math.degrees(v_to_a(z_from))
        a2 = math.degrees(v_to_a(z_to))
        canvas.create_arc(cx - inner_r + 2, cy - inner_r + 2,
                          cx + inner_r - 2, cy + inner_r - 2,
                          start=a2, extent=a1 - a2,
                          style="arc", outline=z_col, width=6,
                          tags=tag)

    # деления
    n_ticks = int((data.max_v - data.min_v) / data.tick_step) + 1
    for i in range(n_ticks):
        v = data.min_v + i * data.tick_step
        a = v_to_a(v)
        is_major = (i % 2 == 0)
        tick_len = 10 if is_major else 5
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        col = TEXT_GLOW if is_major else TEXT_DIM
        w = 2 if is_major else 1
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w, tags=tag)
        if is_major:
            tx = cx + (inner_r - 22) * math.cos(a)
            ty = cy - (inner_r - 22) * math.sin(a)
            label_txt = f"{v:.0f}" if abs(v) >= 1 else f"{v:.1f}"
            canvas.create_text(tx, ty, text=label_txt,
                               fill=TEXT_GLOW,
                               font=("Consolas", 8, "bold"),
                               tags=tag)

    # стрелка
    a = v_to_a(data.value)
    canvas.create_line(cx + 2, cy + 2,
                       cx + 2 + (inner_r - 12) * math.cos(a),
                       cy + 2 - (inner_r - 12) * math.sin(a),
                       fill="#000000", width=5, tags=tag)
    canvas.create_line(cx, cy,
                       cx + (inner_r - 12) * math.cos(a),
                       cy - (inner_r - 12) * math.sin(a),
                       fill=NEON_RED, width=3,
                       capstyle="round", tags=tag)
    canvas.create_line(cx, cy,
                       cx - 15 * math.cos(a),
                       cy + 15 * math.sin(a),
                       fill=lerp(NEON_RED, "#000000", 0.4), width=3,
                       capstyle="round", tags=tag)
    canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10,
                       fill="#1a1f2e",
                       outline=lerp(data.color, BG_DEEP, 0.4),
                       width=2, tags=tag)
    canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4,
                       fill=data.color, outline="", tags=tag)

    # подписи
    canvas.create_text(cx, cy + r - 30, text=data.label,
                       fill=TEXT_GLOW, font=FONT_LABEL, tags=tag)
    canvas.create_text(cx, cy + r - 12, text=data.unit,
                       fill=TEXT_DIM, font=("Segoe UI", 9), tags=tag)
    canvas.create_text(cx, cy + r + 22,
                       text=data.fmt.format(data.value),
                       fill=data.status_color(), font=FONT_VAL, tags=tag)


def draw_thermometer(canvas, cx, cy, w, h, data, tag="gauge"):
    tube_x0 = cx - w/2
    tube_x1 = cx + w/2
    tube_y0 = cy - h/2
    tube_y1 = cy + h/2

    round_rect(canvas, cx - w/2 - 20, cy - h/2 - 40,
               cx + w/2 + 20, cy + h/2 + 70, 16,
               fill=BG_GLASS, outline=BORDER, width=1, tags=tag)
    canvas.create_text(cx, cy - h/2 - 20, text=data.label,
                       fill=TEXT_GLOW, font=FONT_LABEL, tags=tag)

    round_rect(canvas, tube_x0, tube_y0, tube_x1, tube_y1,
               w/2, fill="#0a0d14",
               outline=lerp(data.color, BG_DEEP, 0.5),
               width=2, tags=tag)

    ball_r = w * 0.75
    canvas.create_oval(cx - ball_r, tube_y1 - ball_r/2,
                       cx + ball_r, tube_y1 + ball_r * 1.5,
                       fill=lerp(data.color, BG_DEEP, 0.3),
                       outline=data.color, width=2, tags=tag)

    n = 11
    for i in range(n):
        k = i / (n - 1)
        y = tube_y1 - k * (tube_y1 - tube_y0)
        is_major = (i % 2 == 0)
        tick_len = 12 if is_major else 6
        canvas.create_line(tube_x1 + 4, y, tube_x1 + 4 + tick_len, y,
                           fill=TEXT_GLOW if is_major else TEXT_DIM,
                           width=2 if is_major else 1, tags=tag)
        if is_major:
            v = data.min_v + (data.max_v - data.min_v) * k
            canvas.create_text(tube_x1 + 4 + tick_len + 12, y,
                               text=f"{v:.0f}", fill=TEXT_GLOW,
                               font=("Consolas", 9, "bold"),
                               anchor="w", tags=tag)

    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    fill_y = tube_y1 - k * (tube_y1 - tube_y0)
    round_rect(canvas, tube_x0 + 4, fill_y, tube_x1 - 4, tube_y1 - 2,
               w/2 - 4, fill=data.color, tags=tag)

    round_rect(canvas, tube_x0 + 6, tube_y0 + 6,
               tube_x0 + 12, tube_y1 - 6, 3,
               fill=lerp(data.color, "#FFFFFF", 0.4), tags=tag)

    canvas.create_text(cx, cy + h/2 + 40,
                       text=f"{data.value:.1f} {data.unit}",
                       fill=data.status_color(), font=FONT_VAL, tags=tag)


def draw_goodbad(canvas, cx, cy, r, data, tag="gauge"):
    round_rect(canvas, cx - r - 30, cy - r - 40,
               cx + r + 30, cy + r + 80, 16,
               fill=BG_GLASS, outline=BORDER, tags=tag)
    canvas.create_text(cx, cy - r - 20, text=data.label,
                       fill=TEXT_GLOW, font=FONT_LABEL, tags=tag)

    zones = [(0.00, 0.35, NEON_RED),
             (0.35, 0.65, NEON_AMBER),
             (0.65, 1.00, NEON_GREEN)]
    for (k0, k1, col) in zones:
        s = 180 + 180 * k0
        e = 180 * (k1 - k0)
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                          start=s, extent=-e,
                          style="arc", outline=col, width=14, tags=tag)

    canvas.create_oval(cx - r - 8, cy - r - 8,
                       cx + r + 8, cy + r + 8,
                       fill="", outline=lerp(NEON_CYAN, BG_DEEP, 0.7),
                       width=2, tags=tag)
    canvas.create_text(cx - r + 20, cy - r + 30, text="BAD",
                       fill=NEON_RED, font=("Segoe UI", 9, "bold"), tags=tag)
    canvas.create_text(cx + r - 20, cy - r + 30, text="GOOD",
                       fill=NEON_GREEN, font=("Segoe UI", 9, "bold"), tags=tag)

    for i in range(11):
        k = i / 10
        a = math.radians(180 + 180 * k)
        x1 = cx + (r - 22) * math.cos(a)
        y1 = cy - (r - 22) * math.sin(a)
        x2 = cx + (r - 14) * math.cos(a)
        y2 = cy - (r - 14) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=TEXT_DIM, width=1, tags=tag)

    k = (data.value - data.min_v) / (data.max_v - data.min_v)
    k = max(0.0, min(1.0, k))
    a = math.radians(180 + 180 * k)
    canvas.create_line(cx + 2, cy + 2,
                       cx + 2 + (r - 30) * math.cos(a),
                       cy + 2 - (r - 30) * math.sin(a),
                       fill="#000000", width=5, tags=tag)
    canvas.create_line(cx, cy,
                       cx + (r - 30) * math.cos(a),
                       cy - (r - 30) * math.sin(a),
                       fill="#FFFFFF", width=3, capstyle="round", tags=tag)
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill="#1a1f2e", outline="#FFFFFF", width=2, tags=tag)

    if data.value < 35: col = NEON_RED
    elif data.value < 65: col = NEON_AMBER
    else: col = NEON_GREEN
    canvas.create_text(cx, cy + 30, text=f"{data.value:.1f} %",
                       fill=col, font=FONT_VAL, tags=tag)
    canvas.create_text(cx, cy + r + 40, text=data.unit,
                       fill=TEXT_DIM, font=FONT_LABEL, tags=tag)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚙ Industrial Control Panel · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # ==== приборы (только данные) ====
        self.g_pressure = GaugeData(
            "ДАВЛЕНИЕ", "бар", 0, 2.5, NEON_CYAN,
            0.5, [(2.0, 2.5, NEON_RED)], "{:.2f}",
            warn_hi=1.9, crit_hi=2.2)

        self.g_temp = GaugeData(
            "ТЕМПЕРАТУРА", "°C", -30, 60, NEON_PINK,
            9, [], "{:.1f}",
            warn_hi=35, crit_hi=45)

        self.g_baro = GaugeData(
            "БАРОМЕТР", "мм рт.ст.", 720, 790, NEON_AMBER,
            10, [(720, 745, NEON_RED), (745, 765, NEON_AMBER),
                 (765, 790, NEON_GREEN)], "{:.1f}",
            warn_lo=740, warn_hi=775, crit_lo=730, crit_hi=785)

        self.g_quality = GaugeData(
            "КАЧЕСТВО", "оценка %", 0, 100, NEON_GREEN,
            10, [], "{:.1f}")

        self.g_load = GaugeData(
            "НАГРУЗКА", "км/ч", 0, 240, NEON_PURP,
            20, [(180, 240, NEON_RED)], "{:.0f}",
            warn_hi=160, crit_hi=200)

        # события
        self.events = deque(maxlen=6)
        self.last_status = {}
        self._layout_coords = {}      # координаты для перерисовки

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        # первый расчёт координат + отрисовка
        self.root.update_idletasks()
        self._calc_layout()
        self._redraw_all()

        self._animate()

    def _on_resize(self, event):
        # пересчитываем координаты и полностью перерисовываем
        self._calc_layout()
        self._redraw_all()

    # ---------- КООРДИНАТЫ ----------
    def _calc_layout(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        top_y = 230
        self._layout_coords = {
            "pressure": (w * 0.13, top_y + 130, 110),
            "temp":     (w * 0.30, top_y + 130, 40, 260),
            "baro":     (w * 0.47, top_y + 130, 110),
            "quality":  (w * 0.65, top_y + 140, 110),
            "load":     (w * 0.5,  top_y + 420, 140),
        }

    # ---------- ФОН + СТАТИКА ----------
    def _redraw_all(self):
        """Полная перерисовка: фон, заголовок, приборы, статус-бар, журнал."""
        self.canvas.delete("all")

        w, h = self.W, self.H

        # фон
        for i in range(40):
            y0 = int(i * h / 40)
            y1 = int((i + 1) * h / 40)
            col = lerp(BG_DEEP, "#0a0e18", i / 40)
            self.canvas.create_rectangle(0, y0, w, y1,
                                         fill=col, outline="")

        # заголовок
        self.canvas.create_text(60, 40, text="⚙",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="INDUSTRIAL CONTROL PANEL",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(430, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # приборы (все 5 в правильных позициях)
        p = self._layout_coords
        cx, cy, r = p["pressure"]
        draw_round_gauge(self.canvas, cx, cy, r, self.g_pressure)

        cx, cy, tw, th = p["temp"]
        draw_thermometer(self.canvas, cx, cy, tw, th, self.g_temp)

        cx, cy, r = p["baro"]
        draw_round_gauge(self.canvas, cx, cy, r, self.g_baro)

        cx, cy, r = p["quality"]
        draw_goodbad(self.canvas, cx, cy, r, self.g_quality)

        cx, cy, r = p["load"]
        draw_round_gauge(self.canvas, cx, cy, r, self.g_load)

        # статус-бар сверху
        self._draw_status_bar(w)

        # журнал событий внизу
        self._draw_event_log(w, h)

        # FPS
        self.canvas.create_text(w - 60, 37,
                                text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S,
                                anchor="e")

    # ---------- СТАТУС-БАР ----------
    def _draw_status_bar(self, w):
        y = 90
        h = 60
        round_rect(self.canvas, 40, y, w - 40, y + h, 12,
                   fill=BG_GLASS, outline=BORDER)

        items = [
            ("СИСТЕМА", "АКТИВНА", NEON_GREEN),
            ("ДАТЧИКОВ", "5 / 5", NEON_CYAN),
            ("ВРЕМЯ", time.strftime("%H:%M:%S"), TEXT_GLOW),
            ("СОБЫТИЙ", f"{len(self.events)}", NEON_AMBER),
        ]
        x_step = (w - 100) / len(items)
        for i, (label, val, col) in enumerate(items):
            x = 60 + i * x_step
            self.canvas.create_text(x, y + 22, anchor="w",
                                    text=label, fill=TEXT_DIM,
                                    font=FONT_LABEL_S)
            self.canvas.create_text(x, y + 42, anchor="w",
                                    text=val, fill=col, font=FONT_MONO)

    # ---------- ЖУРНАЛ СОБЫТИЙ ----------
    def _draw_event_log(self, w, h):
        x, y = 40, h - 200
        ww, hh = w - 80, 160

        round_rect(self.canvas, x, y, x + ww, y + hh, 12,
                   fill=BG_GLASS, outline=BORDER)

        self.canvas.create_text(x + 16, y + 18, anchor="w",
                                text="▸ ЖУРНАЛ СОБЫТИЙ", fill=NEON_CYAN,
                                font=FONT_LABEL)
        self.canvas.create_text(x + ww - 16, y + 18, anchor="e",
                                text=f"{len(self.events)} записей",
                                fill=TEXT_DIM, font=FONT_LABEL_S)
        self.canvas.create_line(x + 12, y + 32, x + ww - 12, y + 32,
                                fill=BORDER)

        colors = {"INFO": TEXT_GLOW, "WARN": NEON_AMBER,
                  "ERROR": NEON_RED, "OK": NEON_GREEN}
        for i, (ts, source, msg, level) in enumerate(self.events):
            ey = y + 48 + i * 22
            col = colors.get(level, TEXT_GLOW)
            self.canvas.create_text(x + 16, ey, anchor="w", text=ts,
                                    fill=TEXT_DIM, font=FONT_MONO_S)
            self.canvas.create_oval(x + 82, ey - 4, x + 90, ey + 4,
                                    fill=col, outline="")
            self.canvas.create_text(x + 100, ey, anchor="w", text=source,
                                    fill=col, font=FONT_MONO_S)
            self.canvas.create_text(x + 190, ey, anchor="w", text=msg,
                                    fill=TEXT_GLOW, font=FONT_LABEL_S)

    # ---------- СОБЫТИЯ ----------
    def _push_event(self, source, msg, level="INFO"):
        ts = time.strftime("%H:%M:%S")
        self.events.appendleft((ts, source, msg, level))

    # ---------- СИМУЛЯЦИЯ ----------
    def _simulate(self, dt):
        self.t += dt
        t = self.t
        random.seed(int(t * 100) % 1000)
        self.g_baro.target = 757 + 12 * math.sin(t * 0.15) + random.uniform(-0.3, 0.3)
        self.g_pressure.target = 1.6 + 0.35 * math.sin(t * 0.7) + random.uniform(-0.03, 0.03)
        self.g_temp.target = 15 + (self.g_pressure.value - 1.0) * 20 + 5 * math.sin(t * 0.4) + random.uniform(-0.4, 0.4)
        self.g_load.target = 100 + 60 * math.sin(t * 0.5) + random.uniform(-3, 3)

        q = 100.0
        if self.g_pressure.value > 1.9:
            q -= (self.g_pressure.value - 1.9) * 40
        if self.g_temp.value > 35:
            q -= (self.g_temp.value - 35) * 1.5
        if abs(self.g_baro.value - 757) > 15:
            q -= abs(self.g_baro.value - 757 - 15) * 0.5
        if self.g_load.value > 160:
            q -= (self.g_load.value - 160) * 0.4
        self.g_quality.target = max(0, min(100, q + random.uniform(-1.5, 1.5)))

    # ---------- СОБЫТИЯ ----------
    def _check_events(self):
        checks = [
            ("pressure", self.g_pressure, "ДАВЛ",
             "Повышенное давление", "КРИТИЧЕСКОЕ давление!", "Давление в норме"),
            ("temp", self.g_temp, "ТЕМП",
             "Нагрев выше нормы", "ПЕРЕГРЕВ!", "Температура в норме"),
            ("load", self.g_load, "НАГР",
             "Высокая нагрузка", "Перегрузка!", "Нагрузка в норме"),
        ]
        for key, gauge, src, warn_msg, crit_msg, ok_msg in checks:
            s = gauge.status()
            if self.last_status.get(key) != s:
                self.last_status[key] = s
                if s == "WARN":
                    self._push_event(src, warn_msg, "WARN")
                elif s == "CRIT":
                    self._push_event(src, crit_msg, "ERROR")
                else:
                    self._push_event(src, ok_msg, "OK")

        if self.g_quality.value < 40 and self.last_status.get("q") != "low":
            self.last_status["q"] = "low"
            self._push_event("КАЧ", "Качество ниже нормы", "WARN")
        elif self.g_quality.value >= 60 and self.last_status.get("q") == "low":
            self.last_status["q"] = "ok"
            self._push_event("КАЧ", "Качество восстановлено", "OK")

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

        # тикаем все приборы
        for g in (self.g_pressure, self.g_temp, self.g_baro,
                  self.g_quality, self.g_load):
            g.tick()

        self._check_events()

        # полная перерисовка (простая, но надёжная)
        self._redraw_all()

        self.root.after(33, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()