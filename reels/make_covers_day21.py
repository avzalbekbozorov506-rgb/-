"""Обложки роликов 21.10 (книга недели: Э. Берн, «Игры, в которые играют люди»): «Если бы не ты», «Да, но…», «Смотри, что ты заставил меня сделать»."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("b_94840", 0.5, 0.4, 2000), "МУЖ НЕ ПУСКАЛ ЕЁ\nИЗ ДОМА. ПОТОМ ПУСТИЛ", "ИГРА БЕРНА", "ЭРИК БЕРН", "«Если бы не ты»", "49_berne_ifnot_click", y=1180, stamp_pos="bottom")
make_click(crop("b_7792c", 0.5, 0.45, 1830), "ЧАСТО СЛЫШИШЬ\nВ ОТВЕТ «ДА, НО»?", "ИГРА БЕРНА", "ЭРИК БЕРН", "«Да, но…» · пример", "50_berne_yesbut_click", y=1180, stamp_pos="bottom")
make_click(crop("b_34579c", 0.5, 0.45, 2150), "ОН УДАРИЛ СЕБЯ\nМОЛОТКОМ. ВИНОВАТА ДОЧЬ", "ИГРА БЕРНА", "ЭРИК БЕРН", "«Смотри, что ты заставил меня» · пример", "51_berne_swymd_click", y=1180, stamp_pos="bottom")
print("ok")
