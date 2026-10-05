"""
ОКФРС. Практика 5. Задание 10.
Анимация уровня жидкостей — 6 стилей круглых индикаторов.
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
# ДАННЫЕ ЖИДКОСТИ
# ============================================================
class LiquidData:
    def __init__(self, value=65.0, color=NEON_BLUE, bubbles=6):
        self.value = value
        self.target = value
        self.color = color
        self.phase = 0.0
        self.phase2 = 0.0
        self.bubbles = []
        for _ in range(bubbles):
            self.bubbles.append({
                "x_k": random.uniform(-0.6, 0.6),   # смещение по X
                "y": random.uniform(0.0, 1.0),      # позиция по Y
                "speed": random.uniform(0.15, 0.35),
                "size": random.uniform(2, 4),
            })
        self.pulse_t = 0.0

    def tick(self, dt):
        diff = self.target - self.value
        if abs(diff) > 0.01:
            self.value += diff * 0.1
        else:
            self.value = self.target
        self.phase += dt * 2.5
        self.phase2 += dt * 1.7
        self.pulse_t += dt

        # двигаем пузырьки вверх
        for b in self.bubbles:
            b["y"] -= b["speed"] * dt
            if b["y"] < 0:
                b["y"] = 1.0
                b["x_k"] = random.uniform(-0.6, 0.6)

    def k(self):
        return max(0.0, min(1.0, self.value / 100.0))


# ============================================================
# УНИВЕРСАЛЬНАЯ ОТРИСОВКА ЖИДКОСТИ
# ============================================================
def draw_liquid_circle(canvas, cx, cy, r, data,
                       body_color="#0a0d14",
                       ring_color=None,
                       ring_width=3,
                       wave_amp=5.0,
                       wave_count=2,
                       dark=True):
    """
    Рисует круг с жидкостью.
    """
    if ring_color is None:
        ring_color = data.color

    # тень
    canvas.create_oval(cx - r - 2, cy - r + 4, cx + r + 2, cy + r + 8,
                       fill="#000000", outline="")

    # корпус
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill=body_color,
                       outline=ring_color, width=ring_width)

    # маска — клип по кругу через вложенные овалы
    inner_r = r - ring_width - 1

    # уровень жидкости (снизу вверх)
    k = data.k()
    liquid_top = cy + inner_r - k * (2 * inner_r)

    # ─── волна ───
    # строим точки волны
    n_pts = 60
    wave_pts = []
    for i in range(n_pts + 1):
        # позиция по X
        t = i / n_pts
        px = cx - inner_r + t * 2 * inner_r
        # амплитуда волны уменьшается ближе к краям (чтобы не вылезала)
        edge_factor = math.sin(t * math.pi) ** 0.5
        # волны
        y_offset = 0
        y_offset += math.sin(data.phase + t * wave_count * 2 * math.pi) * wave_amp * edge_factor
        if wave_count >= 2:
            y_offset += math.sin(data.phase2 + t * wave_count * 1.5 * math.pi) * wave_amp * 0.5 * edge_factor
        py = liquid_top + y_offset
        wave_pts.append((px, py))

    # ─── клипаем волну по кругу ───
    # для каждой точки волны находим границы круга на этом X
    clipped = []
    for (px, py) in wave_pts:
        # на каком X, пересекает ли круг
        dx = px - cx
        if abs(dx) >= inner_r:
            continue
        # верх круга на этом X
        y_top = cy - math.sqrt(inner_r**2 - dx**2)
        y_bot = cy + math.sqrt(inner_r**2 - dx**2)
        # обрезаем py по границам
        py_c = max(min(py, y_bot), y_top)
        clipped.append((px, py_c))

    # ─── заливаем тело жидкости (полигон) ───
    if clipped and k > 0.005:
        # левый и правый край круга на уровне жидкости
        # дорисуем до дна круга
        left_x = cx - inner_r
        right_x = cx + inner_r
        # нижние точки — на дне круга
        bottom_poly = [(right_x, cy + inner_r), (left_x, cy + inner_r)]
        poly = clipped + bottom_poly

        flat = []
        for (px, py) in poly:
            flat.extend([px, py])

        canvas.create_polygon(flat,
                              fill=data.color,
                              outline="",
                              smooth=True)

    # ─── пузырьки ───
    if k > 0.02:
        for b in data.bubbles:
            # позиция пузырька
            bx = cx + b["x_k"] * inner_r * 0.8
            # Y: от дна до уровня жидкости
            by = cy + inner_r - b["y"] * (2 * inner_r) * k
            # обрезаем по кругу
            dx = bx - cx
            if abs(dx) >= inner_r:
                continue
            y_top = cy - math.sqrt(inner_r**2 - dx**2)
            y_bot = cy + math.sqrt(inner_r**2 - dx**2)
            if by < y_top or by > y_bot:
                continue
            # пузырёк
            canvas.create_oval(bx - b["size"], by - b["size"],
                               bx + b["size"], by + b["size"],
                               fill=lerp(data.color, "#ffffff", 0.5),
                               outline="")

    # ─── внутренний блик на жидкости ───
    if k > 0.05:
        # тонкая светлая полоска на верху жидкости
        for (px, py) in clipped[::3]:
            canvas.create_oval(px - 2, py - 1,
                               px + 2, py + 1,
                               fill=lerp(data.color, "#ffffff", 0.6),
                               outline="")

    # ─── обводка поверх ───
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=ring_color, width=ring_width)

    # ─── значение в центре ───
    txt_col = "#ffffff" if dark else "#1a1a2e"
    canvas.create_text(cx, cy - 8,
                       text=f"{data.value:.0f}",
                       fill=txt_col, font=FONT_BIG)
    canvas.create_text(cx, cy + 22,
                       text="%",
                       fill=lerp(txt_col, BG_DEEP, 0.4),
                       font=("Consolas", 14, "bold"))


# ============================================================
# 1-2. ТЁМНЫЕ КРУГИ (синий / зелёный)
# ============================================================
def draw_dark_liquid(canvas, cx, cy, r, data, label=""):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)
    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)
    draw_liquid_circle(canvas, cx, cy, r, data,
                       body_color="#0a0d14",
                       ring_color=data.color,
                       ring_width=4,
                       wave_amp=5.0,
                       wave_count=2,
                       dark=True)
    canvas.create_text(cx, cy + r + 35,
                       text=f"{data.value:.1f}%",
                       fill=data.color, font=FONT_VAL)


# ============================================================
# 3. СВЕТЛЫЙ С ГОЛУБОЙ ЖИДКОСТЬЮ
# ============================================================
def draw_light_liquid(canvas, cx, cy, r, data, label=""):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)
    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # светлый корпус
    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")

    inner_r = r - 4

    # светлая подложка
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#f5f7ff",
                       outline=data.color, width=3)

    # ─── клип жидкости ───
    k = data.k()
    liquid_top = cy + inner_r - k * (2 * inner_r)

    # волны
    n_pts = 60
    clipped = []
    for i in range(n_pts + 1):
        t = i / n_pts
        px = cx - inner_r + t * 2 * inner_r
        edge_factor = math.sin(t * math.pi) ** 0.5
        y_off = math.sin(data.phase + t * 2 * 2 * math.pi) * 5.0 * edge_factor
        y_off += math.sin(data.phase2 + t * 2 * 1.5 * math.pi) * 2.5 * edge_factor
        py = liquid_top + y_off
        dx = px - cx
        if abs(dx) >= inner_r:
            continue
        y_top = cy - math.sqrt(inner_r**2 - dx**2)
        y_bot = cy + math.sqrt(inner_r**2 - dx**2)
        py_c = max(min(py, y_bot), y_top)
        clipped.append((px, py_c))

    if clipped and k > 0.005:
        left_x = cx - inner_r
        right_x = cx + inner_r
        poly = clipped + [(right_x, cy + inner_r), (left_x, cy + inner_r)]
        flat = []
        for (px, py) in poly:
            flat.extend([px, py])
        canvas.create_polygon(flat, fill=data.color, outline="", smooth=True)

    # пузырьки
    if k > 0.02:
        for b in data.bubbles:
            bx = cx + b["x_k"] * inner_r * 0.8
            by = cy + inner_r - b["y"] * (2 * inner_r) * k
            dx = bx - cx
            if abs(dx) >= inner_r:
                continue
            y_top = cy - math.sqrt(inner_r**2 - dx**2)
            y_bot = cy + math.sqrt(inner_r**2 - dx**2)
            if by < y_top or by > y_bot:
                continue
            canvas.create_oval(bx - b["size"], by - b["size"],
                               bx + b["size"], by + b["size"],
                               fill=lerp(data.color, "#ffffff", 0.6),
                               outline="")

    # обводка
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=data.color, width=3)

    # значение в центре
    canvas.create_text(cx, cy - 8,
                       text=f"{data.value:.0f}",
                       fill="#1a1a2e", font=FONT_BIG)
    canvas.create_text(cx, cy + 22,
                       text="%",
                       fill="#5a6780",
                       font=("Consolas", 14, "bold"))

    canvas.create_text(cx, cy + r + 35,
                       text=f"{data.value:.1f}%",
                       fill=data.color, font=FONT_VAL)


# ============================================================
# 4-5. ПОЛНЫЙ ЦВЕТНОЙ КРУГ (красный / зелёный)
# ============================================================
def draw_full_colored(canvas, cx, cy, r, data, label=""):
    """Полный цветной круг с пульсацией."""
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)
    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # пульсация
    pulse = 0.5 + 0.5 * math.sin(data.pulse_t * 3)

    # ореол
    glow_r = r + 6 + int(pulse * 4)
    for k in range(4, 0, -1):
        canvas.create_oval(cx - glow_r - k, cy - glow_r - k,
                           cx + glow_r + k, cy + glow_r + k,
                           fill="", outline=lerp(data.color, BG_DEEP, k / 5),
                           width=1)

    # тело круга
    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill=data.color,
                       outline=lerp(data.color, "#ffffff", 0.4), width=3)

    # внутренний блик
    canvas.create_oval(cx - r * 0.7, cy - r * 0.75,
                       cx + r * 0.2, cy - r * 0.25,
                       fill=lerp(data.color, "#ffffff", 0.3),
                       outline="")

    # значение
    canvas.create_text(cx, cy - 8,
                       text=f"{data.value:.0f}",
                       fill="#ffffff", font=FONT_BIG)
    canvas.create_text(cx, cy + 22,
                       text="%",
                       fill=lerp("#ffffff", data.color, 0.3),
                       font=("Consolas", 14, "bold"))

    canvas.create_text(cx, cy + r + 35,
                       text=f"{data.value:.1f}%",
                       fill=data.color, font=FONT_VAL)


# ============================================================
# 6. ФИОЛЕТОВЫЙ С ГРАДИЕНТОМ
# ============================================================
def draw_gradient_liquid(canvas, cx, cy, r, data, label=""):
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 16,
               fill=BG_GLASS, outline=BORDER, width=1)
    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # корпус — толстое кольцо
    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0a0d14",
                       outline="#1a2030", width=10)

    # деления вокруг
    for i in range(72):
        a = math.radians(90 - i * 5)
        is_major = (i % 9 == 0)
        tick_len = 8 if is_major else 4
        col = TEXT_GLOW if is_major else "#3a4560"
        x1 = cx + (r + 2) * math.cos(a)
        y1 = cy - (r + 2) * math.sin(a)
        x2 = cx + (r + 2 + tick_len) * math.cos(a)
        y2 = cy - (r + 2 + tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col,
                           width=2 if is_major else 1)

    # внутренний радиус
    inner_r = r - 8

    # жидкость
    k = data.k()
    liquid_top = cy + inner_r - k * (2 * inner_r)

    n_pts = 60
    clipped = []
    for i in range(n_pts + 1):
        t = i / n_pts
        px = cx - inner_r + t * 2 * inner_r
        edge_factor = math.sin(t * math.pi) ** 0.5
        y_off = math.sin(data.phase + t * 3 * 2 * math.pi) * 6.0 * edge_factor
        y_off += math.sin(data.phase2 + t * 2 * 1.5 * math.pi) * 3.0 * edge_factor
        py = liquid_top + y_off
        dx = px - cx
        if abs(dx) >= inner_r:
            continue
        y_top = cy - math.sqrt(inner_r**2 - dx**2)
        y_bot = cy + math.sqrt(inner_r**2 - dx**2)
        py_c = max(min(py, y_bot), y_top)
        clipped.append((px, py_c))

    if clipped and k > 0.005:
        # градиент жидкости — от фиолетового к розовому
        left_x = cx - inner_r
        right_x = cx + inner_r
        poly = clipped + [(right_x, cy + inner_r), (left_x, cy + inner_r)]

        # основной цвет
        canvas.create_polygon(*sum([[px, py] for (px, py) in poly], []),
                              fill=data.color, outline="", smooth=True)

        # верхняя светлая кромка
        for (px, py) in clipped[::2]:
            canvas.create_oval(px - 2, py - 1,
                               px + 2, py + 1,
                               fill=lerp(data.color, "#ffffff", 0.5),
                               outline="")

    # пузырьки
    if k > 0.02:
        for b in data.bubbles:
            bx = cx + b["x_k"] * inner_r * 0.8
            by = cy + inner_r - b["y"] * (2 * inner_r) * k
            dx = bx - cx
            if abs(dx) >= inner_r:
                continue
            y_top = cy - math.sqrt(inner_r**2 - dx**2)
            y_bot = cy + math.sqrt(inner_r**2 - dx**2)
            if by < y_top or by > y_bot:
                continue
            canvas.create_oval(bx - b["size"], by - b["size"],
                               bx + b["size"], by + b["size"],
                               fill=lerp(data.color, "#ffffff", 0.6),
                               outline="")

    # обводка
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="", outline=data.color, width=2)

    # значение
    canvas.create_text(cx, cy - 8,
                       text=f"{data.value:.0f}",
                       fill="#ffffff", font=FONT_BIG)
    canvas.create_text(cx, cy + 22,
                       text="%",
                       fill=lerp("#ffffff", data.color, 0.4),
                       font=("Consolas", 14, "bold"))

    canvas.create_text(cx, cy + r + 35,
                       text=f"{data.value:.1f}%",
                       fill=data.color, font=FONT_VAL)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("💧 Liquid Levels · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # 6 жидкостей
        self.l_blue = LiquidData(65, NEON_BLUE, bubbles=8)
        self.l_green = LiquidData(65, NEON_GREEN, bubbles=8)
        self.l_light = LiquidData(65, NEON_CYAN, bubbles=6)
        self.l_red = LiquidData(100, NEON_RED, bubbles=0)
        self.l_full_green = LiquidData(100, NEON_GREEN, bubbles=0)
        self.l_purple = LiquidData(65, NEON_PURP, bubbles=10)

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
        self.canvas.create_text(60, 40, text="💧",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="LIQUID LEVELS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(320, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # 3 колонки × 2 ряда
        r = min(115, w * 0.062)
        col_x = [w * 0.17, w * 0.50, w * 0.83]
        row_y = [h * 0.30, h * 0.72]

        # РЯД 1
        draw_dark_liquid(self.canvas, col_x[0], row_y[0], r,
                         self.l_blue, "СИНЯЯ ЖИДКОСТЬ")
        draw_dark_liquid(self.canvas, col_x[1], row_y[0], r,
                         self.l_green, "ЗЕЛЁНАЯ ЖИДКОСТЬ")
        draw_light_liquid(self.canvas, col_x[2], row_y[0], r,
                          self.l_light, "СВЕТЛАЯ ЦИАН")

        # РЯД 2
        draw_full_colored(self.canvas, col_x[0], row_y[1], r,
                          self.l_red, "КРАСНАЯ ТРЕВОГА")
        draw_full_colored(self.canvas, col_x[1], row_y[1], r,
                          self.l_full_green, "ЗЕЛЁНАЯ НОРМА")
        draw_gradient_liquid(self.canvas, col_x[2], row_y[1], r,
                             self.l_purple, "ФИОЛЕТОВЫЙ ГРАДИЕНТ")

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _simulate(self, dt):
        self.t += dt
        t = self.t
        # уровни колеблются
        self.l_blue.target = 55 + 25 * math.sin(t * 0.4)
        self.l_green.target = 60 + 25 * math.sin(t * 0.5 + 1)
        self.l_light.target = 50 + 30 * math.sin(t * 0.45 + 2)
        # красный пульсирует 95-100
        self.l_red.target = 97 + 3 * math.sin(t * 1.5)
        # зелёный 100
        self.l_full_green.target = 100
        # фиолетовый
        self.l_purple.target = 55 + 35 * math.sin(t * 0.35 + 0.5)

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self._simulate(dt)
        for ld in (self.l_blue, self.l_green, self.l_light,
                   self.l_red, self.l_full_green, self.l_purple):
            ld.tick(dt)

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()