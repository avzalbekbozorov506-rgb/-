"""«Пресс давит фисташки в масло» — 3D-сцена Blender (Cycles, CPU), всё создаётся кодом, без чужих моделей и текстур.
Запуск: python3 blender/press_nuts.py <out_dir> [кадры, напр. 1-300 или 120] [ширина] [сэмплы]
Анимация: пресс опускается, слой орехов сжимается (shape key «crushed»), масло копится на дне, течёт струйкой в стакан, стакан наполняется."""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/press"
FR = sys.argv[2] if len(sys.argv) > 2 else "1-300"
RW = int(sys.argv[3]) if len(sys.argv) > 3 else 720
SPP = int(sys.argv[4]) if len(sys.argv) > 4 else 48
FPS, N_FR = 24, 336
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SPP
sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03; sc.cycles.max_bounces = 10; sc.cycles.transmission_bounces = 10; sc.cycles.glossy_bounces = 4; sc.cycles.diffuse_bounces = 2
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.blur_glossy = 1.0
sc.render.resolution_x = RW; sc.render.resolution_y = int(RW * 16 / 9); sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, N_FR
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
def mat(name, color, rough=0.5, metal=0.0, trans=0.0, ior=1.45, spec=0.5, aniso=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Transmission Weight"].default_value = trans; b.inputs["IOR"].default_value = ior
    if aniso: b.inputs["Anisotropic"].default_value = aniso
    return m, b
def link_noise(m, b, scale, c1, c2, bump=0.0):
    nt = m.node_tree; n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = 8
    r = nt.nodes.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].color = (*c1, 1); r.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"]); nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    if bump:
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; nt.links.new(n.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
def obj_from(mesh_fn, name, m=None):
    mesh_fn(); o = bpy.context.active_object; o.name = name
    if m: o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o
# ---------------- материалы
glass, _ = mat("glass", (0.95, 0.97, 1.0), rough=0.02, trans=1.0, ior=1.45)
def shadow_clear(m):
    nt = m.node_tree; out = nt.nodes["Material Output"]; pb = nt.nodes["Principled BSDF"]
    lp = nt.nodes.new("ShaderNodeLightPath"); tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0]); nt.links.new(pb.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
shadow_clear(glass)
steel, sb = mat("steel", (0.62, 0.64, 0.67), rough=0.22, metal=1.0, aniso=0.6)
oil, ob = mat("oil", (1.0, 0.72, 0.08), rough=0.03, trans=1.0, ior=1.47)
shadow_clear(oil)
ob.inputs["Coat Weight"].default_value = 0.0
nt = oil.node_tree; vol = nt.nodes.new("ShaderNodeVolumeAbsorption"); vol.inputs["Color"].default_value = (1.0, 0.82, 0.25, 1); vol.inputs["Density"].default_value = 2.2
nt.links.new(vol.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
shell, shb = mat("shell", (0.66, 0.50, 0.36), rough=0.55); link_noise(shell, shb, 22, (0.55, 0.40, 0.28), (0.80, 0.66, 0.50), bump=0.3)
_nt = shell.node_tree; _attr = _nt.nodes.new("ShaderNodeAttribute"); _attr.attribute_name = "tint"; _mixc = _nt.nodes.new("ShaderNodeMix"); _mixc.data_type = "RGBA"; _mixc.blend_type = "MULTIPLY"; _mixc.inputs[0].default_value = 1.0
_ramp_out = [l for l in _nt.links if l.to_socket == shb.inputs["Base Color"]][0].from_socket
_nt.links.new(_ramp_out, _mixc.inputs[6]); _nt.links.new(_attr.outputs["Color"], _mixc.inputs[7]); _nt.links.new(_mixc.outputs[2], shb.inputs["Base Color"])
wall, wb = mat("wall", (0.06, 0.075, 0.075), rough=0.75)
shelf, _ = mat("shelf", (0.02, 0.02, 0.022), rough=0.4)
# ---------------- фон: стена с вертикальными рейками, полка
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.9, 0.55)); w = bpy.context.active_object; w.scale = (3.0, 1, 1.6); w.rotation_euler = (math.radians(90), 0, 0); w.data.materials.append(wall)
for i in range(-14, 15):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 0.11, 0.86, 0.55)); r_ = bpy.context.active_object; r_.scale = (0.035, 0.03, 1.6); r_.data.materials.append(wall)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.2, -0.32)); sh = bpy.context.active_object; sh.scale = (3.0, 1.6, 0.04); sh.data.materials.append(shelf)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.2, 0.0)); sh2 = bpy.context.active_object; sh2.scale = (3.0, 1.6, 0.03); sh2.data.materials.append(shelf)
# ---------------- стеклянный цилиндр, краник, стакан
CR, CH, CZ = 0.20, 0.28, 0.03                      # радиус, высота, низ цилиндра
def tube(r, h, z, thick, m, name, bottom=True):
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=r, depth=h, location=(0, 0, z + h / 2)); o = bpy.context.active_object; o.name = name
    bm = bmesh.new(); bm.from_mesh(o.data); top = [f for f in bm.faces if f.normal.z > 0.9]; bmesh.ops.delete(bm, geom=top, context="FACES")
    if not bottom: bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.9], context="FACES")
    bm.to_mesh(o.data); bm.free(); md = o.modifiers.new("s", "SOLIDIFY"); md.thickness = thick; md.offset = 1.0
    bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.modifier_apply(modifier="s")
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
    o.data.materials.append(m); bpy.ops.object.shade_flat(); return o
