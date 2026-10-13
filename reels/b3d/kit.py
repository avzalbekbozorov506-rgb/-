"""Мини-студия «под Pixar» в Blender (bpy, Cycles, CPU): материалы, персонажи из метаболов, свет, камера.
Персонаж смотрит в −Y, ось Z вверх, рост ~1.8 (единицы — метры)."""
import math, bpy, bmesh
from mathutils import Vector, Euler

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene

# ---------- материалы ----------
def _bsdf(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"], m.node_tree
def lin(c): return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)   # цвета задаём как в sRGB (как в пипетке)
def mat(name, color, rough=0.5, sss=0.0, sheen=0.0, metal=0.0, coat=0.0, emit=None, emit_k=0.0, noise=0.0, nscale=30.0, alpha=1.0, spec=0.5):
    m, b, t = _bsdf(name); color = lin(color)
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Specular IOR Level"].default_value = spec
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss; b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.03
    if sheen: b.inputs["Sheen Weight"].default_value = sheen; b.inputs["Sheen Roughness"].default_value = 0.35; b.inputs["Sheen Tint"].default_value = (*[min(1, v * 3 + 0.15) for v in color], 1)
    if coat: b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = 0.08
    if emit: b.inputs["Emission Color"].default_value = (*lin(emit), 1); b.inputs["Emission Strength"].default_value = emit_k
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
    if noise:                                                                         # пятна/ворс: шум двигает цвет и шероховатость
        n = t.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = nscale; n.inputs["Detail"].default_value = 6
        r = t.nodes.new("ShaderNodeMapRange"); r.inputs["To Min"].default_value = 1 - noise; r.inputs["To Max"].default_value = 1 + noise
        vm = t.nodes.new("ShaderNodeVectorMath"); vm.operation = "SCALE"; vm.inputs[0].default_value = color
        t.links.new(n.outputs["Fac"], r.inputs["Value"]); t.links.new(r.outputs["Result"], vm.inputs["Scale"])
        t.links.new(vm.outputs["Vector"], b.inputs["Base Color"])
    return m

def eye_mat(name, iris=(0.45, 0.3, 0.16)):
    """Глазное яблоко: белок, радужка с тёмным ободком, зрачок; лак сверху (блик). Ось взгляда — локальная −Y."""
    m, b, t = _bsdf(name); N = t.nodes; L = t.links; iris = lin(iris)
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    # расстояние от оси взгляда: sqrt(x²+z²) на передней полусфере
    vx = N.new("ShaderNodeVectorMath"); vx.operation = "MULTIPLY"; vx.inputs[1].default_value = (1, 0, 1); L.new(tc.outputs["Object"], vx.inputs[0])
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; L.new(vx.outputs[0], ln.inputs[0])
    front = N.new("ShaderNodeMath"); front.operation = "LESS_THAN"; front.inputs[1].default_value = 0.0; L.new(sep.outputs["Y"], front.inputs[0])
    ramp = N.new("ShaderNodeValToRGB"); cr = ramp.color_ramp; cr.interpolation = "EASE"
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.01, 0.008, 0.008, 1)
    cr.elements[1].position = 0.2; cr.elements[1].color = (*iris, 1)
    for p, c in ((0.42, tuple(v * 0.6 for v in iris) + (1,)), (0.5, (0.04, 0.03, 0.025, 1)), (0.56, (0.78, 0.74, 0.7, 1)), (1.0, (0.84, 0.8, 0.76, 1))):
        e = cr.elements.new(p); e.color = c
    e = cr.elements.new(0.18); e.color = (0.01, 0.008, 0.008, 1)
    mul = N.new("ShaderNodeMath"); mul.operation = "SUBTRACT"; mul.inputs[0].default_value = 1.0; L.new(front.outputs[0], mul.inputs[1])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; L.new(ln.outputs["Value"], mx.inputs[0]); L.new(mul.outputs[0], mx.inputs[1])
    L.new(mx.outputs[0], ramp.inputs["Fac"]); L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.35; b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.0
    b.inputs["Subsurface Weight"].default_value = 0.1; b.inputs["Subsurface Scale"].default_value = 0.005
    return m

# ---------- геометрия ----------
def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob); return ob
def blob(name, parts, material, res=0.012, smooth=2, parent=None, thresh=0.6):
    """Гладкое «вылепленное» тело из метаболов → меш. parts: [(тип, (x,y,z), радиус, (sx,sy,sz), (rx,ry,rz) в градусах, жёсткость, отрицательный)]."""
    mb = bpy.data.metaballs.new(name + "_mb"); mb.resolution = res; mb.render_resolution = res; mb.threshold = thresh
    for p in parts:
        typ, co, r = p[0], p[1], p[2]; s = p[3] if len(p) > 3 else (1, 1, 1); rot = p[4] if len(p) > 4 else (0, 0, 0)
        e = mb.elements.new(type=typ); e.co = co; e.radius = r; e.stiffness = p[5] if len(p) > 5 else 2.0; e.use_negative = p[6] if len(p) > 6 else False
        if typ in ("ELLIPSOID", "CAPSULE", "CUBE", "PLANE"): e.size_x, e.size_y, e.size_z = s
        e.rotation = Euler([math.radians(a) for a in rot]).to_quaternion()
    ob = link(bpy.data.objects.new(name + "_tmp", mb))
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg)); bpy.data.objects.remove(ob)
    out = link(bpy.data.objects.new(name, me))
    for f in me.polygons: f.use_smooth = True
    if smooth:
        mod = out.modifiers.new("smooth", "CORRECTIVE_SMOOTH"); mod.iterations = 6 * smooth; mod.use_only_smooth = True
    me.materials.append(material)
    if parent: out.parent = parent
    return out

