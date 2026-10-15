"""Свет для селфи-видео: шумоподавление, нейтральный баланс белого по стене (чуть теплее), экспозиция по лицу,
мягкий «ключевой свет» на лицо, локальный контраст (CLAHE), приглушение пересвеченной стены."""
import cv2, numpy as np, subprocess
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
def light(f, face, gains):
    h, w = f.shape[:2]; x, y, fw, fh = face; cx, cy = x + fw / 2, y + fh * 0.55
    f = cv2.bilateralFilter(f, 7, 22, 7)                                            # убрать шум, сохранить края
    img = f.astype(np.float32) / 255 * gains                                        # баланс белого
    lum = img.mean(2); fl = lum[int(y):int(y + fh), int(x):int(x + fw)].mean()
    img = np.clip(img, 0, 1) ** (np.log(0.44) / np.log(max(fl, 1e-3)))              # экспозиция: лицо ≈ 52%
    hi = np.clip((img.mean(2, keepdims=True) - 0.78) / 0.22, 0, 1); img = img * (1 - 0.30 * hi)   # приглушить пересвет стены
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = ((xx - cx) / (fw * 1.6)) ** 2 + ((yy - cy) / (fh * 1.9)) ** 2
    key = 1.0 + 0.10 * np.exp(-r) - 0.22 * np.clip(r / 5, 0, 1)                    # мягкий свет на лицо + виньетка
    img = img * key[..., None] * np.array([0.94, 0.99, 1.05])                        # BGR: чуть теплее
    lab = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lab[..., 0])
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= 1.14
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
def wb_gains(f):
    b, g, r = [np.percentile(f[..., i], 92) for i in range(3)]; m = (b + g + r) / 3
    return np.array([m / b, m / g, m / r], np.float32)
def relight_video(src, dst):
    cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS) or 30; w = int(cap.get(3)); h = int(cap.get(4))
    enc = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-i", src,
                            "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], stdin=subprocess.PIPE)
    face = None; gains = None
    while True:
        ok, f = cap.read()
        if not ok: break
        fs = casc.detectMultiScale(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(150, 150))
        if len(fs): nf = np.array(max(fs, key=lambda r: r[2] * r[3]), np.float32); face = nf if face is None else face * 0.8 + nf * 0.2
        g = wb_gains(f); gains = g if gains is None else gains * 0.9 + g * 0.1
        enc.stdin.write(light(f, tuple(face) if face is not None else (w * 0.3, h * 0.2, w * 0.4, h * 0.25), gains).tobytes())
    enc.stdin.close(); enc.wait()
if __name__ == "__main__":
    cap = cv2.VideoCapture("src.mp4"); out = []
    for i in range(320):
        ok, f = cap.read()
        if not ok: break
        if i in (30, 150, 280):
            fc = max(casc.detectMultiScale(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(150, 150)), key=lambda r: r[2] * r[3])
            out.append(np.vstack([cv2.resize(f, (270, 480)), cv2.resize(light(f, fc, wb_gains(f)), (270, 480))]))
    cv2.imwrite("light_test.jpg", np.hstack(out))
