"""Обложка mach_liar: страница «Государя» с маркером."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("page_liar_2", 0.5, 0.3, 1500), "ОН ЛГАЛ\nВСЮ ЖИЗНЬ", "ЕМУ ВЕРИЛИ", "МАКИАВЕЛЛИ", "«Государь», гл. XVIII", "52_mach_liar_click", y=1180, stamp_pos="bottom")
print("ok")
