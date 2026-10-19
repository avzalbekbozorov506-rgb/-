"""Кадры ролика money_map («Куда утекает зарплата») в бумажном стиле. Цифры: НДФЛ 13 % (до 2,4 млн ₽ в год), страховые взносы работодателя 30 %
(общий тариф, до предельной базы); 100 000 на руки = 114 943 до НДФЛ; + взносы 34 483 → ≈ 149 400 ₽. Кофе 200 ₽ × 365 = 73 000 ₽."""
import sys; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from paper_kit import *
T0 = 300   # верх зоны содержимого (ниже шапки)

def s01():
    im = background(1); tape(im, T0, "Ты получаешь на руки 100 000", hl="100 000")
    card(im, (150, 560), (780, 200), ["НА РУКИ", "100 000 ₽"], fonts=[F(40), S(96)], seed=3)
    person(im, (540, 980), 0.9); save(im, "pp_01")
def s02():
    im = background(2); tape(im, T0, "А работодатель платит почти 150 000", hl="150 000")
    card(im, (90, 420), (620, 230), ["РАБОТОДАТЕЛЬ ПЛАТИТ", "≈ 149 000 ₽"], color=YEL, fonts=[F(34), S(84)], seed=5, angle=-2)
    label(im, (850, 520), "−49 000", size=56, angle=4)
    card(im, (240, 760), (600, 190), ["НА РУКИ", "100 000 ₽"], fonts=[F(34), S(80)], seed=6)
    ImageDraw.Draw(im).line((540, 690, 540, 750), fill=RED, width=8); save(im, "pp_02")
def s03():
    im = background(3); tape(im, T0, "Мы спросили Клода: куда?", hl="Клода:")
    card(im, (160, 470), (760, 420), ["КАРТА ДЕНЕГ", "", "зарплата не исчезает —", "она утекает"], color=CREAM, fonts=[S(84), F(20), F(38), F(38)], colors=[RED, INK, INK, INK], seed=7, angle=1.5)
    save(im, "pp_03")
def s04():
    im = background(4); tape(im, T0, "Кузнец заработал 150 монет", hl="150")
    d = ImageDraw.Draw(im); d.rectangle((0, 820, W, 1000), fill=(70, 55, 45))          # мостовая
    building(im, (830, 700), 260, "shop", "КУЗНИЦА"); person(im, (360, 900), 1.0, apron=(110, 70, 45))
    d = ImageDraw.Draw(im); d.rectangle((460, 760, 620, 800), fill=(70, 70, 75)); d.rectangle((510, 800, 570, 880), fill=(70, 70, 75))   # наковальня
    coins(im, (560, 740), 8, seed=4); label(im, (540, 470), "150 МОНЕТ", color=YEL, fg=INK, size=48); save(im, "pp_04")
def s05():
    im = background(5); tape(im, T0, "Первые краны — до его кармана", hl="краны")
    pipe(im, (80, 520), (1000, 520)); tap(im, (330, 520)); tap(im, (620, 520))
    drops(im, (330, 620), 3); drops(im, (620, 620), 3)
    label(im, (330, 800), "ВЗНОСЫ  35", size=34); label(im, (620, 800), "НАЛОГ  15", size=34)
    building(im, (470, 960), 200, "bank", None); label(im, (870, 450), "ГОРОД", color=INK, size=28)
    coin_big(im, (900, 640), 60); save(im, "pp_05")
def s06():
    im = background(6); tape(im, T0, "До кузнеца дошло 100", hl="100")
    person(im, (300, 960), 1.0, apron=(110, 70, 45)); coins(im, (300, 680), 6, seed=2)
    card(im, (520, 520), (440, 300), ["ОН ДАЖЕ", "НЕ ВИДЕЛ", "ЭТИХ КРАНОВ"], color=YEL, fonts=[S(48)] * 3, seed=9, angle=-3); save(im, "pp_06")
def three_pipes(im, mark=None):
    pipe(im, (540, 440), (540, 560)); coin_big(im, (540, 440), 50)
    pipe(im, (180, 560), (900, 560))
    for k, (x, t) in enumerate([(180, "ЖИЗНЬ"), (540, "ДОЛГИ"), (900, "МЕЛКИЕ КРАНЫ")], 1):
        pipe(im, (x, 560), (x, 760)); tap(im, (x, 760), open_=True); drops(im, (x, 860), 2)
        badge(im, (x - 90, 640), k); label(im, (x, 960), t, color=RED if mark == k else INK, size=30)
def s07():
    im = background(7); tape(im, T0, "Дальше сотня течёт по трём трубам", hl="трём"); three_pipes(im); save(im, "pp_07")
def s08():
    im = background(8); tape(im, T0, "Первая — жизнь", hl="жизнь")
    building(im, (300, 650), 260, "house", "ЖИЛЬЁ"); card(im, (560, 470), (400, 160), ["ЕДА • ДОРОГА"], fonts=[S(40)], seed=11)
    card(im, (560, 700), (400, 230), ["СУЗИТЬ ✓", "ПЕРЕКРЫТЬ ✗"], color=CREAM, fonts=[S(48), S(48)], colors=[GREEN, RED], seed=12, angle=2); save(im, "pp_08")
