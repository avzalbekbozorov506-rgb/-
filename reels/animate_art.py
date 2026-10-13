"""«Оживление» гравюры без нейросетей-генераторов: SAM вырезает фигуры по рамкам, фон под ними дорисовывается (cv2.inpaint),
фигуры двигаются (покачивание, шаг, дыхание, сдвиг), результат — клип work/clips/<картина>.mp4 для движка (CLIPS в конфиге).
Использование: python3 animate_art.py configs/<имя>.py [картина ...]   (берёт словарь PUPPET из конфига)
PUPPET = {картина: [dict(box=(x0,y0,x1,y1) в долях, sway=градусы, bob=доля высоты фигуры, move=(dx,dy) в долях картины за клип,
                          breathe=доля, freq=Гц, phase=рад, pivot=(px,py) в долях рамки фигуры), ...]}"""
import importlib.util, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cfg", sys.argv[1]); cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
NAMES = sys.argv[2:] or list(cfg.PUPPET)
DUR, FPS, LONG = getattr(cfg, "PUPPET_DUR", 7.0), 30, 1400
os.makedirs(f"{HERE}/work/clips", exist_ok=True)
_sam = None
def sam_mask(img, box):
    global _sam
    if _sam is None:
        from transformers import SamModel, SamProcessor
        _sam = (SamModel.from_pretrained("facebook/sam-vit-base").eval(), SamProcessor.from_pretrained("facebook/sam-vit-base"))
    import torch
    m, p = _sam; inp = p(Image.fromarray(img), input_boxes=[[list(map(float, box))]], return_tensors="pt")
    with torch.no_grad(): out = m(**inp)
    ms = p.image_processor.post_process_masks(out.pred_masks, inp["original_sizes"], inp["reshaped_input_sizes"])[0][0].numpy()
    k = int(out.iou_scores[0, 0].argmax()); return ms[k].astype(np.uint8)
for name in NAMES:
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); s = LONG / max(im.size)
    img = np.asarray(im.resize((int(im.width * s) // 2 * 2, int(im.height * s) // 2 * 2), Image.LANCZOS)); h, w = img.shape[:2]
    figs = cfg.PUPPET[name]; layers = []; union = np.zeros((h, w), np.uint8)
    for j, f in enumerate(figs):
        b = f["box"]; box = (b[0] * w, b[1] * h, b[2] * w, b[3] * h); mp = f"{HERE}/art/masks/{name}__{j}.png"
        if os.path.exists(mp) and not f.get("redo"): mask = (np.asarray(Image.open(mp).resize((w, h))) > 127).astype(np.uint8)
        else:
            mask = sam_mask(img, box); bb = np.zeros_like(mask); bb[int(box[1]):int(box[3]), int(box[0]):int(box[2])] = 1; mask *= bb
            Image.fromarray(mask * 255).save(mp)
        union |= mask
        soft = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.2)
        layers.append((np.dstack([img, (soft * 255).astype(np.uint8)]), f, box))
    hole = cv2.dilate(union * 255, np.ones((9, 9), np.uint8))
    bg = cv2.inpaint(img, hole, 9, cv2.INPAINT_TELEA)
    out = f"{HERE}/work/clips/{name}.mp4"
    pr = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        t = n / FPS; fr = bg.astype(np.float32)
        for lay, f, box in layers:
            fq, ph = f.get("freq", 0.35), f.get("phase", 0.0); px, py = f.get("pivot", (0.5, 1.0))
            cx, cy = box[0] + (box[2] - box[0]) * px, box[1] + (box[3] - box[1]) * py
            ang = f.get("sway", 0) * math.sin(2 * math.pi * fq * t + ph)
            sc = 1 + f.get("breathe", 0) * math.sin(2 * math.pi * fq * 0.8 * t + ph)
            dx = f.get("move", (0, 0))[0] * w * t / DUR; dy = f.get("move", (0, 0))[1] * h * t / DUR
            dy -= f.get("bob", 0) * (box[3] - box[1]) * abs(math.sin(math.pi * f.get("step", 1.6) * t + ph))
            M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0); M[1, :] *= 1; M[:, 2] += (dx, dy)
            if sc != 1: M = np.array([[1, 0, 0], [0, sc, cy * (1 - sc)], [0, 0, 1]], np.float64)[:2] @ np.vstack([M, [0, 0, 1]])
            wl = cv2.warpAffine(lay, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0).astype(np.float32)
            a = wl[..., 3:4] / 255; fr = fr * (1 - a) + wl[..., :3] * a
        pr.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait(); print("клип", out, f"{w}x{h}")
