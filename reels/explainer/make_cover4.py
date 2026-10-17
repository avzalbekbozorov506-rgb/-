"""Обложка «Две смены»."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import subprocess
subprocess.run(["ffmpeg","-v","error","-y","-ss","1.5","-i","/home/user/-/reels/hq/two_shifts_hq.mp4","-frames:v","1","/tmp/ts_bg.png"],check=True)
im = Image.open("/tmp/ts_bg.png").convert("RGB"); im = ImageEnhance.Brightness(im).enhance(.85)
d = ImageDraw.Draw(im)
def F(s): return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", s)
def txt(y, s, fs, col, sh=(0,0,0)):
    f = F(fs); w = d.textlength(s, font=f); x = (1080 - w) / 2; d.text((x+5, y+6), s, font=f, fill=sh); d.text((x, y), s, font=f, fill=col)
d.rectangle([0, 280, 1080, 640], fill=(14, 8, 5)); txt(310, "ОБА РАБОТАЮТ", 98, (255,255,255)); txt(440, "С 9 ДО 6.", 98, (255,200,100)); txt(570, "А ВЕЧЕР — У КОГО?", 60, (200,210,230))
d.rectangle([60, 1400, 1020, 1560], fill=(210, 60, 40)); txt(1425, "ДВЕ СМЕНЫ", 100, (255,255,255), (90,10,0))
im.save("/home/user/-/reels/covers/two_shifts_click.jpg", quality=93)
