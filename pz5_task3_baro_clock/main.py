"""
ОКФРС. Практика 5. Задание 3.
Барометр + Часы + Секундомер.
Премиум-стиль 2026.
"""
import tkinter as tk
import sys, os, math, random, time, datetime

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
FONT_BIG   = ("Consolas", 32, "bold")


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
# БАРОМЕТР
# ============================================================
class Barometer:
    def __init__(self, cx, cy, r):
        self.cx = cx
        self.cy = cy
        self.r = r
        self.value = 1013.0
        self.target = 1013.0
        self.history = []
        self.min_v = 980
        self.max_v = 1040
        self.a_start = math.radians(225)
        self.a_end = math.radians(-45)

    def _angle(self, v):
        k = (v - self.min_v) / (self.max_v - self.min_v)
        k = max(0.0, min(1.0, k))
        return self.a_start + (self.a_end - self.a_start) * k

    def tick(self, dt):
        diff = self.target - self.value
        if abs(diff) > 0.001:
            self.value += diff * 0.1
        else:
            self.value = self.target
        self.history.append(self.value)
        if len(self.history) > 200:
            self.history.pop(0)

    def forecast(self):
        if self.value < 995:
            return "ШТОРМ", NEON_RED
        elif self.value < 1005:
            return "ДОЖДЬ", NEON_BLUE
        elif self.value < 1015:
            return "ПЕРЕМЕННО", NEON_AMBER
        else:
            return "ЯСНО", NEON_GREEN