cyl = tube(CR, CH, CZ, 0.008, glass, "cyl")
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.012, depth=0.05, location=(0, 0, CZ - 0.02)); sp = bpy.context.active_object; sp.data.materials.append(glass); bpy.ops.object.shade_flat()
BZ = -0.30; BR, BH = 0.12, 0.17
beaker = tube(BR, BH, BZ, 0.004, glass, "beaker")
# ---------------- пресс
PZ0, PZ1 = CZ + CH + 0.08, CZ + 0.055            # нижняя грань диска: начало и конец хода
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=CR * 0.985, depth=0.05, location=(0, 0, PZ0 + 0.025)); disk = bpy.context.active_object; disk.data.materials.append(steel); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.075, depth=0.9, location=(0, 0, PZ0 + 0.05 + 0.45)); rod = bpy.context.active_object; rod.data.materials.append(steel); bpy.ops.object.shade_smooth(); rod.parent = disk; rod.matrix_parent_inverse = disk.matrix_world.inverted()
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.27, depth=0.06, location=(0, 0, 0.98)); topp = bpy.context.active_object; topp.data.materials.append(steel); bpy.ops.object.shade_smooth()
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def press_z(f):
    u = (f - 1) / (N_FR - 1); a = ease(min(1, u / 0.18)) * 0.33 + ease((u - 0.18) / 0.82) * 0.67 if u > 0.18 else ease(u / 0.18) * 0.33
    return PZ0 - (PZ0 - PZ1) * (a if u > 0.18 else ease(u / 0.18) * 0.33)
# ---------------- фисташки: один объект, ключ формы «crushed»
bm = bmesh.new(); TOP = CZ + CH - 0.01; n = 0; cents = []
base0 = bmesh.new(); bmesh.ops.create_uvsphere(base0, u_segments=12, v_segments=8, radius=1.0); PV = [v.co.copy() for v in base0.verts]; base0.free()
while n < 820:
    x = random.uniform(-CR, CR); y = random.uniform(-CR, CR)
    if x * x + y * y > (CR - 0.018) ** 2: continue
    z = CZ + 0.012 + random.uniform(0, TOP - CZ - 0.02); cents.append((x, y, z)); n += 1
crushed = []
from mathutils import Euler
for (x, y, z) in cents:
    e = Euler((random.uniform(-0.6, 0.6), random.uniform(0, math.pi), random.uniform(0, math.pi))); sx, sy, sz = 0.0165 * random.uniform(0.9, 1.1), 0.0115, 0.010
    for c in PV:
        p = Vector((c.x * sx, c.y * sy, c.z * sz)); p.rotate(e); crushed.append(p)
# собираем меш вручную (быстрее, чем duplicate)
me = bpy.data.meshes.new("nuts"); nuts = bpy.data.objects.new("nuts", me); sc.collection.objects.link(nuts)
bm = bmesh.new(); base = bmesh.new(); bmesh.ops.create_uvsphere(base, u_segments=12, v_segments=8, radius=1.0); base.verts.ensure_lookup_table()
faces_idx = [[v.index for v in f.verts] for f in base.faces]; NV = len(base.verts); base.free()
rest, crush = [], []
random.seed(11)
for k, (x, y, z) in enumerate(cents):
    loc = crushed[k * NV:(k + 1) * NV]
    for p in loc: rest.append(Vector((x, y, z)) + p)
    # сжатая форма: высота слоя от низа уменьшается до (PZ1 - CZ), орех сплющивается
    H0 = TOP - CZ; H1 = (PZ1 - CZ) * 0.92; zz = CZ + (z - CZ) * H1 / H0
    for p in loc: crush.append(Vector((x + p.x * 1.25, y + p.y * 1.25, zz + p.z * 0.35)))
vs = [bm.verts.new(p) for p in rest]; bm.verts.ensure_lookup_table()
for k in range(len(cents)):
    for f in faces_idx:
        try: bm.faces.new([vs[k * NV + i] for i in f])
        except ValueError: pass
bm.to_mesh(me); bm.free(); nuts.data.materials.append(shell)
ca = me.color_attributes.new("tint", "FLOAT_COLOR", "POINT"); random.seed(5)
for k in range(len(cents)):
    t = random.random(); c = (1.0, 0.92, 0.85) if t < 0.5 else ((0.92, 0.80, 0.70) if t < 0.8 else ((0.80, 0.85, 0.62) if t < 0.92 else (0.85, 0.66, 0.70)))
    c = tuple(v * random.uniform(0.85, 1.08) for v in c)
    for i in range(k * NV, (k + 1) * NV): ca.data[i].color = (*c, 1)
