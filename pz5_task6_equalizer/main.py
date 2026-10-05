"""
ОКФРС. Практика 5. Задание 6.
Эквалайзер / спектр-анализатор 32 полосы.
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
# СПЕКТР
# ============================================================
class Spectrum:
    def __init__(self, n=32):
        self.n = n
        self.values = [0.0] * n
        self.targets = [0.0] * n
        self.peaks = [0.0] * n
        self.peak_ages = [0.0] * n
        self.t = 0.0

    def tick(self, dt):
        self.t += dt
        t = self.t

        for i in range(self.n):
            freq = i / self.n
            tilt = 1.0 - freq * 0.7
            noise = random.uniform(0.4, 1.0)
            beat1 = 0.6 + 0.4 * math.sin(t * (2.5 + freq * 3) + i * 0.5)
            beat2 = 0.7 + 0.3 * math.sin(t * (1.8 + freq * 2) + i * 1.2)
            v = tilt * noise * beat1 * beat2
            v = max(0.05, min(1.0, v))
            self.targets[i] = v

        for i in range(self.n):
            diff = self.targets[i] - self.values[i]
            self.values[i] += diff * (0.35 if diff > 0 else 0.15)

            if self.values[i] > self.peaks[i]:
                self.peaks[i] = self.values[i]
                self.peak_ages[i] = 0.0
            else:
                self.peak_ages[i] += dt
                if self.peak_ages[i] > 0.5:
                    self.peaks[i] -= dt * 0.4
                    self.peaks[i] = max(self.values[i], self.peaks[i])

    def rms(self):
        return math.sqrt(sum(v * v for v in self.values) / self.n)

    def peak(self):
        return max(self.values)

    def mean(self):
        return sum(self.values) / self.n


# ============================================================
# ЭКВАЛАЙЗЕР — теперь без внешней карточки снаружи,
# чтобы не налезала на верх
# ============================================================
def band_color(k):
    if k < 0.5:
        return lerp(NEON_GREEN, NEON_AMBER, k / 0.5)
    else:
        return lerp(NEON_AMBER, NEON_RED, (k - 0.5) / 0.5)


def draw_equalizer(canvas, x, y, w, h, spec, mode="SPECTRUM"):
    # карточка (внутренние отступы)
    round_rect(canvas, x - 20, y - 55, x + w + 20, y + h + 55, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(x + 10, y - 32, anchor="w",
                       text="▸ SPECTRUM ANALYZER",
                       fill=NEON_CYAN, font=FONT_LABEL)
    canvas.create_text(x + w - 10, y - 32, anchor="e",
                       text=f"РЕЖИМ: {mode}",
                       fill=NEON_AMBER, font=FONT_LABEL_S)

    round_rect(canvas, x, y, x + w, y + h, 8,
               fill="#050810",
               outline=lerp(NEON_CYAN, BG_DEEP, 0.6), width=1)

    for i in range(1, 8):
        gy = y + i * h / 8
        canvas.create_line(x + 4, gy, x + w - 4, gy,
                           fill="#141a28", width=1)
        db = -6 * i
        canvas.create_text(x - 6, gy, anchor="e", text=f"{db}",
                           fill=TEXT_DIM, font=("Consolas", 7, "bold"))

    n = spec.n
    bar_gap = 3
    bar_w = (w - 8 - bar_gap * (n - 1)) / n
    base_y = y + h - 4

    for i in range(n):
        bx = x + 4 + i * (bar_w + bar_gap)
        by_top = base_y - spec.values[i] * (h - 8)

        n_seg = 12
        seg_h = (base_y - by_top) / n_seg
        for s in range(n_seg):
            sy0 = base_y - s * seg_h
            sy1 = base_y - (s + 1) * seg_h
            k = s / (n_seg - 1)
            col = band_color(k)
            canvas.create_rectangle(bx, sy1, bx + bar_w, sy0,
                                    fill=col, outline="")

        if spec.values[i] > 0.05:
            canvas.create_rectangle(bx, by_top, bx + bar_w, by_top + 3,
                                    fill="#ffffff", outline="")

        peak_y = base_y - spec.peaks[i] * (h - 8)
        if spec.peaks[i] > 0.03:
            canvas.create_rectangle(bx, peak_y - 2, bx + bar_w, peak_y,
                                    fill="#ffffff", outline="")

    canvas.create_line(x + 4, y + 4, x + w - 4, y + 4,
                       fill=lerp(NEON_CYAN, BG_DEEP, 0.5))

    for i in range(0, n + 1, 4):
        bx = x + 4 + i * (bar_w + bar_gap) - bar_gap / 2
        canvas.create_line(bx, base_y + 4, bx, base_y + 8,
                           fill=TEXT_DIM)
        freq = int(20 * (1000 ** (i / n)))
        canvas.create_text(bx, base_y + 18, text=f"{freq}",
                           fill=TEXT_DIM,
                           font=("Consolas", 7, "bold"))


# ============================================================
# СТЕРЕО-КАНАЛЫ
# ============================================================
def draw_stereo_channels(canvas, x, y, w, h, left, right):
    round_rect(canvas, x, y, x + w, y + h, 12,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(x + 16, y + 22, anchor="w",
                       text="▸ СТЕРЕО", fill=NEON_PINK,
                       font=FONT_LABEL)

    bar_x0 = x + 40
    bar_x1 = x + w - 60
    bar_y0 = y + 50
    bar_y1 = y + h - 20
    bar_cy = (bar_y0 + bar_y1) / 2
    half_h = (bar_y1 - bar_y0) / 2

    for sign, values, color, label in [(-1, left, NEON_GREEN, "L"),
                                        (1, right, NEON_CYAN, "R")]:
        bar_h_each = half_h / len(values)
        for i in range(len(values)):
            yy0 = bar_cy + sign * i * bar_h_each
            yy1 = bar_cy + sign * (i + 1) * bar_h_each
            k = values[i]
            if k < 0.05:
                continue
            xx0 = bar_x0
            xx1 = bar_x0 + (bar_x1 - bar_x0) * k
            col = lerp(color, BG_DEEP, 1 - k)
            canvas.create_rectangle(xx0, min(yy0, yy1) + 1,
                                    xx1, max(yy0, yy1) - 1,
                                    fill=col, outline="")

        canvas.create_text(x + w - 25, bar_cy + sign * 20,
                           text=label, fill=color,
                           font=("Segoe UI", 14, "bold"))

    canvas.create_line(bar_x0 - 5, bar_cy, bar_x1 + 5, bar_cy,
                       fill="#2a3340", width=1)


# ============================================================
# LED-ИНДИКАТОР
# ============================================================
def draw_level_meter(canvas, x, y, w, h, value, label="УРОВЕНЬ"):
    round_rect(canvas, x, y, x + w, y + h, 8,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(x + 12, y + 16, anchor="w",
                       text=label, fill=TEXT_DIM,
                       font=FONT_LABEL_S)

    n = 30
    seg_gap = 2
    seg_w = (w - 24 - seg_gap * (n - 1)) / n
    seg_h = h - 40
    base_y = y + 28

    for i in range(n):
        k = i / (n - 1)
        sx = x + 12 + i * (seg_w + seg_gap)
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

        round_rect(canvas, sx, base_y, sx + seg_w, base_y + seg_h,
                   2, fill=col)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("🎚 Equalizer · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        self.spec = Spectrum(32)
        self.stereo_l = [0.0] * 12
        self.stereo_r = [0.0] * 12
        self.mode = "SPECTRUM"
        self.modes = ["SPECTRUM", "AUDIO", "WAVE", "STEREO"]

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

        self.hit_zones = {}

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
        self.canvas.create_text(60, 40, text="🎚",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="EQUALIZER",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(280, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # ==== ВЕРХ: 4 стат-карточки ====
        STAT_Y = 85
        STAT_H = 55
        STAT_END = STAT_Y + STAT_H   # 140

        # ==== ЭКВАЛАЙЗЕР ====
        # начинаем через 75px после карточек, чтобы зазор был большим
        eq_x = 80
        eq_card_y = STAT_END + 30    # 170 — верх карточки эквалайзера
        eq_y = eq_card_y + 45        # 215 — верх полос
        eq_w = w - 160
        eq_h = h * 0.42

        # ==== ВНИЗУ: стерео + LED ====
        bottom_y = eq_y + eq_h + 35
        bottom_h = h - bottom_y - 110   # 110 — запас на кнопки

        # ==== РИСУЕМ ====
        # 1. Стат-карточки
        self._draw_stats(w, STAT_Y, STAT_H)

        # 2. Эквалайзер
        draw_equalizer(self.canvas, eq_x, eq_y, eq_w, eq_h,
                       self.spec, self.mode)

        # 3. Стерео слева
        st_x = 80
        st_w = (w - 200) * 0.6
        draw_stereo_channels(self.canvas, st_x, bottom_y, st_w, bottom_h,
                             self.stereo_l, self.stereo_r)

        # 4. LED-индикаторы справа
        lm_x = st_x + st_w + 40
        lm_w = w - lm_x - 80
        lm_h = (bottom_h - 20) / 2

        draw_level_meter(self.canvas, lm_x, bottom_y,
                         lm_w, lm_h, self.spec.mean(),
                         "СРЕДНИЙ УРОВЕНЬ")
        draw_level_meter(self.canvas, lm_x, bottom_y + lm_h + 20,
                         lm_w, lm_h, self.spec.peak(),
                         "ПИКОВЫЙ УРОВЕНЬ")

        # 5. Кнопки снизу
        self._draw_modes(w, h)

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _draw_stats(self, w, y, h_card):
        card_w = (w - 100) / 4
        self.hit_zones = {}

        rms = self.spec.rms()
        self._stat_card(60, y, card_w - 10, h_card,
                        "RMS", f"{rms*100:.1f} %", NEON_GREEN)

        pk = self.spec.peak()
        self._stat_card(60 + card_w, y, card_w - 10, h_card,
                        "ПИК", f"{pk*100:.1f} %", NEON_RED)

        mn = self.spec.mean()
        self._stat_card(60 + card_w * 2, y, card_w - 10, h_card,
                        "СРЕДНИЙ", f"{mn*100:.1f} %", NEON_CYAN)

        self._stat_card(60 + card_w * 3, y, card_w - 10, h_card,
                        "РЕЖИМ", self.mode, NEON_AMBER)

    def _stat_card(self, x, y, w, h, label, value, color):
        round_rect(self.canvas, x, y, x + w, y + h, 10,
                   fill=BG_GLASS, outline=BORDER, width=1)
        round_rect(self.canvas, x, y, x + 4, y + h, 2,
                   fill=color)
        self.canvas.create_text(x + 16, y + 16, anchor="w",
                                text=label, fill=TEXT_DIM,
                                font=FONT_LABEL_S)
        self.canvas.create_text(x + 16, y + 37, anchor="w",
                                text=value, fill=color,
                                font=FONT_VAL)

    def _draw_modes(self, w, h):
        modes = [
            ("SPECTRUM", NEON_CYAN),
            ("AUDIO", NEON_GREEN),
            ("WAVE", NEON_PINK),
            ("STEREO", NEON_PURP),
        ]
        bw = 180
        bh = 50
        gap = 20
        total = len(modes) * bw + (len(modes) - 1) * gap
        sx = (w - total) / 2
        y = h - 75

        for i, (name, col) in enumerate(modes):
            bx = sx + i * (bw + gap)
            active = (self.mode == name)

            if active:
                for k in range(4, 0, -1):
                    gcol = lerp(col, BG_DEEP, k / 5)
                    round_rect(self.canvas, bx - k, y - k,
                               bx + bw + k, y + bh + k, 10 + k,
                               outline=gcol, width=1)
                round_rect(self.canvas, bx, y, bx + bw, y + bh, 10,
                           fill=lerp(col, BG_DEEP, 0.7),
                           outline=col, width=3)
                self.canvas.create_text(bx + bw / 2, y + bh / 2,
                                        text=name, fill=col,
                                        font=("Segoe UI", 12, "bold"))
            else:
                round_rect(self.canvas, bx, y, bx + bw, y + bh, 10,
                           fill=BG_GLASS, outline=BORDER, width=1)
                self.canvas.create_text(bx + bw / 2, y + bh / 2,
                                        text=name, fill=TEXT_DIM,
                                        font=("Segoe UI", 12, "bold"))

            self.hit_zones[f"mode_{name}"] = (bx, y, bx + bw, y + bh)

    def _on_click(self, event):
        x, y = event.x, event.y
        for key, (x0, y0, x1, y1) in self.hit_zones.items():
            if x0 <= x <= x1 and y0 <= y <= y1 and key.startswith("mode_"):
                self.mode = key[5:]
                self._redraw_all()
                return

    def _simulate(self, dt):
        self.t += dt
        self.spec.tick(dt)

        for i in range(12):
            self.stereo_l[i] = max(0, min(1,
                self.spec.values[i] * 0.9 + random.uniform(-0.05, 0.05)))
            self.stereo_r[i] = max(0, min(1,
                self.spec.values[i + 16] * 0.9 + random.uniform(-0.05, 0.05)))

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self._simulate(dt)
        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()