def s09():
    im = background(9); tape(im, T0, "Вторая — долги", hl="долги")
    card(im, (90, 460), (420, 300), ["МОЛОТ", "В ДОЛГ", "год назад"], color=YEL, fonts=[S(60), S(60), F(30)], seed=13, angle=-3)
    pipe(im, (560, 600), (1000, 600)); drops(im, (780, 650), 3)
    building(im, (800, 850), 220, "bank", "РОСТОВЩИК"); label(im, (300, 900), "МОЛОТ СЛОМАН", size=34, angle=-2); save(im, "pp_09")
def s10():
    im = background(10); tape(im, T0, "Третья — мелкие краны", hl="мелкие")
    pipe(im, (60, 470), (1020, 470))
    for k, x in enumerate([190, 420, 650, 880]): tap(im, (x, 470)); drops(im, (x, 570), 2); bucket(im, (x, 680), 140, 110, 0.35 + 0.1 * k)
    card(im, (220, 870), (640, 140), ["КОФЕ 200 ₽ × 365 = 73 000 ₽"], color=YEL, fonts=[F(36)], seed=14); save(im, "pp_10")
def s11():
    im = background(11); tape(im, T0, "По отдельности — мелочь", hl="мелочь")
    for x, t in [(190, "КОФЕ"), (420, "ПОДПИСКИ"), (650, "ДОСТАВКА"), (880, "ТАКСИ")]: label(im, (x, 470), t, color=INK, size=28)
    pipe(im, (190, 520), (190, 700)); pipe(im, (420, 520), (420, 700)); pipe(im, (650, 520), (650, 700)); pipe(im, (880, 520), (880, 700))
    pipe(im, (190, 700), (880, 700)); pipe(im, (540, 700), (540, 880)); drops(im, (540, 900), 3, step=26)
    label(im, (780, 900), "ВМЕСТЕ — КУСОК ЗАРПЛАТЫ", size=30, angle=-2); save(im, "pp_11")
def s12():
    im = background(12, light=True); tape(im, T0, "Деньги никуда не пропадают", hl="не")
    coin_big(im, (540, 460), 70); pipe(im, (540, 530), (540, 640)); pipe(im, (220, 640), (860, 640))
    for x, k, t in [(220, "bank", "БАНК"), (540, "shop", "МАГАЗИН"), (860, "house", "СЕРВИС")]: pipe(im, (x, 640), (x, 760)); building(im, (x, 860), 170, k, t)
    save(im, "pp_12")
def s13():
    im = background(13); tape(im, T0, "А тебе что-то остаётся?", hl="тебе")
    bucket(im, (540, 520), 260, 230, 0.05, None); label(im, (540, 830), "ТВОЁ БУДУЩЕЕ", color=RED, size=40)
    label(im, (820, 470), "?", color=YEL, fg=INK, size=90, angle=8); save(im, "pp_13")
def s14():
    im = background(14); tape(im, T0, "Краны закрывают в обратном порядке", hl="обратном")
    pipe(im, (540, 410), (540, 470)); coin_big(im, (540, 415), 40); pipe(im, (240, 470), (900, 470))
    pipe(im, (240, 470), (240, 600)); bucket(im, (240, 610), 200, 160, 0.6, "СЕБЕ 10 %")
    for y, t in [(600, "ЖИЗНЬ"), (720, "ДОЛГИ"), (840, "МЕЛКИЕ КРАНЫ")]:
        d = ImageDraw.Draw(im); d.rectangle((520, y, 940, y + 70), fill=(80, 84, 90)); d.text((730, y + 35), t, font=S(30, "Bold"), fill=(230, 230, 230), anchor="mm")
    badge(im, (130, 520), 1); save(im, "pp_14")
def s15():
    im = background(15); tape(im, T0, "Потом — самый дорогой долг", hl="дорогой")
    pipe(im, (80, 560), (1000, 560)); d = ImageDraw.Draw(im); d.ellipse((420, 460, 620, 660), outline=RED, width=18); d.line((520, 460, 520, 660), fill=RED, width=14)
    badge(im, (200, 450), 2); label(im, (520, 760), "ПЕРЕКРЫТЬ", size=44)
    badge(im, (200, 900), 3); card(im, (300, 850), (620, 130), ["МЕЛКИЕ КРАНЫ — РАЗ В МЕСЯЦ"], color=YEL, fonts=[F(30)], seed=16); save(im, "pp_15")
def s16():
    im = background(16); tape(im, T0, "Нарисуй свою карту", hl="свою")
    card(im, (140, 440), (800, 480), ["ЗАРПЛАТА", "НЕ ИСЧЕЗАЕТ.", "", "ОНА УТЕКАЕТ ТУДА,", "ГДЕ НЕТ КАРТЫ"], color=YEL,
         fonts=[S(70), S(70), F(16), S(44), S(44)], colors=[INK, INK, INK, RED, RED], seed=17, angle=-1.5); save(im, "pp_16")
if __name__ == "__main__":
    for f in [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16]: f()
    print("ok")
