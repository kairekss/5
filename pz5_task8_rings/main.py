"""
ОКФРС. Практика 5. Задание 8.
Кольцевые прогресс-бары разных стилей — 6 вариантов.
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
class RingData:
    def __init__(self, value=50, color=NEON_CYAN):
        self.value = value
        self.target = value
        self.color = color

    def tick(self):
        diff = self.target - self.value
        if abs(diff) > 0.001:
            self.value += diff * 0.12
        else:
            self.value = self.target

    def k(self):
        return max(0.0, min(1.0, self.value / 100.0))


# ============================================================
# 1. НЕОНОВЫЙ С ТОЧКОЙ
# ============================================================
def draw_neon_dot_ring(canvas, cx, cy, r, data, label="НЕОН"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    ring_r = r - 15

    # фон-трек
    canvas.create_oval(cx - ring_r, cy - ring_r,
                       cx + ring_r, cy + ring_r,
                       fill="", outline="#1a2030", width=6)

    # заполненная дуга
    k = data.k()
    if k > 0.005:
        canvas.create_arc(cx - ring_r, cy - ring_r,
                          cx + ring_r, cy + ring_r,
                          start=90, extent=-360 * k,
                          style="arc",
                          outline=data.color, width=6)

    # светящаяся точка на конце
    a = math.radians(90 - k * 360)
    px = cx + ring_r * math.cos(a)
    py = cy - ring_r * math.sin(a)

    for kk in range(5, 0, -1):
        col = lerp(data.color, BG_DEEP, kk / 6)
        canvas.create_oval(px - 10 - kk, py - 10 - kk,
                           px + 10 + kk, py + 10 + kk,
                           fill="", outline=col, width=1)
    canvas.create_oval(px - 10, py - 10, px + 10, py + 10,
                       fill=data.color, outline="#ffffff", width=2)
    canvas.create_oval(px - 4, py - 4, px + 4, py + 4,
                       fill="#ffffff", outline="")

    # центр
    canvas.create_text(cx, cy - 8,
                       text=f"{data.value:.0f}",
                       fill="#ffffff", font=FONT_HUGE)
    canvas.create_text(cx, cy + 30,
                       text="%", fill=TEXT_DIM,
                       font=("Consolas", 14, "bold"))


# ============================================================
# 2. СВЕТЛЫЙ ЗЕЛЁНЫЙ
# ============================================================
def draw_light_green_ring(canvas, cx, cy, r, data, label="ЗЕЛЁНЫЙ"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # тень
    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")

    # светлый корпус
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#f5f7ff",
                       outline="#d0d5e5", width=3)
    canvas.create_oval(cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
                       fill="#ffffff", outline="#e8ebf5", width=1)

    ring_r = r - 24

    # фон-трек серый
    canvas.create_oval(cx - ring_r, cy - ring_r,
                       cx + ring_r, cy + ring_r,
                       fill="", outline="#e8ebf5", width=12)

    # заполнение зелёное
    k = data.k()
    if k > 0.005:
        canvas.create_arc(cx - ring_r, cy - ring_r,
                          cx + ring_r, cy + ring_r,
                          start=90, extent=-360 * k,
                          style="arc",
                          outline=data.color, width=12)

    # большая цифра
    canvas.create_text(cx, cy,
                       text=f"{data.value:.0f}",
                       fill=data.color, font=FONT_HUGE)

    # деления вокруг (маленькие)
    for i in range(36):
        a = math.radians(90 - i * 10)
        is_major = (i % 9 == 0)
        tick_len = 6 if is_major else 3
        col = "#8894b0" if is_major else "#c8cfe0"
        x1 = cx + (r - 12) * math.cos(a)
        y1 = cy - (r - 12) * math.sin(a)
        x2 = cx + (r - 12 - tick_len) * math.cos(a)
        y2 = cy - (r - 12 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col,
                           width=2 if is_major else 1)


# ============================================================
# 3. КОЛЬЦО ИЗ ДЕЛЕНИЙ
# ============================================================
def draw_tick_ring(canvas, cx, cy, r, data, label="ДЕЛЕНИЯ"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    ring_r = r - 20
    n_ticks = 60
    k_filled = data.k()

    # 60 чёрточек по кругу
    for i in range(n_ticks):
        a = math.radians(90 - i * (360 / n_ticks))
        k = i / n_ticks
        is_major = (i % 5 == 0)
        tick_len = 16 if is_major else 10
        w = 3 if is_major else 2

        if k < k_filled:
            col = data.color
        else:
            col = "#1a2030"

        x1 = cx + (ring_r - tick_len / 2) * math.cos(a)
        y1 = cy - (ring_r - tick_len / 2) * math.sin(a)
        x2 = cx + (ring_r + tick_len / 2) * math.cos(a)
        y2 = cy - (ring_r + tick_len / 2) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w,
                           capstyle="round")

    # центральный тёмный круг
    inner_r = ring_r - 25
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14",
                       outline="#1a2030", width=2)

    # цифра в центре
    canvas.create_text(cx, cy,
                       text=f"{data.value:.0f}",
                       fill=data.color, font=FONT_HUGE)

    # подпись
    canvas.create_text(cx, cy + r + 40,
                       text=f"{data.value:.0f}%",
                       fill=TEXT_GLOW, font=FONT_LABEL)


# ============================================================
# 4. ДВОЙНОЕ КОЛЬЦО
# ============================================================
def draw_double_ring(canvas, cx, cy, r, data, label="ДВОЙНОЕ"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # ВНЕШНЕЕ КОЛЬЦО — красное
    outer_r = r - 15
    canvas.create_oval(cx - outer_r, cy - outer_r,
                       cx + outer_r, cy + outer_r,
                       fill="", outline="#1a2030", width=8)

    k = data.k()
    if k > 0.005:
        canvas.create_arc(cx - outer_r, cy - outer_r,
                          cx + outer_r, cy + outer_r,
                          start=90, extent=-360 * k,
                          style="arc", outline=NEON_RED, width=8)

    # ВНУТРЕННЕЕ КОЛЬЦО — зелёное (инвертированное для красоты)
    inner_r = r - 35
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="", outline="#1a2030", width=6)

    # для красоты внутреннее кольцо заполняется наоборот
    k2 = 1 - k
    if k2 > 0.005:
        canvas.create_arc(cx - inner_r, cy - inner_r,
                          cx + inner_r, cy + inner_r,
                          start=90, extent=-360 * k2,
                          style="arc", outline=NEON_GREEN, width=6)

    # центр
    canvas.create_text(cx, cy,
                       text=f"{data.value:.0f}",
                       fill="#ffffff", font=FONT_HUGE)

    # подписи
    canvas.create_text(cx, cy + r - 5,
                       text=f"R {data.value:.0f}%   G {k2*100:.0f}%",
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# 5. СЕГМЕНТНОЕ КОЛЬЦО
# ============================================================
def draw_segment_ring(canvas, cx, cy, r, data, label="СЕГМЕНТЫ"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    n_seg = 24
    ring_r = r - 20
    seg_angle = 360 / n_seg
    k_filled = data.k()

    for i in range(n_seg):
        a_start = 90 - i * seg_angle + 3
        a_ext = -(seg_angle - 6)

        k = i / n_seg
        if k < k_filled:
            col = data.color
        else:
            col = "#1a2030"

        canvas.create_arc(cx - ring_r, cy - ring_r,
                          cx + ring_r, cy + ring_r,
                          start=a_start, extent=a_ext,
                          style="arc", outline=col, width=14)

    # центр
    canvas.create_text(cx, cy,
                       text=f"{data.value:.0f}",
                       fill=data.color, font=FONT_HUGE)
    canvas.create_text(cx, cy + 30,
                       text="%", fill=TEXT_DIM,
                       font=("Consolas", 14, "bold"))


# ============================================================
# 6. ТОЛСТОЕ ГРАДИЕНТНОЕ КОЛЬЦО
# ============================================================
def draw_gradient_ring(canvas, cx, cy, r, data, label="ГРАДИЕНТ"):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    ring_r = r - 20
    thickness = 20

    # фон-трек
    canvas.create_oval(cx - ring_r, cy - ring_r,
                       cx + ring_r, cy + ring_r,
                       fill="", outline="#0a0d14", width=thickness)

    # сегменты с градиентом (зелёный → жёлтый → красный)
    n_seg = 100
    k_filled = data.k()
    for i in range(n_seg):
        k0 = i / n_seg
        k1 = (i + 1) / n_seg
        if k0 >= k_filled:
            break
        # цвет по уровню
        if k0 < 0.5:
            col = lerp(NEON_GREEN, NEON_AMBER, k0 / 0.5)
        else:
            col = lerp(NEON_AMBER, NEON_RED, (k0 - 0.5) / 0.5)

        s = 90 - k0 * 360
        e = -360 * (k1 - k0)
        canvas.create_arc(cx - ring_r, cy - ring_r,
                          cx + ring_r, cy + ring_r,
                          start=s, extent=e,
                          style="arc", outline=col, width=thickness)

    # свечение по концу
    a = math.radians(90 - k_filled * 360)
    px = cx + ring_r * math.cos(a)
    py = cy - ring_r * math.sin(a)
    for kk in range(6, 0, -1):
        col = lerp(NEON_RED, BG_DEEP, kk / 7)
        canvas.create_oval(px - 12 - kk, py - 12 - kk,
                           px + 12 + kk, py + 12 + kk,
                           fill="", outline=col, width=1)

    # центр
    canvas.create_text(cx, cy - 10,
                       text=f"{data.value:.0f}",
                       fill="#ffffff", font=FONT_HUGE)
    canvas.create_text(cx, cy + 30,
                       text="°C", fill=TEXT_DIM,
                       font=("Consolas", 14, "bold"))


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("💍 Ring Progress · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # 6 колец
        self.r_neon = RingData(65, NEON_CYAN)
        self.r_green = RingData(65, NEON_GREEN)
        self.r_ticks = RingData(65, NEON_AMBER)
        self.r_double = RingData(65, NEON_RED)
        self.r_segment = RingData(65, NEON_PURP)
        self.r_gradient = RingData(65, NEON_GREEN)

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
        self.canvas.create_text(60, 40, text="💍",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="RING PROGRESS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(330, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # 3 колонки × 2 ряда
        r = min(120, w * 0.065)
        col_x = [w * 0.17, w * 0.50, w * 0.83]
        row_y = [h * 0.30, h * 0.72]

        # РЯД 1
        draw_neon_dot_ring(self.canvas, col_x[0], row_y[0], r,
                           self.r_neon, "НЕОН + ТОЧКА")
        draw_light_green_ring(self.canvas, col_x[1], row_y[0], r,
                              self.r_green, "СВЕТЛЫЙ ЗЕЛЁНЫЙ")
        draw_tick_ring(self.canvas, col_x[2], row_y[0], r,
                       self.r_ticks, "60 ДЕЛЕНИЙ")

        # РЯД 2
        draw_double_ring(self.canvas, col_x[0], row_y[1], r,
                         self.r_double, "ДВОЙНОЕ")
        draw_segment_ring(self.canvas, col_x[1], row_y[1], r,
                          self.r_segment, "24 СЕГМЕНТА")
        draw_gradient_ring(self.canvas, col_x[2], row_y[1], r,
                           self.r_gradient, "ГРАДИЕНТ")

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _simulate(self, dt):
        self.t += dt
        t = self.t
        self.r_neon.target = 50 + 40 * math.sin(t * 0.4) + random.uniform(-2, 2)
        self.r_green.target = 55 + 40 * math.sin(t * 0.5 + 1) + random.uniform(-2, 2)
        self.r_ticks.target = 45 + 45 * math.sin(t * 0.35 + 2) + random.uniform(-2, 2)
        self.r_double.target = 60 + 35 * math.sin(t * 0.45 + 0.5) + random.uniform(-2, 2)
        self.r_segment.target = 40 + 50 * math.sin(t * 0.55 + 1.5) + random.uniform(-2, 2)
        self.r_gradient.target = 50 + 45 * math.sin(t * 0.3 + 3) + random.uniform(-2, 2)

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self._simulate(dt)
        for r in (self.r_neon, self.r_green, self.r_ticks,
                  self.r_double, self.r_segment, self.r_gradient):
            r.tick()

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()