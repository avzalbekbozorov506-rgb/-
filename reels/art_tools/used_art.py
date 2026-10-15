"""Картины, уже использованные в роликах и обложках (не повторять — просьба пользователя 15.10).
  python3 art_tools/used_art.py                 — список: картина → ролики
  python3 art_tools/used_art.py configs/x.py    — проверить новый конфиг: какие его картины уже были (выход 1, если есть повторы)"""
import ast, glob, os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def base(n): return re.sub(r"_(v|va|vb|pad|dark|crop\w*)$", "", n.lstrip("_"))   # фрагменты одной картины = та же картина
def images(path):
    src = open(path).read(); out = set()
    try: tree = ast.parse(src)
    except SyntaxError: return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Tuple) and len(node.elts) >= 4 and all(isinstance(e, ast.Constant) for e in node.elts[3:4]):
            v = node.elts[3].value
            if isinstance(v, str) and os.path.exists(f"{HERE}/art/{v}.jpg"): out.add(v)
    out |= {m for m in re.findall(r'(?:crop|pad_top)\("([\w]+)"', src) if os.path.exists(f"{HERE}/art/{m}.jpg")}
    return out
def used(skip=None):
    u = {}
    for p in glob.glob(f"{HERE}/configs/*.py") + glob.glob(f"{HERE}/make_covers*.py"):
        if skip and os.path.abspath(p) == os.path.abspath(skip): continue
        if skip and "make_covers" in p and os.path.basename(skip)[:-3] in open(p).read(): continue   # обложка этого же ролика
        for im in images(p): u.setdefault(base(im), set()).add(os.path.basename(p)[:-3])
    return u
if __name__ == "__main__":
    if len(sys.argv) > 1:
        u = used(sys.argv[1]); rep = {im: u[base(im)] for im in images(sys.argv[1]) if base(im) in u}
        for im, w in sorted(rep.items()): print(f"ПОВТОР {im}: {', '.join(sorted(w))}")
        print("повторов нет" if not rep else f"повторов: {len(rep)}"); sys.exit(1 if rep else 0)
    for k, v in sorted(used().items(), key=lambda kv: -len(kv[1])): print(f"{len(v):2} {k}: {', '.join(sorted(v))}")
