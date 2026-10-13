import sys, os, math; sys.path.insert(0, os.path.dirname(__file__))
import kit, cast
kit.reset()
cast.remirro(at=(-0.35, 0, 0)); cast.niccolo(at=(0.35, 0, 0))
bg = kit.mat("bg", (0.3, 0.28, 0.27), rough=0.9); kit.box("bg", (8, 0.1, 5), (0, 2, 2), bg)
kit.area("key", (-1.5, -2, 2.5), (0, 0, 1.6), 200, size=1.5, color=(1, 0.85, 0.7)); kit.area("rim", (1.5, 1.5, 2.5), (0, 0, 1.6), 300, size=1, color=(0.7, 0.8, 1))
kit.world((0.2, 0.22, 0.25), 1.0)
kit.camera((0, -1.6, 1.68), (0, 0, 1.66), lens=50, fstop=0)
kit.setup_render(samples=16, res=(1920, 1080), pct=50); kit.render("/tmp/claude-0/t/faces.png")