def draw_barometer(canvas, baro):
    cx, cy, r = baro.cx, baro.cy, baro.r

    # заголовок — НАД прибором
    canvas.create_text(cx, cy - r - 38, text="БАРОМЕТР",
                       fill=NEON_AMBER, font=FONT_LABEL)
    canvas.create_text(cx, cy - r - 20, text="гПа · hPa",
                       fill=TEXT_DIM, font=FONT_LABEL_S)

    # внешний обод
    canvas.create_oval(cx - r - 5, cy - r + 3, cx + r + 5, cy + r + 12,
                       fill="#000000", outline="")
    for i in range(10):
        k = i / 10
        rr = r - k * 8
        col = lerp("#2a3040", "#05070c", k)
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                           fill=col, outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=lerp(NEON_AMBER, "#000000", 0.6),
                       width=4)
    canvas.create_oval(cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
                       fill="", outline=lerp(NEON_AMBER, BG_DEEP, 0.5),
                       width=2)

    inner_r = r - 22
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14",
                       outline=lerp(NEON_AMBER, BG_DEEP, 0.4), width=1)

    # цветные зоны
    zones = [
        (980, 995, NEON_RED),
        (995, 1005, NEON_BLUE),
        (1005, 1015, NEON_AMBER),
        (1015, 1040, NEON_GREEN),
    ]
    for (z0, z1, col) in zones:
        a1 = math.degrees(baro._angle(z0))
        a2 = math.degrees(baro._angle(z1))
        canvas.create_arc(cx - inner_r + 3, cy - inner_r + 3,
                          cx + inner_r - 3, cy + inner_r - 3,
                          start=a2, extent=a1 - a2,
                          style="arc", outline=col, width=7)

    # деления
    n = 13
    for i in range(n):
        v = 980 + i * 5
        a = baro._angle(v)
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
            tx = cx + (inner_r - 26) * math.cos(a)
            ty = cy - (inner_r - 26) * math.sin(a)
            canvas.create_text(tx, ty, text=str(v),
                               fill=TEXT_GLOW,
                               font=("Consolas", 8, "bold"))

    # подписи зон — внутри
    canvas.create_text(cx - inner_r * 0.38, cy - inner_r * 0.38,
                       text="ШТОРМ", fill=NEON_RED,
                       font=("Segoe UI", 8, "bold"))
    canvas.create_text(cx + inner_r * 0.38, cy - inner_r * 0.38,
                       text="ЯСНО", fill=NEON_GREEN,
                       font=("Segoe UI", 8, "bold"))

    # стрелка
    a = baro._angle(baro.value)
    canvas.create_line(cx + 2, cy + 2,
                       cx + 2 + (inner_r - 16) * math.cos(a),
                       cy + 2 - (inner_r - 16) * math.sin(a),
                       fill="#000000", width=6)
    canvas.create_line(cx, cy,
                       cx + (inner_r - 16) * math.cos(a),
                       cy - (inner_r - 16) * math.sin(a),
                       fill=NEON_RED, width=4, capstyle="round")
    canvas.create_line(cx, cy,
                       cx - 20 * math.cos(a),
                       cy + 20 * math.sin(a),
                       fill=lerp(NEON_RED, "#000000", 0.4),
                       width=4, capstyle="round")

    # втулка
    canvas.create_oval(cx - 12, cy - 12, cx + 12, cy + 12,
                       fill="#1a1f2e",
                       outline=lerp(NEON_AMBER, BG_DEEP, 0.4), width=3)
    canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                       fill=NEON_AMBER, outline="")

    # значение — в нижней части циферблата
    canvas.create_text(cx, cy + inner_r - 40,
                       text=f"{baro.value:.1f}",
                       fill="#ffffff",
                       font=("Consolas", 22, "bold"))

    # прогноз — ниже обода
    fc_text, fc_col = baro.forecast()
    canvas.create_text(cx, cy + r + 30, text=fc_text,
                       fill=fc_col, font=FONT_VAL)
    canvas.create_text(cx, cy + r + 55, text="ПРОГНОЗ",
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# ЧАСЫ
# ============================================================
class Clock:
    def __init__(self, cx, cy, r):
        self.cx = cx
        self.cy = cy
        self.r = r
        self.hour = 0
        self.minute = 0
        self.second = 0.0
        self.tick_anim = 0.0

    def update(self):
        now = datetime.datetime.now()
        self.hour = now.hour % 12
        self.minute = now.minute
        self.second = now.second + now.microsecond / 1_000_000.0

    def tick(self, dt):
        self.tick_anim += dt
        self.update()


def draw_clock(canvas, clock):
    cx, cy, r = clock.cx, clock.cy, clock.r

    # заголовок над часами
    canvas.create_text(cx, cy - r - 25, text="ЧАСЫ",
                       fill=NEON_CYAN, font=FONT_LABEL)

    # внешний обод — красный
    canvas.create_oval(cx - r - 6, cy - r + 3, cx + r + 6, cy + r + 12,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4,
                       fill=lerp(NEON_RED, "#000000", 0.3),
                       outline=NEON_RED, width=3)
    canvas.create_oval(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2,
                       fill="#f8f8f0", outline="#d0d0c8", width=1)

    inner_r = r - 18
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#ffffff", outline="#e0e0d8", width=1)

    # цифры 1..12
    for i in range(1, 13):
        a = math.radians(90 - i * 30)
        tx = cx + (inner_r - 22) * math.cos(a)
        ty = cy - (inner_r - 22) * math.sin(a)
        canvas.create_text(tx, ty, text=str(i),
                           fill="#1a1a2e",
                           font=("Segoe UI", int(r * 0.13), "bold"))

    # деления минут
    for i in range(60):
        a = math.radians(90 - i * 6)
        is_hour = (i % 5 == 0)
        tick_len = 8 if is_hour else 4
        col = "#1a1a2e" if is_hour else "#a0a0b0"
        w = 2 if is_hour else 1
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w)

    # часовая
    h_angle = math.radians(90 - (clock.hour * 30 + clock.minute * 0.5))
    canvas.create_line(cx, cy,
                       cx + (inner_r * 0.5) * math.cos(h_angle),
                       cy - (inner_r * 0.5) * math.sin(h_angle),
                       fill="#1a1a2e", width=7, capstyle="round")

    # минутная
    m_angle = math.radians(90 - (clock.minute * 6 + clock.second * 0.1))
    canvas.create_line(cx, cy,
                       cx + (inner_r * 0.72) * math.cos(m_angle),
                       cy - (inner_r * 0.72) * math.sin(m_angle),
                       fill="#1a1a2e", width=4, capstyle="round")

    # секундная
    s_angle = math.radians(90 - clock.second * 6)
    canvas.create_line(cx, cy,
                       cx + (inner_r * 0.85) * math.cos(s_angle),
                       cy - (inner_r * 0.85) * math.sin(s_angle),
                       fill=NEON_RED, width=2, capstyle="round")
    canvas.create_line(cx, cy,
                       cx - 22 * math.cos(s_angle),
                       cy + 22 * math.sin(s_angle),
                       fill=NEON_RED, width=2, capstyle="round")

    # центр
    canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                       fill=NEON_RED, outline="#ffffff", width=2)
    canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                       fill="#ffffff", outline="")

    # цифровое время снизу
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    canvas.create_text(cx, cy + r + 35, text=now_str,
                       fill=NEON_CYAN, font=FONT_BIG)
    date_str = datetime.datetime.now().strftime("%d.%m.%Y")
    canvas.create_text(cx, cy + r + 60, text=date_str,
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# СЕКУНДОМЕР
# ============================================================
class Stopwatch:
    def __init__(self):
        self.running = False
        self.start_time = 0.0
        self.elapsed = 0.0
        self.laps = []

    def start_stop(self):
        if self.running:
            self.running = False
            self.elapsed = time.time() - self.start_time
        else:
            self.running = True
            self.start_time = time.time() - self.elapsed

    def reset(self):
        self.running = False
        self.elapsed = 0.0
        self.laps = []

    def lap(self):
        if self.elapsed > 0 or self.running:
            self.laps.append(self.current())
            if len(self.laps) > 5:
                self.laps.pop(0)

    def current(self):
        if self.running:
            return time.time() - self.start_time
        return self.elapsed


def draw_stopwatch(canvas, sw, x, y, w, h, buttons):
    round_rect(canvas, x, y, x + w, y + h, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(x + 20, y + 24, anchor="w",
                       text="▸ СЕКУНДОМЕР", fill=NEON_PURP,
                       font=FONT_LABEL)

    # круги — в правом верхнем углу
    if sw.laps:
        canvas.create_text(x + w - 20, y + 24, anchor="e",
                           text=f"КРУГИ: {len(sw.laps)}",
                           fill=TEXT_DIM, font=FONT_LABEL_S)
        for i, lap_t in enumerate(reversed(sw.laps)):
            lx = x + w - 20 - i * 90
            canvas.create_text(lx, y + 50, anchor="e",
                               text=f"#{len(sw.laps) - i} {lap_t:.2f}с",
                               fill=NEON_CYAN, font=FONT_MONO_S)

    # время — слева
    t = sw.current()
    mins = int(t // 60)
    secs = int(t % 60)
    ms = int((t * 100) % 100)
    time_str = f"{mins:02d}:{secs:02d}.{ms:02d}"

    canvas.create_text(x + 180, y + h / 2,
                       text=time_str,
                       fill="#ffffff",
                       font=("Consolas", 36, "bold"))

    # кнопки — справа
    btn_h = 50
    btn_w = 140
    btn_gap = 14
    total_btn_w = 3 * btn_w + 2 * btn_gap
    btn_x_start = x + w - 20 - total_btn_w
    btn_y = y + (h - btn_h) / 2

    for i, (label, col, key) in enumerate([
        ("СТАРТ" if not sw.running else "СТОП",
         NEON_GREEN if not sw.running else NEON_RED, "start"),
        ("КРУГ", NEON_CYAN, "lap"),
        ("СБРОС", NEON_AMBER, "reset"),
    ]):
        bx = btn_x_start + i * (btn_w + btn_gap)
        by = btn_y
        round_rect(canvas, bx, by, bx + btn_w, by + btn_h, 10,
                   fill=lerp(col, BG_DEEP, 0.8),
                   outline=col, width=2)
        canvas.create_text(bx + btn_w / 2, by + btn_h / 2,
                           text=label, fill=col,
                           font=("Segoe UI", 12, "bold"))
        buttons[key] = (bx, by, bx + btn_w, by + btn_h)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⏱ Barometer & Clock · Lab Series 2026")
        root.geometry("1400x900")
        root.minsize(1200, 800)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.baro = Barometer(0, 0, 160)
        self.clock = Clock(0, 0, 160)
        self.sw = Stopwatch()
        self.sw_buttons = {}

        self.W, self.H = 1400, 900

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

        self.baro.value = self.baro.target = 1013.0

        self.root.update_idletasks()
        self._redraw_all()
        self._animate()

    def _on_resize(self, event):
        self._redraw_all()

    def _layout(self, w, h):
        r = min(160, w * 0.11)
        self.baro.cx = w * 0.22
        self.baro.cy = h * 0.32
        self.baro.r = r

        self.clock.cx = w * 0.62
        self.clock.cy = h * 0.32
        self.clock.r = r

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
        self.canvas.create_text(60, 40, text="⏱",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="BAROMETER & CLOCK",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(420, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        self._layout(w, h)

        draw_barometer(self.canvas, self.baro)
        draw_clock(self.canvas, self.clock)

        self._draw_summary(w, h)

        # секундомер внизу
        sw_x = 60
        sw_h = 140
        sw_y = h - sw_h - 40
        sw_w = w - 120
        self.sw_buttons = {}
        draw_stopwatch(self.canvas, self.sw, sw_x, sw_y, sw_w, sw_h,
                       self.sw_buttons)

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _draw_summary(self, w, h):
        x = w - 380
        y = h * 0.15
        cw = 340
        ch = h * 0.45

        round_rect(self.canvas, x, y, x + cw, y + ch, 16,
                   fill=BG_GLASS, outline=BORDER, width=1)

        self.canvas.create_text(x + 20, y + 24, anchor="w",
                                text="▸ МЕТЕОСТАНЦИЯ", fill=NEON_AMBER,
                                font=FONT_LABEL)

        # давление
        self.canvas.create_text(x + 20, y + 70, anchor="w",
                                text="ДАВЛЕНИЕ", fill=TEXT_DIM,
                                font=FONT_LABEL_S)
        self.canvas.create_text(x + 20, y + 100, anchor="w",
                                text=f"{self.baro.value:.1f} гПа",
                                fill="#ffffff", font=FONT_VAL)

        # температура
        temp = 15 + (self.baro.value - 1013) * 0.3
        self.canvas.create_text(x + 20, y + 140, anchor="w",
                                text="ТЕМПЕРАТУРА", fill=TEXT_DIM,
                                font=FONT_LABEL_S)
        self.canvas.create_text(x + 20, y + 170, anchor="w",
                                text=f"{temp:.1f} °C",
                                fill=NEON_PINK, font=FONT_VAL)

        # влажность
        humid = 60 - (self.baro.value - 1013) * 1.5
        humid = max(20, min(95, humid))
        self.canvas.create_text(x + 20, y + 210, anchor="w",
                                text="ВЛАЖНОСТЬ", fill=TEXT_DIM,
                                font=FONT_LABEL_S)
        self.canvas.create_text(x + 20, y + 240, anchor="w",
                                text=f"{humid:.0f} %",
                                fill=NEON_BLUE, font=FONT_VAL)

        # прогноз
        fc_text, fc_col = self.baro.forecast()
        box_y = y + ch - 90
        round_rect(self.canvas, x + 20, box_y,
                   x + cw - 20, box_y + 70, 12,
                   fill=lerp(fc_col, BG_DEEP, 0.8),
                   outline=fc_col, width=2)
        self.canvas.create_text(x + cw / 2, box_y + 22,
                                text="ПРОГНОЗ", fill=fc_col,
                                font=FONT_LABEL_S)
        self.canvas.create_text(x + cw / 2, box_y + 48,
                                text=fc_text, fill=fc_col,
                                font=("Segoe UI", 18, "bold"))

    def _simulate(self, dt):
        self.t += dt
        t = self.t
        self.baro.target = 1013 + 20 * math.sin(t * 0.05) + 3 * math.sin(t * 0.4) + random.uniform(-0.3, 0.3)

    def _on_click(self, event):
        x, y = event.x, event.y
        for key, (x0, y0, x1, y1) in self.sw_buttons.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                if key == "start":
                    self.sw.start_stop()
                elif key == "reset":
                    self.sw.reset()
                elif key == "lap":
                    self.sw.lap()
                self._redraw_all()
                return

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self._simulate(dt)
        self.baro.tick(dt)
        self.clock.tick(dt)

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()