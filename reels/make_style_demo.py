"""Проба стиля «лекция в анимированной карточке»: 10 с, 9:16, без звука."""
import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 10.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "style_demo.mp4"
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
BG = (13, 16, 38)
CX0, CY0, CW, CH = 70, 360, 940, 1040          # карточка со сценой
SUBS = [(0.6, 4.6, "Sabr — mo‘minning\neng go‘zal fazilati"),
        (5.0, 9.6, "G‘azabini yutgan inson —\nhaqiqiy kuchli insondir")]
random.seed(3)

def font(w, s): return ImageFont.truetype(F.format(w), s)

def glow(size, color, radius, alpha):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((radius, radius, size[0] - radius, size[1] - radius), fill=color + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(radius / 2))

# ---------- статичный фон страницы ----------
page = Image.new("RGBA", (W, H), BG + (255,))
pd = ImageDraw.Draw(page)
for (x, y, r) in [(-200, 300, 700), (1200, 1500, 800)]:
    page.alpha_composite(glow((r, r), (60, 50, 140), r // 4, 60), (x - r // 2 + 200, y - r // 2))
# логотип-заглушка: полумесяц + название
logo = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); ld = ImageDraw.Draw(logo)
ld.ellipse((10, 10, 110, 110), fill=(186, 160, 255)); ld.ellipse((38, 2, 128, 92), fill=(0, 0, 0, 0))
page.alpha_composite(logo.resize((96, 96)), (300, 196))
pd.text((410, 200), "sizning nomingiz", font=font("Bold", 58), fill=(240, 240, 255))
pd.text((412, 266), "ma’ruzalar zamonaviy uslubda", font=font("Medium", 30), fill=(170, 160, 230))
pd.text((W // 2, 1790), "@sizning_sahifa", font=font("Medium", 34), fill=(150, 150, 190), anchor="mm")

# ---------- статичная часть сцены ----------
scene = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); sd = ImageDraw.Draw(scene)
for y in range(CH):                                    # стена: градиент
    t = y / CH
    sd.line((0, y, CW, y), fill=(int(52 - 20 * t), int(40 - 14 * t), int(96 - 30 * t)))
sd.rectangle((0, 760, CW, CH), fill=(44, 32, 74))       # пол
sd.rectangle((0, 752, CW, 762), fill=(64, 50, 104))
WX, WY, WW, WH_ = 600, 70, 270, 340                     # окно
sd.rounded_rectangle((WX - 14, WY - 14, WX + WW + 14, WY + WH_ + 14), 10, fill=(70, 56, 120))
sd.rectangle((WX, WY, WX + WW, WY + WH_), fill=(16, 18, 48))
sd.rectangle((70, 250, 330, 262), fill=(80, 64, 130))   # полка с книгами
for i, (h, c) in enumerate([(70, (150, 110, 200)), (52, (110, 90, 180)), (84, (180, 130, 170)), (60, (120, 120, 200))]):
    x = 90 + i * 46; sd.rectangle((x, 250 - h, x + 34, 250), fill=c)
sd.ellipse((140, 800, 800, 930), fill=(122, 58, 96))    # коврик
sd.ellipse((170, 815, 770, 915), outline=(170, 90, 130), width=6)
win_stars = [(WX + random.randint(10, WW - 10), WY + random.randint(10, WH_ - 10), random.random() * 6) for _ in range(14)]
room_dust = [(random.randint(0, CW), random.randint(0, CH), random.random() * 6, random.uniform(2, 4)) for _ in range(40)]
mask = Image.new("L", (CW, CH), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, CW - 1, CH - 1), 46, fill=255)

def person(d, cx, base, breath):
    """Сидящий человек в тюбетейке/такье с книгой, плоский стиль."""
    up = int(breath * 6)
    d.ellipse((cx - 150, base - 70, cx + 150, base + 40), fill=(52, 58, 110))                       # ноги
    d.polygon([(cx - 95, base - 10), (cx + 95, base - 10), (cx + 70, base - 250 - up), (cx - 70, base - 250 - up)], fill=(84, 96, 160))  # торс
    d.rectangle((cx - 8, base - 245 - up, cx + 8, base - 30), fill=(70, 80, 140))                     # шов халата
    d.rounded_rectangle((cx - 28, base - 290 - up, cx + 28, base - 240 - up), 10, fill=(206, 160, 130))  # шея
    d.ellipse((cx - 58, base - 390 - up, cx + 58, base - 270 - up), fill=(222, 176, 144))             # голова
    d.chord((cx - 60, base - 412 - up, cx + 60, base - 330 - up), 180, 360, fill=(245, 245, 250))     # такья
    d.ellipse((cx - 50, base - 318 - up, cx + 50, base - 262 - up), fill=(70, 60, 70))                # борода
    d.polygon([(cx - 110, base - 120), (cx, base - 100), (cx, base - 70), (cx - 110, base - 90)], fill=(240, 228, 200))  # книга
    d.polygon([(cx + 110, base - 120), (cx, base - 100), (cx, base - 70), (cx + 110, base - 90)], fill=(228, 214, 186))
    d.ellipse((cx - 128, base - 128, cx - 88, base - 88), fill=(222, 176, 144))                      # руки
    d.ellipse((cx + 88, base - 128, cx + 128, base - 88), fill=(222, 176, 144))

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
F_SUB = font("SemiBold", 56)

def frame(t):
    sc = scene.copy(); d = ImageDraw.Draw(sc)
    for (x, y, ph) in win_stars:                                       # звёзды в окне мерцают
        a = 0.5 + 0.5 * math.sin(t * 2.2 + ph); r = 2 + 2 * a
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 230, int(120 + 135 * a)))
    mx, my = WX + 190, WY + 90                                         # луна с пульсирующим ореолом
    g = glow((220, 220), (255, 240, 200), 60, int(70 + 30 * math.sin(t * 1.5)))
    sc.alpha_composite(g, (mx - 110, my - 110))
    d.ellipse((mx - 34, my - 34, mx + 34, my + 34), fill=(255, 248, 220))
    lamp = glow((520, 520), (255, 190, 110), 140, int(80 + 18 * math.sin(t * 3.1) + 8 * math.sin(t * 7.3)))
    sc.alpha_composite(lamp, (CW - 330, 330))                          # тёплый свет справа
    person(d, 470, 830, (math.sin(t * 1.6) + 1) / 2)
    for (x, y, ph, sp) in room_dust:                                   # плавающие пылинки
        yy = (y - t * sp * 12) % CH; a = 0.5 + 0.5 * math.sin(t * 1.3 + ph)
        d.ellipse((x - 2, yy - 2, x + 2, yy + 2), fill=(255, 255, 255, int(40 + 70 * a)))
    sc.putalpha(Image.composite(sc.getchannel("A"), Image.new("L", (CW, CH), 0), mask))
    img = page.copy()
    shadow = Image.new("RGBA", (CW + 80, CH + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((40, 50, CW + 40, CH + 50), 46, fill=(0, 0, 0, 150))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)), (CX0 - 40, CY0 - 40))
    img.alpha_composite(sc, (CX0, CY0))
    ImageDraw.Draw(img).rounded_rectangle((CX0, CY0, CX0 + CW - 1, CY0 + CH - 1), 46, outline=(120, 100, 200, 120), width=3)
    # прогресс под карточкой
    dd = ImageDraw.Draw(img); py = CY0 + CH + 50
    dd.rounded_rectangle((CX0 + 20, py, CX0 + CW - 20, py + 8), 4, fill=(255, 255, 255, 50))
    dd.rounded_rectangle((CX0 + 20, py, CX0 + 20 + int((CW - 40) * t / DUR), py + 8), 4, fill=(186, 160, 255))
    # субтитры
    for a, b, text in SUBS:
        if a <= t <= b:
            al = min(ease((t - a) / 0.4), ease((b - t) / 0.4))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            y = py + 90 + int((1 - al) * 20)
            ld.multiline_text((W // 2 + 3, y + 4), text, font=F_SUB, fill=(0, 0, 0, int(140 * al)), anchor="ma", align="center", spacing=16)
            ld.multiline_text((W // 2, y), text, font=F_SUB, fill=(255, 255, 255, int(255 * al)), anchor="ma", align="center", spacing=16)
            img.alpha_composite(lay)
    return img.convert("RGB")

p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                      "-c:a", "aac", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("done", OUT)
