"""Кликбейт-обложки для трёх роликов о Макиавелли (портреты The Met CC0): лицо над плашкой, текст — правдивый."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers import cover_crop
from make_covers_click import make_click
for art, fx, fy, z, hook, stamp, title, sub, out in [
    ("sarto_man", 0.36, 0.42, 1.15, "ЕГО ПЫТАЛИ.\nПОТОМ ОН\nНАПИСАЛ ЭТО", "1513", "МАКИАВЕЛЛИ", "5 горьких правд о людях", "12_mach_people_click"),
    ("tintoretto_man", 0.43, 0.38, 1.2, "14 ЛЕТ СЛУЖБЫ —\nИ ЕГО ВЫГНАЛИ", "УВОЛЕН", "МАКИАВЕЛЛИ", "как распознать умного человека", "13_mach_minds_click"),
    ("moretto_man", 0.38, 0.45, 1.15, "ОН НИКОГДА\nЭТОГО\nНЕ ПИСАЛ", "МИФ", "МАКИАВЕЛЛИ", "что он писал на самом деле", "14_mach_myth_click")]:
    make_click(cover_crop(Image.open(f"{HERE}/art/{art}.jpg").convert("RGB"), fx, fy, z), hook, stamp, title, sub, out)
print("ok")
