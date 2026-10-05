"""
ОКФРС. Практика 5. Задание 13.
Интерфейс инструмента «Генератор сигналов» с максимальной анимацией.
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
FONT_LED   = ("Consolas", 30, "bold")


def clamp_ch(v):
    return max(0, min(255, int(v)))


def lerp(c1, c2, t):
    """Безопасный lerp — гарантирует корректный 6-значный hex."""
    t = max(0.0, min(1.0, float(t)))
    try:
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    except Exception:
        return c1 if c1.startswith("#") and len(c1) == 7 else "#808080"
    r = clamp_ch(r1 + (r2 - r1) * t)
    g = clamp_ch(g1 + (g2 - g1) * t)
    b = clamp_ch(b1 + (b2 - b1) * t)
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


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
# СИГНАЛ
# ============================================================
def signal_sample(kind, t):
    if kind == "sine":
        return math.sin(2 * math.pi * t)
    if kind == "square":
        return 1.0 if (t % 1) < 0.5 else -1.0
    if kind == "triangle":
        x = (t % 1) * 4
        if x < 1: return x
        if x < 3: return 2 - x
        return x - 4
    if kind == "sawtooth":
        return ((t % 1) * 2) - 1
    return 0


# ============================================================
# КРУТИЛКА
# ============================================================
class Knob:
    def __init__(self, cx, cy, r, label, min_v, max_v,
                 color=NEON_CYAN, value=None, unit="",
                 on_change=None, fmt=None):
        self.cx = cx
        self.cy = cy
        self.r = r
        self.label = label
        self.min_v = min_v
        self.max_v = max_v
        self.color = color
        self.value = value if value is not None else (min_v + max_v) / 2
        self.unit = unit
        self.on_change = on_change
        self.fmt = fmt or (lambda v: f"{v:.0f}")
        self.dragging = False
        self.drag_start_y = 0
        self.drag_start_v = 0
        self.tag = f"knob_{id(self)}"
        self.hover = False

    def _a_range(self):
        return math.radians(225), math.radians(-45)

    def _v_to_angle(self, v):
        k = (v - self.min_v) / (self.max_v - self.min_v)
        a0, a1 = self._a_range()
        return a0 + (a1 - a0) * max(0.0, min(1.0, k))

    def _y_to_v(self, dy):
        k = -dy / 200.0
        new_v = self.drag_start_v + k * (self.max_v - self.min_v)
        return max(self.min_v, min(self.max_v, new_v))

    def draw(self, canvas):
        canvas.delete(self.tag)
        cx, cy, r = self.cx, self.cy, self.r

        # ореол при hover
        if self.hover:
            for i in range(6, 0, -1):
                col = lerp(BG_DEEP, self.color, 0.15 * (7 - i) / 6)
                canvas.create_oval(cx - r - i * 2, cy - r - i * 2,
                                   cx + r + i * 2, cy + r + i * 2,
                                   fill="", outline=col, width=2,
                                   tags=self.tag)

        # деления
        a_start, a_end = self._a_range()
        n_ticks = 21
        for i in range(n_ticks):
            t = i / (n_ticks - 1)
            ang = a_start + (a_end - a_start) * t
            is_major = (i % 5 == 0)
            tl = 8 if is_major else 4
            x1 = cx + (r + 5) * math.cos(ang)
            y1 = cy - (r + 5) * math.sin(ang)
            x2 = cx + (r + 5 + tl) * math.cos(ang)
            y2 = cy - (r + 5 + tl) * math.sin(ang)
            col = TEXT_GLOW if is_major else TEXT_DIM
            canvas.create_line(x1, y1, x2, y2, fill=col,
                               width=2 if is_major else 1, tags=self.tag)

        # корпус
        canvas.create_oval(cx - r + 2, cy - r + 4, cx + r + 2, cy + r + 4,
                           fill="#000000", outline="", tags=self.tag)
        for i in range(6):
            k = i / 6
            rr = r - k * 8
            col = lerp("#2a3040", "#0a0d14", k)
            canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                               fill=col, outline="", tags=self.tag)
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill="", outline=lerp(self.color, "#000000", 0.5),
                           width=3, tags=self.tag)
        canvas.create_oval(cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3,
                           fill="", outline=self.color, width=2,
                           tags=self.tag)

        # риска
        ang = self._v_to_angle(self.value)
        rx = cx + (r - 14) * math.cos(ang)
        ry = cy - (r - 14) * math.sin(ang)
        canvas.create_line(cx, cy, rx, ry,
                           fill=self.color, width=4,
                           capstyle="round", tags=self.tag)
        canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                           fill=self.color, outline="", tags=self.tag)

        # дуга заполнения
        a_start_deg = math.degrees(a_start)
        a_val_deg = math.degrees(ang)
        canvas.create_arc(cx - r - 15, cy - r - 15,
                          cx + r + 15, cy + r + 15,
                          start=a_val_deg, extent=a_start_deg - a_val_deg,
                          style="arc", outline=self.color, width=3,
                          tags=self.tag)

        # подписи
        canvas.create_text(cx, cy + r + 28,
                           text=self.fmt(self.value),
                           fill=self.color, font=FONT_MONO,
                           tags=self.tag)
        canvas.create_text(cx, cy + r + 48,
                           text=self.label,
                           fill=TEXT_DIM, font=FONT_LABEL,
                           tags=self.tag)
        if self.unit:
            canvas.create_text(cx, cy + r + 65,
                               text=self.unit,
                               fill=TEXT_DIM, font=FONT_LABEL_S,
                               tags=self.tag)

        # привязки
        canvas.tag_bind(self.tag, "<ButtonPress-1>", self._press)
        canvas.tag_bind(self.tag, "<B1-Motion>", self._drag)
        canvas.tag_bind(self.tag, "<ButtonRelease-1>", self._release)
        canvas.tag_bind(self.tag, "<Enter>", self._enter)
        canvas.tag_bind(self.tag, "<Leave>", self._leave)
        canvas.tag_bind(self.tag, "<MouseWheel>", self._wheel)

    def _press(self, e):
        self.dragging = True
        self.drag_start_y = e.y
        self.drag_start_v = self.value

    def _drag(self, e):
        if not self.dragging:
            return
        new_v = self._y_to_v(e.y - self.drag_start_y)
        if abs(new_v - self.value) > 0.001:
            self.value = new_v
            if self.on_change:
                self.on_change(self.value)

    def _release(self, e):
        self.dragging = False

    def _enter(self, e):
        self.hover = True

    def _leave(self, e):
        self.hover = False

    def _wheel(self, e):
        delta = 1 if e.delta > 0 else -1
        step = (self.max_v - self.min_v) / 50
        self.value = max(self.min_v, min(self.max_v, self.value + delta * step))
        if self.on_change:
            self.on_change(self.value)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("⚡ Signal Generator · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0
        self.phase = 0.0

        # параметры
        self.freq1 = 1000.0
        self.amp1 = 20.0
        self.freq2 = 1000.0
        self.amp2 = 20.0
        self.wave = "sine"
        self.mode = "ГНЧ"
        self.running = True

        # крутилки
        self.knobs = []
        self.knobs_built = False

        # зоны кликов
        self.wave_zones = {}
        self.mode_zones = {}
        self.btn_zones = {}

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

        self.root.update_idletasks()
        self._redraw_all()
        self._animate()

    def _on_resize(self, event):
        self._redraw_all()

    # ---------- ФОН ----------
    def _draw_bg(self, w, h):
        for i in range(40):
            y0 = int(i * h / 40)
            y1 = int((i + 1) * h / 40)
            col = lerp(BG_DEEP, "#0a0e18", i / 40)
            self.canvas.create_rectangle(0, y0, w, y1, fill=col, outline="")
        for x in range(0, w, 60):
            self.canvas.create_line(x, 0, x, h, fill="#0d1220")
        for y in range(0, h, 60):
            self.canvas.create_line(0, y, w, y, fill="#0d1220")

    # ---------- ЗАГОЛОВОК ----------
    def _draw_header(self, w):
        self.canvas.create_text(60, 40, text="⚡",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="SIGNAL GENERATOR",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(360, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))

        scol = NEON_GREEN if self.running else NEON_RED
        stext = "ACTIVE" if self.running else "STANDBY"
        self.canvas.create_oval(w - 200, 30, w - 186, 44,
                                fill=scol, outline="")
        self.canvas.create_text(w - 175, 37, anchor="w",
                                text=stext, fill=scol, font=FONT_LABEL)

        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

    # ---------- LED-ДИСПЛЕИ ----------
    def _draw_led_displays(self, w):
        y = 90
        ch = 100
        cw = (w - 100) / 4
        data = [
            ("ГЛАВНЫЙ КАНАЛ", f"{self.freq1:>7.1f} Гц", "1·F", self.freq1),
            ("АМПЛИТУДА",     f"{self.amp1:>7.1f} мВ",  "1·A", self.amp1),
            ("ПРИБЛИЖ. КАНАЛ", f"{self.freq2:>7.1f} Гц", "2·F", self.freq2),
            ("АМПЛИТУДА",     f"{self.amp2:>7.1f} мВ",  "2·A", self.amp2),
        ]
        for i, (label, value, code, raw) in enumerate(data):
            x = 60 + i * cw
            round_rect(self.canvas, x, y, x + cw - 15, y + ch, 12,
                       fill=BG_METAL, outline=BORDER, width=1)
            self.canvas.create_text(x + 15, y + 20, anchor="w",
                                    text=label, fill=TEXT_DIM,
                                    font=FONT_LABEL_S)
            self.canvas.create_text(x + cw - 30, y + 20, anchor="e",
                                    text=code, fill=NEON_GREEN,
                                    font=FONT_MONO_S)
            self.canvas.create_text(x + 15, y + 55, anchor="w",
                                    text=value, fill=NEON_GREEN,
                                    font=("Consolas", 22, "bold"))
            bar_x0 = x + 15
            bar_x1 = x + cw - 30
            bar_y = y + ch - 20
            round_rect(self.canvas, bar_x0, bar_y, bar_x1, bar_y + 6, 3,
                       fill="#0a0d14", outline="")
            k = min(1.0, raw / 2000.0)
            if k > 0.02:
                round_rect(self.canvas, bar_x0, bar_y,
                           bar_x0 + (bar_x1 - bar_x0) * k,
                           bar_y + 6, 3, fill=NEON_GREEN)

    # ---------- ОСЦИЛЛОГРАФ ----------
    def _draw_oscilloscope(self, w):
        sx = 60
        sy = 220
        sw = w - 120
        sh = 220

        round_rect(self.canvas, sx, sy, sx + sw, sy + sh, 14,
                   fill="#050710", outline=BORDER, width=2)

        for gx in range(int(sx) + 30, int(sx + sw), 30):
            self.canvas.create_line(gx, sy + 15, gx, sy + sh - 15,
                                    fill="#0d1220", width=1)
        for gy in range(int(sy) + 30, int(sy + sh), 30):
            self.canvas.create_line(sx + 15, gy, sx + sw - 15, gy,
                                    fill="#0d1220", width=1)

        mid_y = sy + sh / 2
        self.canvas.create_line(sx + 15, mid_y, sx + sw - 15, mid_y,
                                fill="#1a2540", width=1)

        self.canvas.create_text(sx + 25, sy + 20, anchor="w",
                                text="OSC · LIVE", fill=NEON_GREEN,
                                font=FONT_LABEL)
        self.canvas.create_text(sx + sw - 25, sy + 20, anchor="e",
                                text=self.wave.upper(),
                                fill=NEON_CYAN, font=FONT_LABEL)

        n_pts = 400
        points = []
        px0 = sx + 20
        px1 = sx + sw - 20
        amp_px = (sh / 2 - 30) * min(1.0, self.amp1 / 100.0 + 0.3)
        amp_px = min(amp_px, sh / 2 - 30)
        freq_disp = 2 + (self.freq1 / 200.0)

        for i in range(n_pts):
            t = i / (n_pts - 1)
            v = signal_sample(self.wave, t * freq_disp + self.phase)
            x = px0 + (px1 - px0) * t
            y = mid_y - v * amp_px
            points.extend([x, y])

        if len(points) >= 4:
            self.canvas.create_line(*points,
                                    fill=lerp(NEON_GREEN, BG_DEEP, 0.7),
                                    width=6, smooth=True)
            self.canvas.create_line(*points,
                                    fill=NEON_GREEN,
                                    width=2, smooth=True)

    # ---------- ПАНЕЛЬ УПРАВЛЕНИЯ ----------
    def _draw_controls(self, w, h):
        left_x = 60
        y = h - 480

        # === Режим ГНЧ / ГВЧ ===
        round_rect(self.canvas, left_x, y, left_x + 250, y + 140, 14,
                   fill=BG_GLASS, outline=BORDER)
        self.canvas.create_text(left_x + 20, y + 25, anchor="w",
                                text="РЕЖИМ ГЕНЕРАТОРА", fill=TEXT_DIM,
                                font=FONT_LABEL)

        self.mode_zones = {}
        for i, (name, col) in enumerate([("ГНЧ", NEON_GREEN),
                                          ("ГВЧ", NEON_CYAN)]):
            bx = left_x + 20 + i * 115
            by = y + 50
            bw, bh = 105, 70
            active = (self.mode == name)
            if active:
                for k in range(4, 0, -1):
                    gcol = lerp(col, BG_DEEP, k / 5)
                    round_rect(self.canvas, bx - k, by - k,
                               bx + bw + k, by + bh + k, 10 + k,
                               outline=gcol, width=1)
                round_rect(self.canvas, bx, by, bx + bw, by + bh, 10,
                           fill=lerp(col, BG_DEEP, 0.7),
                           outline=col, width=3)
                self.canvas.create_text(bx + bw/2, by + bh/2,
                                        text=name, fill=col,
                                        font=("Consolas", 18, "bold"))
            else:
                round_rect(self.canvas, bx, by, bx + bw, by + bh, 10,
                           fill=BG_METAL, outline=BORDER, width=1)
                self.canvas.create_text(bx + bw/2, by + bh/2,
                                        text=name, fill=TEXT_DIM,
                                        font=("Consolas", 18, "bold"))
            self.mode_zones[name] = (bx, by, bx + bw, by + bh)

        # === Форма сигнала ===
        wave_y = y + 160
        round_rect(self.canvas, left_x, wave_y, left_x + 250,
                   wave_y + 270, 14,
                   fill=BG_GLASS, outline=BORDER)
        self.canvas.create_text(left_x + 20, wave_y + 25, anchor="w",
                                text="ФОРМА СИГНАЛА", fill=TEXT_DIM,
                                font=FONT_LABEL)

        self.wave_zones = {}
        waves = [
            ("sine",     "∿  СИНУС",       NEON_GREEN),
            ("square",   "⊓  КВАДРАТ",     NEON_AMBER),
            ("triangle", "△  ТРЕУГОЛЬНИК", NEON_PINK),
            ("sawtooth", "◺  ПИЛА",        NEON_PURP),
        ]
        for i, (key, label, col) in enumerate(waves):
            bx = left_x + 20
            by = wave_y + 50 + i * 52
            bw, bh = 210, 42
            active = (self.wave == key)
            if active:
                round_rect(self.canvas, bx, by, bx + bw, by + bh, 8,
                           fill=lerp(col, BG_DEEP, 0.75),
                           outline=col, width=2)
                self.canvas.create_text(bx + 15, by + bh/2, anchor="w",
                                        text=label, fill=col,
                                        font=FONT_LABEL)
            else:
                round_rect(self.canvas, bx, by, bx + bw, by + bh, 8,
                           fill=BG_METAL, outline=BORDER, width=1)
                self.canvas.create_text(bx + 15, by + bh/2, anchor="w",
                                        text=label, fill=TEXT_DIM,
                                        font=FONT_LABEL)
            self.wave_zones[key] = (bx, by, bx + bw, by + bh)

        # === 4 крутилки справа ===
        right_x = w - 60
        kw = 200
        total_kw = kw * 4
        kstart_x = right_x - total_kw
        ky = h - 200

        if not self.knobs_built:
            self.knobs = [
                Knob(kstart_x + kw*0.5, ky, 55, "ГЛАВНЫЙ", 0, 2000,
                     NEON_GREEN, value=self.freq1, unit="Гц",
                     on_change=self._set_freq1,
                     fmt=lambda v: f"{v:.0f}"),
                Knob(kstart_x + kw*1.5, ky, 55, "АМПЛИТУДА", 0, 100,
                     NEON_GREEN, value=self.amp1, unit="мВ",
                     on_change=self._set_amp1,
                     fmt=lambda v: f"{v:.0f}"),
                Knob(kstart_x + kw*2.5, ky, 55, "ПРИБЛИЖ.", 0, 2000,
                     NEON_CYAN, value=self.freq2, unit="Гц",
                     on_change=self._set_freq2,
                     fmt=lambda v: f"{v:.0f}"),
                Knob(kstart_x + kw*3.5, ky, 55, "АМПЛИТУДА", 0, 100,
                     NEON_CYAN, value=self.amp2, unit="мВ",
                     on_change=self._set_amp2,
                     fmt=lambda v: f"{v:.0f}"),
            ]
            self.knobs_built = True
        else:
            for i, k in enumerate(self.knobs):
                k.cx = kstart_x + (i + 0.5) * kw
                k.cy = ky

        for k in self.knobs:
            try:
                k.draw(self.canvas)
            except Exception as ex:
                print(f"[knob] {ex}")

        # === Кнопки ПУСК / СТОП / СЛУЧАЙНО ===
        btn_y = h - 60
        bw = 220
        bh = 44
        gap = 20
        total = bw * 3 + gap * 2
        bx_start = (w - total) / 2

        self.btn_zones = {}

        self._draw_big_btn(bx_start, btn_y, bw, bh,
                           "▶  ПУСК", NEON_GREEN,
                           self._on_start, "start",
                           active=self.running)
        self._draw_big_btn(bx_start + bw + gap, btn_y, bw, bh,
                           "■  СТОП", NEON_RED,
                           self._on_stop, "stop",
                           active=not self.running)
        self._draw_big_btn(bx_start + (bw + gap) * 2, btn_y, bw, bh,
                           "⟳  СЛУЧАЙНО", NEON_PURP,
                           self._on_random, "random",
                           active=False)

    def _draw_big_btn(self, x, y, w, h, text, color, command, key, active):
        if active:
            for k in range(4, 0, -1):
                gcol = lerp(color, BG_DEEP, k / 5)
                round_rect(self.canvas, x - k, y - k, x + w + k, y + h + k,
                           10 + k, outline=gcol, width=1)
            round_rect(self.canvas, x, y, x + w, y + h, 10,
                       fill=lerp(color, BG_DEEP, 0.65),
                       outline=color, width=3)
        else:
            round_rect(self.canvas, x, y, x + w, y + h, 10,
                       fill=BG_METAL, outline=BORDER, width=1)
        self.canvas.create_text(x + w / 2, y + h / 2,
                                text=text, fill=color,
                                font=("Segoe UI", 12, "bold"))
        self.btn_zones[key] = (x, y, x + w, y + h)

    # ---------- SETTERS ----------
    def _set_freq1(self, v): self.freq1 = v
    def _set_amp1(self, v):  self.amp1 = v
    def _set_freq2(self, v): self.freq2 = v
    def _set_amp2(self, v):  self.amp2 = v

    def _on_start(self):
        self.running = True

    def _on_stop(self):
        self.running = False

    def _on_random(self):
        self.freq1 = random.randint(100, 1800)
        self.amp1 = random.randint(5, 95)
        self.freq2 = random.randint(100, 1800)
        self.amp2 = random.randint(5, 95)
        if self.knobs:
            self.knobs[0].value = self.freq1
            self.knobs[1].value = self.amp1
            self.knobs[2].value = self.freq2
            self.knobs[3].value = self.amp2

    # ---------- КЛИКИ ----------
    def _on_click(self, event):
        x, y = event.x, event.y

        for name, (x0, y0, x1, y1) in self.mode_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.mode = name
                return

        for key, (x0, y0, x1, y1) in self.wave_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.wave = key
                return

        for key, (x0, y0, x1, y1) in self.btn_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                if key == "start":
                    self._on_start()
                elif key == "stop":
                    self._on_stop()
                elif key == "random":
                    self._on_random()
                return

    # ---------- ПЕРЕРИСОВКА ----------
    def _redraw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = self.W, self.H
        self.W, self.H = w, h

        self._draw_bg(w, h)
        self._draw_header(w)
        self._draw_led_displays(w)
        self._draw_oscilloscope(w)
        self._draw_controls(w, h)

    # ---------- АНИМАЦИЯ ----------
    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        if self.running:
            self.phase += (self.freq1 / 20000.0) * 0.5
            self.phase %= 1.0

        self._redraw_all()
        self.root.after(33, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()