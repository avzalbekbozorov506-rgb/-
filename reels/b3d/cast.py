"""Актёры ролика «Чезаре и Рамиро»."""
import chars
def cesare(at=(0, 0, 0), rot_z=0, **kw):
    return chars.man("Cesare", at=at, rot_z=rot_z, skin=(0.80, 0.56, 0.44), hair=(0.30, 0.16, 0.08), iris=(0.50, 0.33, 0.16), coat=(0.07, 0.065, 0.07),
                     frown=0.5, lids=0.35, nose=1.1, jaw=1.05, cape=(0.12, 0.03, 0.03), fur=(0.22, 0.17, 0.13), **kw)
def remirro(at=(0, 0, 0), rot_z=0, **kw):
    return chars.man("Remirro", at=at, rot_z=rot_z, skin=(0.74, 0.50, 0.38), hair=(0.08, 0.07, 0.065), iris=(0.36, 0.38, 0.36), coat=(0.55, 0.54, 0.52),
                     beard=True, hair_style="short", hat=None, gold=False, armor=True, frown=1.0, lids=0.55, nose=1.25, jaw=1.4, chin=1.4, brow=1.8,
                     cheek=1.1, bulk=1.25, scar=True, thin=1.05, shirt=(0.3, 0.22, 0.16), **kw)
def niccolo(at=(0, 0, 0), rot_z=0, **kw):
    return chars.man("Niccolo", at=at, rot_z=rot_z, skin=(0.84, 0.64, 0.52), hair=(0.15, 0.11, 0.08), iris=(0.36, 0.26, 0.17), coat=(0.09, 0.08, 0.08),
                     beard=False, hair_style="short", hat=None, gold=False, frown=0.15, lids=0.5, nose=1.2, jaw=0.9, chin=0.9, cheek=0.92, thin=0.9,
                     smirk=1.0, bulk=0.9, cape=(0.42, 0.06, 0.05), fur=(0.3, 0.26, 0.22), **kw)
TOWN = [dict(skin=(0.82, 0.6, 0.47), hood=(0.42, 0.33, 0.24), coat=(0.4, 0.31, 0.22), hair=(0.3, 0.2, 0.12), beard=True),
        dict(skin=(0.76, 0.54, 0.42), hood=(0.32, 0.36, 0.3), coat=(0.3, 0.33, 0.27), hair=(0.5, 0.48, 0.45), beard=True, thin=0.95, nose=1.3),
        dict(skin=(0.86, 0.66, 0.54), hood=(0.5, 0.2, 0.15), coat=(0.45, 0.2, 0.15), hair=(0.2, 0.13, 0.08), beard=False, jaw=0.95),
        dict(skin=(0.7, 0.5, 0.38), hood=(0.28, 0.27, 0.32), coat=(0.25, 0.25, 0.3), hair=(0.15, 0.1, 0.07), beard=True, jaw=1.15, bulk=1.15),
        dict(skin=(0.84, 0.62, 0.5), hood=(0.45, 0.4, 0.3), coat=(0.38, 0.33, 0.24), hair=(0.6, 0.58, 0.55), beard=True, thin=0.92, nose=1.2)]
def townsman(k, at=(0, 0, 0), rot_z=0, step=0.0024, **kw):
    p = dict(TOWN[k % len(TOWN)]); p.update(kw)
    return chars.man(f"Town{k}", at=at, rot_z=rot_z, hat=None, hair_style="short", gold=False, step=step, lids=0.45, frown=0.3, **p)
