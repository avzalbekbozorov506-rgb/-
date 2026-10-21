"""Общие помощники недели «Кристи»: карточки с текстом."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dopamine_1 import bg, text_c, sans, ease, cta_card, GOLD, WHITE, GREY, RED
from PIL import Image, ImageDraw

W, H = 1080, 1920
def words_card(*lines, size=68, step=130, y0=860):
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); n = len(lines)
        for i, (t, col) in enumerate(lines):
            k = ease((lt - i * 0.9) / 0.5)
            text_c(d, (W // 2, y0 + (i - (n - 1) / 2) * step), t, sans("Black", size), col + (int(255 * k),))
        return im
    return f

def clue_card(who, said, clue1, clue2=None):
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.6); k2 = ease((lt - 1.4) / 0.6)
        text_c(d, (W // 2, 600), who, sans("Black", 96), GOLD + (int(255 * k),))
        text_c(d, (W // 2, 790), said, sans("Black", 56), WHITE + (int(255 * k),))
        text_c(d, (W // 2, 960), clue1, sans("Black", 52), GREY + (int(255 * k2),))
        if clue2: text_c(d, (W // 2, 1040), clue2, sans("Black", 52), GREY + (int(255 * k2),))
        return im
    return f
