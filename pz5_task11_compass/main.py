"""
ОКФРС. Практика 5. Задание 11.
Компас с розой ветров + 3 мини-компаса + статистика.
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
# СОСТОЯНИЕ КОМПАСА
# ============================================================
class CompassState:
    def __init__(self, angle=0.0, auto_speed=0.3):
        self.angle = angle
        self.target = angle
        self.auto_speed = auto_speed
        self.auto = True
        self.pulse_t = 0.0

    def tick(self, dt):
        self.pulse_t += dt
        if self.auto:
            self.target = (self.target + self.auto_speed) % 360
        diff = self.target - self.angle
        while diff > 180: diff -= 360
        while diff < -180: diff += 360
        if abs(diff) > 0.1:
            self.angle += diff * 0.15
        else:
            self.angle = self.target
        self.angle %= 360

    def direction_name(self):
        a = self.angle
        names = [
            ("С", 0), ("ССВ", 22.5), ("СВ", 45), ("ВСВ", 67.5),
            ("В", 90), ("ВЮВ", 112.5), ("ЮВ", 135), ("ЮЮВ", 157.5),
            ("Ю", 180), ("ЮЮЗ", 202.5), ("ЮЗ", 225), ("ЗЮЗ", 247.5),
            ("З", 270), ("ЗСЗ", 292.5), ("СЗ", 315), ("ССЗ", 337.5),
        ]
        best = min(names, key=lambda x: min(abs(x[1] - a),
                                             360 - abs(x[1] - a)))
        return best[0]


# ============================================================
# БОЛЬШОЙ КОМПАС С РОЗОЙ ВЕТРОВ
# ============================================================
def draw_main_compass(canvas, cx, cy, r, st, label="НАВИГАЦИЯ"):
    # карточка
    round_rect(canvas, cx - r - 60, cy - r - 60,
               cx + r + 60, cy + r + 80, 18,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 40, text=label,
                       fill=TEXT_GLOW, font=FONT_LABEL)

    # === РОЗА ВЕТРОВ — лучи по кругу ===
    # тонкие лучи через каждые 22.5°
    for i in range(16):
        a = math.radians(90 - i * 22.5)
        is_main = (i % 4 == 0)
        is_med = (i % 2 == 0)
        line_len = r + 30 if is_main else (r + 15 if is_med else r + 5)
        col = lerp(NEON_CYAN, BG_DEEP, 0.7 if is_main else 0.85)
        canvas.create_line(cx, cy,
                           cx + line_len * math.cos(a),
                           cy - line_len * math.sin(a),
                           fill=col, width=2 if is_main else 1)

    # === ОБОД ===
    canvas.create_oval(cx - r - 2, cy - r + 3, cx + r + 2, cy + r + 6,
                       fill="#000000", outline="")

    # красное кольцо (внешнее)
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0f1520",
                       outline=NEON_RED, width=5)
    canvas.create_oval(cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8,
                       fill="", outline=lerp(NEON_RED, BG_DEEP, 0.4), width=1)

    inner_r = r - 22
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14",
                       outline="#1a2030", width=1)

    # === ДЕЛЕНИЯ ===
    for i in range(72):
        a = math.radians(90 - i * 5)
        is_major = (i % 9 == 0)
        is_medium = (i % 3 == 0)
        tick_len = 14 if is_major else (8 if is_medium else 4)
        col = TEXT_GLOW if is_major else ("#4a5360" if is_medium else "#2a3340")
        w = 2 if is_major else 1
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w)

    # === ЦИФРЫ 0..360 по кругу каждые 30° ===
    for i in range(12):
        a = math.radians(90 - i * 30)
        v = i * 30
        tx = cx + (inner_r - 42) * math.cos(a)
        ty = cy - (inner_r - 42) * math.sin(a)
        canvas.create_text(tx, ty, text=str(v),
                           fill=TEXT_GLOW,
                           font=("Consolas", 9, "bold"))

    # === N/S/E/W (крупно) ===
    dirs = [("N", 90, NEON_RED),
            ("E", 0, NEON_GREEN),
            ("S", 270, TEXT_GLOW),
            ("W", 180, TEXT_GLOW)]
    for letter, adeg, col in dirs:
        a = math.radians(adeg)
        # позиция у внешнего края внутреннего круга
        tx = cx + (inner_r - 8) * math.cos(a)
        ty = cy - (inner_r - 8) * math.sin(a)
        canvas.create_text(tx, ty, text=letter,
                           fill=col,
                           font=("Segoe UI", 22, "bold"))

    # === СТРЕЛКА (двухцветная: N — красная, S — белая) ===
    a = math.radians(90 - st.angle)

    # тень под стрелкой
    canvas.create_polygon(cx + 2, cy + 2,
                          cx + 2 + 16 * math.cos(a + math.pi/2),
                          cy + 2 - 16 * math.sin(a + math.pi/2),
                          cx + 2 + (inner_r - 30) * math.cos(a),
                          cy + 2 - (inner_r - 30) * math.sin(a),
                          cx + 2 + 16 * math.cos(a - math.pi/2),
                          cy + 2 - 16 * math.sin(a - math.pi/2),
                          fill="#000000", outline="")

    # север (красная половина)
    canvas.create_polygon(cx, cy,
                          cx + 16 * math.cos(a + math.pi/2),
                          cy - 16 * math.sin(a + math.pi/2),
                          cx + (inner_r - 30) * math.cos(a),
                          cy - (inner_r - 30) * math.sin(a),
                          cx + 16 * math.cos(a - math.pi/2),
                          cy - 16 * math.sin(a - math.pi/2),
                          fill=NEON_RED, outline="#000000", width=1)

    # юг (белая половина)
    a2 = a + math.pi
    canvas.create_polygon(cx, cy,
                          cx + 16 * math.cos(a2 + math.pi/2),
                          cy - 16 * math.sin(a2 + math.pi/2),
                          cx + (inner_r - 30) * math.cos(a2),
                          cy - (inner_r - 30) * math.sin(a2),
                          cx + 16 * math.cos(a2 - math.pi/2),
                          cy - 16 * math.sin(a2 - math.pi/2),
                          fill="#ffffff", outline="#000000", width=1)

    # центральная втулка
    canvas.create_oval(cx - 14, cy - 14, cx + 14, cy + 14,
                       fill="#1a1f2e",
                       outline=NEON_AMBER, width=3)
    canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                       fill=NEON_AMBER, outline="")

    # === БОЛЬШАЯ ЦИФРА АЗИМУТА ===
    canvas.create_text(cx, cy + r + 30,
                       text=f"{int(st.angle)}°",
                       fill=NEON_AMBER, font=FONT_HUGE)
    canvas.create_text(cx, cy + r + 65,
                       text=st.direction_name(),
                       fill=NEON_RED, font=FONT_BIG)


# ============================================================
# МИНИ-КОМПАС
# ============================================================
def draw_mini_compass(canvas, cx, cy, r, st, label, color):
    # карточка
    round_rect(canvas, cx - r - 25, cy - r - 45,
               cx + r + 25, cy + r + 65, 14,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(cx, cy - r - 25, text=label,
                       fill=color, font=FONT_LABEL)

    # обод
    canvas.create_oval(cx - r - 1, cy - r + 2, cx + r + 1, cy + r + 4,
                       fill="#000000", outline="")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill="#0f1520",
                       outline=color, width=3)

    inner_r = r - 14
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill="#0a0d14", outline="#1a2030", width=1)

    # деления
    for i in range(24):
        a = math.radians(90 - i * 15)
        is_major = (i % 6 == 0)
        tick_len = 8 if is_major else 4
        col = TEXT_GLOW if is_major else "#3a4560"
        x1 = cx + (inner_r - 2) * math.cos(a)
        y1 = cy - (inner_r - 2) * math.sin(a)
        x2 = cx + (inner_r - 2 - tick_len) * math.cos(a)
        y2 = cy - (inner_r - 2 - tick_len) * math.sin(a)
        canvas.create_line(x1, y1, x2, y2, fill=col,
                           width=2 if is_major else 1)

    # N/S/E/W мелко
    for letter, adeg, col in [("N", 90, NEON_RED),
                               ("E", 0, TEXT_GLOW),
                               ("S", 270, TEXT_GLOW),
                               ("W", 180, TEXT_GLOW)]:
        a = math.radians(adeg)
        tx = cx + (inner_r - 18) * math.cos(a)
        ty = cy - (inner_r - 18) * math.sin(a)
        canvas.create_text(tx, ty, text=letter,
                           fill=col,
                           font=("Segoe UI", 11, "bold"))

    # стрелка
    a = math.radians(90 - st.angle)
    canvas.create_polygon(cx, cy,
                          cx + 8 * math.cos(a + math.pi/2),
                          cy - 8 * math.sin(a + math.pi/2),
                          cx + (inner_r - 20) * math.cos(a),
                          cy - (inner_r - 20) * math.sin(a),
                          cx + 8 * math.cos(a - math.pi/2),
                          cy - 8 * math.sin(a - math.pi/2),
                          fill=color, outline="#000000")
    a2 = a + math.pi
    canvas.create_polygon(cx, cy,
                          cx + 8 * math.cos(a2 + math.pi/2),
                          cy - 8 * math.sin(a2 + math.pi/2),
                          cx + (inner_r - 20) * math.cos(a2),
                          cy - (inner_r - 20) * math.sin(a2),
                          cx + 8 * math.cos(a2 - math.pi/2),
                          cy - 8 * math.sin(a2 - math.pi/2),
                          fill="#ffffff", outline="#000000")

    # центр
    canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6,
                       fill="#1a1f2e", outline=color, width=2)

    # цифра
    canvas.create_text(cx, cy + r + 30,
                       text=f"{int(st.angle)}°",
                       fill=color, font=FONT_VAL)
    canvas.create_text(cx, cy + r + 52,
                       text=st.direction_name(),
                       fill=TEXT_DIM, font=FONT_LABEL_S)


# ============================================================
# ПАНЕЛЬ СТАТИСТИКИ
# ============================================================
def draw_stats_panel(canvas, x, y, w, h, st):
    round_rect(canvas, x, y, x + w, y + h, 14,
               fill=BG_GLASS, outline=BORDER, width=1)

    canvas.create_text(x + 20, y + 24, anchor="w",
                       text="▸ НАВИГАЦИОННАЯ СВОДКА",
                       fill=NEON_CYAN, font=FONT_LABEL)

    # азимут
    canvas.create_text(x + 20, y + 60, anchor="w",
                       text="АЗИМУТ", fill=TEXT_DIM,
                       font=FONT_LABEL_S)
    canvas.create_text(x + 20, y + 88, anchor="w",
                       text=f"{st.angle:.1f}°",
                       fill=NEON_AMBER, font=FONT_VAL)

    # направление
    canvas.create_text(x + w/2 + 10, y + 60, anchor="w",
                       text="НАПРАВЛЕНИЕ", fill=TEXT_DIM,
                       font=FONT_LABEL_S)
    canvas.create_text(x + w/2 + 10, y + 88, anchor="w",
                       text=st.direction_name(),
                       fill=NEON_RED, font=FONT_VAL)

    # точность
    canvas.create_text(x + 20, y + 120, anchor="w",
                       text="ТОЧНОСТЬ", fill=TEXT_DIM,
                       font=FONT_LABEL_S)
    canvas.create_text(x + 20, y + 148, anchor="w",
                       text="± 0.5°",
                       fill=NEON_GREEN, font=FONT_VAL)

    # статус
    canvas.create_text(x + w/2 + 10, y + 120, anchor="w",
                       text="СТАТУС", fill=TEXT_DIM,
                       font=FONT_LABEL_S)
    canvas.create_text(x + w/2 + 10, y + 148, anchor="w",
                       text="● АКТИВЕН",
                       fill=NEON_GREEN, font=FONT_VAL)


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("🧭 Compass · Lab Series 2026")
        root.geometry("1500x950")
        root.minsize(1300, 850)
        root.configure(bg=BG_DEEP)

        self.t = 0.0
        self.fps_time = time.time()
        self.fps = 60
        self.frame_count = 0

        # компасы
        self.st_main = CompassState(45.0, auto_speed=0.4)
        self.st_nav = CompassState(30.0, auto_speed=0.5)
        self.st_drone = CompassState(200.0, auto_speed=0.8)
        self.st_boat = CompassState(120.0, auto_speed=0.3)

        self.all_states = [self.st_main, self.st_nav,
                           self.st_drone, self.st_boat]

        self.W, self.H = 1500, 950

        self.canvas = tk.Canvas(root, bg=BG_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

        self.main_center = None

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
        self.canvas.create_text(60, 40, text="🧭",
                                fill=NEON_CYAN,
                                font=("Segoe UI Emoji", 26))
        self.canvas.create_text(100, 40, text="COMPASS",
                                fill=TEXT_MAIN, anchor="w",
                                font=("Segoe UI", 20, "bold"))
        self.canvas.create_text(260, 44, text="· LAB SERIES 2026",
                                fill=NEON_CYAN, anchor="w",
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_line(40, 70, w - 40, 70, fill=BORDER)

        # === ЛЕВАЯ ЧАСТЬ — БОЛЬШОЙ КОМПАС ===
        main_r = min(180, w * 0.11)
        main_cx = w * 0.24
        main_cy = h * 0.42
        self.main_center = (main_cx, main_cy, main_r)

        draw_main_compass(self.canvas, main_cx, main_cy, main_r,
                          self.st_main, "НАВИГАЦИЯ")

        # === ПРАВАЯ ЧАСТЬ ===
        # 3 мини-компаса в ряд
        right_x = w * 0.55
        mini_r = min(85, w * 0.045)
        mini_y = h * 0.28
        mini_gap = w * 0.15

        draw_mini_compass(self.canvas, right_x, mini_y, mini_r,
                          self.st_nav, "GPS НАВИГАЦИЯ", NEON_GREEN)

        draw_mini_compass(self.canvas, right_x + mini_gap, mini_y, mini_r,
                          self.st_drone, "ДРОН", NEON_PURP)

        draw_mini_compass(self.canvas, right_x + mini_gap * 2, mini_y, mini_r,
                          self.st_boat, "ЛОДКА", NEON_CYAN)

        # === СТАТИСТИКА ПОД МИНИ-КОМПАСАМИ ===
        stats_x = right_x - mini_r - 25
        stats_y = h * 0.52
        stats_w = mini_gap * 2 + mini_r * 2 + 50
        stats_h = h * 0.28

        draw_stats_panel(self.canvas, stats_x, stats_y,
                         stats_w, stats_h, self.st_main)

        # === ПОДСКАЗКА ===
        self.canvas.create_text(w / 2, h - 30,
                                text="Кликни по большому компасу — стрелка прыгнет на случайный азимут",
                                fill=TEXT_DIM, font=FONT_LABEL_S)

        # FPS
        self.canvas.create_text(w - 60, 37, text=f"{self.fps:>3} FPS",
                                fill=TEXT_DIM, font=FONT_MONO_S, anchor="e")

    def _on_click(self, event):
        if not self.main_center:
            return
        cx, cy, r = self.main_center
        dist = math.hypot(event.x - cx, event.y - cy)
        if dist <= r:
            # новый угол
            self.st_main.target = random.uniform(0, 360)
            self.st_main.auto = False
            # через 5 сек снова авто
            self.root.after(5000, lambda: setattr(self.st_main, "auto", True))

    def _animate(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = now

        dt = 0.033
        self.t += dt
        for st in self.all_states:
            st.tick(dt)

        self._redraw_all()
        self.root.after(50, self._animate)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()