import sys, os, math; sys.path.insert(0, os.path.dirname(__file__))
import kit, chars, sets
kit.reset(); sets.hall()
ces = chars.man("Cesare", at=(0, 0.25, 0), skin=(0.80, 0.56, 0.44), hair=(0.30, 0.16, 0.08), iris=(0.50, 0.33, 0.16), coat=(0.07, 0.065, 0.07),
                frown=0.5, lids=0.35, nose=1.1, jaw=1.05, cape=(0.12, 0.03, 0.03), fur=(0.22, 0.17, 0.13))
ces["head"].rotation_euler = (math.radians(3), 0, math.radians(-10))
kit.area("key", (-0.9, -0.8, 1.2), (0, 0.25, 1.65), 28, size=0.6, color=(1.0, 0.7, 0.42))
kit.area("fillw", (0, -2.5, 2.5), (0, 2.5, 1.5), 60, size=3, color=(0.5, 0.6, 0.85))
kit.area("rim", (1.2, 1.4, 2.2), (0, 0.25, 1.6), 200, size=0.5, color=(0.65, 0.78, 1.0))
kit.world((0.03, 0.035, 0.05), 1.0, fog=float(os.environ.get('FOG', '0.012')), fog_color=(0.9, 0.85, 0.8))
kit.camera((0.22, -0.95, 1.62), (0.0, 0.25, 1.6), lens=40, fstop=2.2, focus=(0, 0.17, 1.63))
kit.setup_render(samples=int(sys.argv[1]), res=(1080, 1920), pct=int(sys.argv[2]))
kit.render(sys.argv[3])