def sphere(name, r, co, material, scale=(1, 1, 1), rot=(0, 0, 0), seg=48, parent=None, cut=None):
    """UV-сфера; cut=доля высоты, ниже которой вершины удаляются (для век/шапок)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    if cut is not None:
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < r * cut], context="VERTS")
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=r * 0.06)
    bm.to_mesh(me); bm.free()
    for f in me.polygons: f.use_smooth = True
    ob = link(bpy.data.objects.new(name, me)); ob.location = co; ob.scale = scale; ob.rotation_euler = [math.radians(a) for a in rot]
    me.materials.append(material)
    if parent: ob.parent = parent
    return ob

def cylinder(name, r, depth, co, material, rot=(0, 0, 0), r2=None, seg=48, parent=None, bevel=0.0):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth, location=co, rotation=[math.radians(a) for a in rot])
    ob = bpy.context.object; ob.name = name; ob.data.materials.append(material)
    if bevel: m = ob.modifiers.new("b", "BEVEL"); m.width = bevel; m.segments = 4
    bpy.ops.object.shade_smooth()
    if parent: ob.parent = parent
    return ob

def box(name, size, co, material, rot=(0, 0, 0), bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=co, rotation=[math.radians(a) for a in rot]); ob = bpy.context.object
    ob.name = name; ob.scale = size; ob.data.materials.append(material)
    if bevel: m = ob.modifiers.new("b", "BEVEL"); m.width = bevel; m.segments = 3; m.limit_method = "NONE"
    if parent: ob.parent = parent
    return ob

def empty(name, co=(0, 0, 0), parent=None):
    e = link(bpy.data.objects.new(name, None)); e.location = co
    if parent: e.parent = parent
    return e

# ---------- свет, мир, камера ----------
def area(name, co, target, energy, size=1.0, color=(1, 1, 1), shape="DISK"):
    l = bpy.data.lights.new(name, "AREA"); l.energy = energy; l.size = size; l.color = lin(color); l.shape = shape
    ob = link(bpy.data.objects.new(name, l)); ob.location = co; aim(ob, target); return ob
def point(name, co, energy, color=(1, 0.7, 0.4), radius=0.05):
    l = bpy.data.lights.new(name, "POINT"); l.energy = energy; l.color = lin(color); l.shadow_soft_size = radius
    ob = link(bpy.data.objects.new(name, l)); ob.location = co; return ob
def spot(name, co, target, energy, angle=40, blend=0.6, color=(1, 1, 1), radius=0.1):
    l = bpy.data.lights.new(name, "SPOT"); l.energy = energy; l.spot_size = math.radians(angle); l.spot_blend = blend; l.color = lin(color); l.shadow_soft_size = radius
    ob = link(bpy.data.objects.new(name, l)); ob.location = co; aim(ob, target); return ob
def aim(ob, target):
    d = Vector(target) - Vector(ob.location); ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def world(color=(0.02, 0.025, 0.04), strength=1.0, fog=0.0, fog_color=(1, 1, 1), aniso=0.3):
    sc = bpy.context.scene; w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (*lin(color), 1); bg.inputs[1].default_value = strength
    if fog:                                                                            # объёмная дымка — лучи света, как в кино
        v = w.node_tree.nodes.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = fog
        v.inputs["Color"].default_value = (*lin(fog_color), 1); v.inputs["Anisotropy"].default_value = aniso
        w.node_tree.links.new(v.outputs[0], w.node_tree.nodes["World Output"].inputs["Volume"])
    return w

def camera(co, target, lens=50, fstop=2.8, focus=None, sensor=36):
    c = bpy.data.cameras.new("Cam"); c.lens = lens; c.sensor_width = sensor; c.sensor_fit = "VERTICAL" if False else "AUTO"
    ob = link(bpy.data.objects.new("Cam", c)); ob.location = co; aim(ob, target); bpy.context.scene.camera = ob
    if fstop:
        c.dof.use_dof = True; c.dof.aperture_fstop = fstop
        f = empty("Focus", focus or target); c.dof.focus_object = f
    return ob

def setup_render(samples=64, res=(1080, 1920), pct=100, vol_step=0.2, bounces=6):
    sc = bpy.context.scene; r = sc.render; r.engine = "CYCLES"
    sc.cycles.device = "CPU"; sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
    sc.cycles.max_bounces = bounces; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transmission_bounces = 4
    sc.cycles.volume_bounces = 0; sc.cycles.volume_step_rate = 4.0 if vol_step else 1
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.blur_glossy = 1.0
    r.resolution_x, r.resolution_y = res; r.resolution_percentage = pct
    r.use_persistent_data = True
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    r.image_settings.file_format = "PNG"
    return sc

def render(path):
    sc = bpy.context.scene; sc.render.filepath = path; bpy.ops.render.render(write_still=True)