for p in me.polygons: p.use_smooth = True
nuts.shape_key_add(name="Basis"); kb = nuts.shape_key_add(name="crushed")
for i, p in enumerate(crush): kb.data[i].co = p
# потемнение и «масляность» скорлупы по мере сжатия: смешиваем через значение (драйвер по ключу)
mix = shell.node_tree.nodes.new("ShaderNodeValue"); mix.name = "wet"
for f in range(1, N_FR + 1, 4):
    pz = press_z(f); c = max(0.0, min(1.0, (PZ0 - 0.0 - pz - (PZ0 - (TOP + 0.0))) / ((TOP + 0.0) - PZ1))) if pz < TOP else 0.0
    kb.value = c; kb.keyframe_insert("value", frame=f)
    shb.inputs["Roughness"].default_value = 0.55 - 0.4 * c; shb.inputs["Roughness"].keyframe_insert("default_value", frame=f)
for f in range(1, N_FR + 1, 4):
    disk.location.z = press_z(f) + 0.025; disk.keyframe_insert("location", index=2, frame=f)
# ---------------- масло: слой на дне цилиндра, струя, стакан
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=CR - 0.004, depth=1.0, location=(0, 0, CZ)); oc = bpy.context.active_object; oc.data.materials.append(oil); bpy.ops.object.shade_smooth()
bpy.ops.object.transform_apply(location=False, scale=True); oc.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
stm, stb = mat("oil_stream", (1.0, 0.70, 0.10), rough=0.05, trans=0.35, ior=1.47); stb.inputs["Emission Color"].default_value = (1.0, 0.70, 0.15, 1); stb.inputs["Emission Strength"].default_value = 0.35
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.0055, depth=1.0, location=(0, 0, 0)); st = bpy.context.active_object; st.data.materials.append(stm); bpy.ops.object.shade_smooth()
st.data.transform(__import__("mathutils").Matrix.Translation((0, 0, -0.5)))
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=BR - 0.003, depth=1.0, location=(0, 0, BZ + 0.004)); obk = bpy.context.active_object; obk.data.materials.append(oil); bpy.ops.object.shade_smooth()
obk.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
F_ON = int(N_FR * 0.42); STREAM_TOP = CZ - 0.045
for f in range(1, N_FR + 1, 2):
    pz = press_z(f); c = max(0.0, min(1.0, (TOP - pz) / (TOP - PZ1))) if pz < TOP else 0.0
    oc.scale.z = max(0.0005, 0.035 * max(0, c - 0.25) / 0.75); oc.keyframe_insert("scale", index=2, frame=f)
    on = f >= F_ON; level = BZ + 0.004 + (0.10 * ((f - F_ON) / (N_FR - F_ON)) ** 0.9 if on else 0.0005)
    obk.scale = (1 if on else 0.001, 1 if on else 0.001, max(0.0005, level - (BZ + 0.004))); obk.keyframe_insert("scale", frame=f)
    st.location = (0, 0, STREAM_TOP); st.keyframe_insert("location", frame=f)
    st.scale = (1 if on else 0.001, 1 if on else 0.001, max(0.001, STREAM_TOP - level) if on else 0.001); st.keyframe_insert("scale", frame=f)
# ---------------- свет и камера
def area(loc, rot, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot); l = bpy.context.active_object; l.data.size = size; l.data.energy = energy; l.data.color = color; return l
area((-1.0, -0.8, 0.6), (math.radians(70), 0, math.radians(-50)), 1.0, 40)
area((1.0, -0.8, 0.5), (math.radians(70), 0, math.radians(50)), 1.0, 28, (1, 0.97, 0.92))
area((0, -0.3, 1.6), (math.radians(10), 0, 0), 1.2, 30)
area((0, 0.6, 0.25), (math.radians(-90), 0, 0), 1.5, 6, (0.8, 0.9, 1.0))
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True; world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.025, 0.03, 1)
bpy.ops.object.camera_add(location=(0, -1.9, 0.12), rotation=(math.radians(90), 0, 0)); cam = bpy.context.active_object; cam.data.lens = 62; sc.camera = cam
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 1.9; cam.data.dof.aperture_fstop = 5.6
# ---------------- рендер
os.makedirs(OUT, exist_ok=True)
STEP = int(os.environ.get("STEP", "1")); fr = [int(FR)] if "-" not in FR else list(range(int(FR.split("-")[0]), int(FR.split("-")[1]) + 1, STEP))
for f in fr:
    sc.frame_set(f); sc.render.filepath = f"{OUT}/{f:04d}.png"
    if os.path.exists(sc.render.filepath): continue
    bpy.ops.render.render(write_still=True)
print("ok", len(fr))
