"""
Costeño AI - Compilador de Animaciones Avanzadas de Alta Fidelidad
Genera animaciones multi-articuladas con cinemática realista:
- Elevación de clavícula (LeftShoulder)
- Arcos de flexión de brazo, antebrazo y muñeca con drag/follow-through
- Movimiento del torso, columna (Spine1, Spine2) y cabeza con balanceo de peso
- Curvas Bezier con auto-clamping para máxima fluidez orgánica
- Exportación a assets/character.glb
"""

import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FBX_PATH = os.path.join(BASE_DIR, "assets", "baselo.fbx")
TEX_DIR = os.path.join(BASE_DIR, "assets", "4021aca1-2d35-4ba4-9d69-3347285a59be")
OUTPUT_GLB = os.path.join(BASE_DIR, "assets", "character.glb")

print(">>> Compilando Personaje con Animaciones Cinemáticas de Alta Fidelidad...")

# 1. Resetear escena
bpy.ops.wm.read_factory_settings(use_empty=True)
for col in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions, bpy.data.images):
    for item in list(col):
        col.remove(item, do_unlink=True)

# 2. Importar FBX
bpy.ops.import_scene.fbx(filepath=FBX_PATH)
arm_obj = bpy.data.objects.get("Armature")
mesh_obj = bpy.data.objects.get("model")

if not arm_obj or not mesh_obj:
    for o in bpy.data.objects:
        if o.type == 'ARMATURE': arm_obj = o
        elif o.type == 'MESH': mesh_obj = o

arm_obj.scale = (1.0, 1.0, 1.0)
mesh_obj.scale = (1.0, 1.0, 1.0)
mesh_obj.name = "Costeno_Mesh"
arm_obj.name = "Costeno_Rig"

# 3. Material PBR
mat = bpy.data.materials.new(name="M_Costeno_PBR")
mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat)
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf_node.outputs["BSDF"], out_node.inputs["Surface"])

# Texturas
diff_file = os.path.join(TEX_DIR, "texture_diffuse.png")
if os.path.exists(diff_file):
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(diff_file)
    links.new(t.outputs["Color"], bsdf_node.inputs["Base Color"])

norm_file = os.path.join(TEX_DIR, "texture_normal.png")
if os.path.exists(norm_file):
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(norm_file)
    t.image.colorspace_settings.name = 'Non-Color'
    nmap = nodes.new("ShaderNodeNormalMap")
    links.new(t.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf_node.inputs["Normal"])

rough_file = os.path.join(TEX_DIR, "texture_roughness.png")
if os.path.exists(rough_file):
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(rough_file)
    t.image.colorspace_settings.name = 'Non-Color'
    links.new(t.outputs["Color"], bsdf_node.inputs["Roughness"])

met_file = os.path.join(TEX_DIR, "texture_metallic.png")
if os.path.exists(met_file):
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(met_file)
    t.image.colorspace_settings.name = 'Non-Color'
    links.new(t.outputs["Color"], bsdf_node.inputs["Metallic"])

# 4. Creación de Animaciones Cinemáticas con Curvas Bezier
bpy.context.view_layer.objects.active = arm_obj
arm_obj.animation_data_create()

for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

# Obtener huesos del esqueleto Mixamo
pb = arm_obj.pose.bones
b_hips      = pb.get("mixamorig:Hips")
b_spine1    = pb.get("mixamorig:Spine1")
b_spine2    = pb.get("mixamorig:Spine2")
b_chest     = b_spine2
b_neck      = pb.get("mixamorig:Neck")
b_head      = pb.get("mixamorig:Head")
b_l_sh      = pb.get("mixamorig:LeftShoulder")
b_l_arm     = pb.get("mixamorig:LeftArm")
b_l_fa      = pb.get("mixamorig:LeftForeArm")
b_l_hand    = pb.get("mixamorig:LeftHand")
b_r_sh      = pb.get("mixamorig:RightShoulder")
b_r_arm     = pb.get("mixamorig:RightArm")
b_r_fa      = pb.get("mixamorig:RightForeArm")
b_r_hand    = pb.get("mixamorig:RightHand")

def key_bone(bone, deg_tuple, frame):
    if not bone: return
    bone.rotation_mode = 'XYZ'
    bone.rotation_euler = (math.radians(deg_tuple[0]), math.radians(deg_tuple[1]), math.radians(deg_tuple[2]))
    bone.keyframe_insert(data_path="rotation_euler", frame=frame)

def smooth_action_curves(action):
    """Convierte todas las curvas de animación a BEZIER suave con AUTO_CLAMPED en Blender 5.2"""
    fcurves = []
    if hasattr(action, 'layers'):
        for l in action.layers:
            for s in l.strips:
                for cb in s.channelbags:
                    fcurves.extend(cb.fcurves)
    elif hasattr(action, 'fcurves'):
        fcurves = list(action.fcurves)
    for fc in fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'


# -----------------------------------------------------------------------------------
# A. IDLE (120 frames = 4.0 segundos a 30fps): Respiración y vida orgánica continua
# -----------------------------------------------------------------------------------
print("-> Creando animación cinemática: Idle (120f)...")
act_idle = bpy.data.actions.new("Idle")
arm_obj.animation_data.action = act_idle

idle_data = [
    # Frame, Spine1, Spine2 (Pecho), Clavícula L, Brazo L, Cuello/Cabeza, Cadera
    (1,   (0,0,0),       (0,0,0),      (0,0,0),      (0,0,0),      (0,0,0),     (0,0,0)),
    (30,  (0.8, 0, 0.4), (2.2, 0, 0),  (0.8, 0, 0.5),(-1.5,0,-1.2),(-1.2,0,1.0),(-0.3,0,0.2)),
    (60,  (0,0,0),       (0,0,0),      (0,0,0),      (0,0,0),      (0,0,0),     (0,0,0)),
    (90,  (-0.6,0,-0.3), (-1.4, 0, 0), (-0.5,0,-0.3),(1.0,0,0.8),  (0.8,0,-0.8),(0.2,0,-0.2)),
    (120, (0,0,0),       (0,0,0),      (0,0,0),      (0,0,0),      (0,0,0),     (0,0,0))
]

for f, sp1, sp2, sh, arm, hd, hp in idle_data:
    key_bone(b_spine1, sp1, f)
    key_bone(b_chest, sp2, f)
    key_bone(b_l_sh, sh, f)
    key_bone(b_l_arm, arm, f)
    key_bone(b_head, hd, f)
    key_bone(b_hips, hp, f)

smooth_action_curves(act_idle)

# -----------------------------------------------------------------------------------
# B. WAVE (120 frames): Saludo caribeño amplio, fluido, con arrastre de muñeca y cabeza
# -----------------------------------------------------------------------------------
print("-> Creando animación cinemática: Wave (120f)...")
act_wave = bpy.data.actions.new("Wave")
arm_obj.animation_data.action = act_wave

wave_data = [
    # f, L_Shoulder, L_Arm, L_ForeArm, L_Hand, Spine2, Head
    # 1. Neutral
    (1,   (0,0,0),       (0,0,0),         (0,0,0),         (0,0,0),      (0,0,0),      (0,0,0)),
    # 2. Anticipación: hombro sube, brazo se prepara con codo doblado
    (15,  (-6, 2, 4),    (-4, 0, 25),     (10, 0, 30),     (-15, 0, 0),  (1, 0, -2),   (-2, 0, 3)),
    # 3. Brazo alcanza altura de saludo (mano alta)
    (28,  (-10, 3, 6),   (-6, 0, 52),     (12, 0, 48),     (8, 0, -5),   (2, 0, -3),   (-4, 0, 8)),
    # 4. Onda 1 - Hacia afuera
    (38,  (-10, 3, 6),   (-6, 0, 54),     (-18, 0, 48),    (-20, 0, -5), (2.5, 0, -3), (-5, 0, 10)),
    # 5. Onda 1 - Hacia adentro
    (48,  (-9, 2, 5),    (-5, 0, 52),     (18, 0, 46),     (18, 0, -2),  (2, 0, -2),   (-3, 0, 6)),
    # 6. Onda 2 - Hacia afuera con energía
    (58,  (-10, 3, 6),   (-6, 0, 55),     (-20, 0, 48),    (-22, 0, -5), (2.5, 0, -3), (-6, 0, 11)),
    # 7. Onda 2 - Hacia adentro
    (68,  (-9, 2, 5),    (-5, 0, 52),     (16, 0, 46),     (16, 0, -2),  (2, 0, -2),   (-3, 0, 5)),
    # 8. Onda 3 - Saludo final suave
    (78,  (-8, 2, 4),    (-5, 0, 50),     (-12, 0, 44),    (-12, 0, -4), (1.5, 0, -1), (-4, 0, 8)),
    # 9. Inicia descenso con amortiguación
    (92,  (-5, 1, 2),    (-3, 0, 30),     (8, 0, 25),      (10, 0, 0),   (1, 0, -1),   (-2, 0, 4)),
    # 10. Retorno perfecto a neutro
    (120, (0,0,0),       (0,0,0),         (0,0,0),         (0,0,0),      (0,0,0),      (0,0,0))
]

for f, sh, arm, fa, hd_l, sp2, hd in wave_data:
    key_bone(b_l_sh, sh, f)
    key_bone(b_l_arm, arm, f)
    key_bone(b_l_fa, fa, f)
    key_bone(b_l_hand, hd_l, f)
    key_bone(b_spine2, sp2, f)
    key_bone(b_head, hd, f)

smooth_action_curves(act_wave)

# -----------------------------------------------------------------------------------
# C. TALK (120 frames): Gesticulación conversacional costeña con cabeza y ambas manos
# -----------------------------------------------------------------------------------
print("-> Creando animación cinemática: Talk (120f)...")
act_talk = bpy.data.actions.new("Talk")
arm_obj.animation_data.action = act_talk

talk_data = [
    # f, Spine2, Neck, Head, L_Shoulder, L_Arm, L_ForeArm, L_Hand, R_Shoulder, R_Arm, R_ForeArm, R_Hand
    (1,   (0,0,0),       (0,0,0),      (0,0,0),       (0,0,0),    (0,0,0),       (0,0,0),     (0,0,0),      (0,0,0),    (0,0,0),       (0,0,0),       (0,0,0)),
    (20,  (2.0, 0, 1.0), (1.0, 0, 2),  (4.0, 0, 3),   (-4, 0, 2), (-3, 0, 20),   (6, 0, 25),  (-8, 0, 5),   (-2, 0, -1),(-2, 0, 10),   (-10, 0, -12), (-5, 0, -4)),
    (40,  (0.5, 0, 0.0), (-0.5, 0, -1),(-2.0, 0, -1), (0, 0, 0),  (-1, 0, 10),   (2, 0, 15),  (4, 0, 0),    (0, 0, 0),  (0, 0, 4),     (-4, 0, -5),   (0, 0, 0)),
    (60,  (2.5, 0, 1.2), (1.5, 0, 2),  (5.0, 0, 4),   (-5, 0, 3), (-4, 0, 24),   (8, 0, 30),  (-10, 0, 6),  (-3, 0, -1),(-3, 0, 12),   (-12, 0, -15), (-6, 0, -5)),
    (80,  (1.0, 0, -0.5),(-0.2, 0, -2),(-1.5, 0, -2), (-1, 0, 0), (-2, 0, 14),   (4, 0, 18),  (2, 0, 2),    (-1, 0, 0), (-1, 0, 6),    (-6, 0, -8),   (-2, 0, -2)),
    (100, (1.8, 0, 0.5), (0.8, 0, 1),  (3.0, 0, 2),   (-3, 0, 1), (-2, 0, 18),   (5, 0, 22),  (-6, 0, 4),   (-2, 0, 0), (-2, 0, 8),    (-8, 0, -10),  (-4, 0, -3)),
    (120, (0,0,0),       (0,0,0),      (0,0,0),       (0,0,0),    (0,0,0),       (0,0,0),     (0,0,0),      (0,0,0),    (0,0,0),       (0,0,0),       (0,0,0))
]

for f, sp2, nk, hd, l_sh, l_arm, l_fa, l_hd, r_sh, r_arm, r_fa, r_hd in talk_data:
    key_bone(b_spine2, sp2, f)
    key_bone(b_neck, nk, f)
    key_bone(b_head, hd, f)
    key_bone(b_l_sh, l_sh, f)
    key_bone(b_l_arm, l_arm, f)
    key_bone(b_l_fa, l_fa, f)
    key_bone(b_l_hand, l_hd, f)
    key_bone(b_r_sh, r_sh, f)
    key_bone(b_r_arm, r_arm, f)
    key_bone(b_r_fa, r_fa, f)
    key_bone(b_r_hand, r_hd, f)

smooth_action_curves(act_talk)

# -----------------------------------------------------------------------------------
# D. EXPLAIN (120 frames): Explicación costeña con AMBAS MANOS abiertas y gesticulando
# -----------------------------------------------------------------------------------
print("-> Creando animación cinemática: Explain con ambas manos (120f)...")
act_explain = bpy.data.actions.new("Explain")
arm_obj.animation_data.action = act_explain

explain_data = [
    # f, Spine2, Neck, Head, L_Shoulder, L_Arm, L_ForeArm, L_Hand, R_Shoulder, R_Arm, R_ForeArm, R_Hand
    # 1. Neutro
    (1,   (0,0,0),       (0,0,0),      (0,0,0),       (0,0,0),    (0,0,0),       (0,0,0),      (0,0,0),      (0,0,0),    (0,0,0),       (0,0,0),       (0,0,0)),
    # 2. Anticipación y elevación de ambas manos hacia el pecho
    (18,  (2.5, 0, 1.0), (1.5, 0, 2),  (4.0, 0, 4),   (-4, 1, 3), (-4, 0, 22),   (8, 0, 26),   (-10, 4, 6),  (-4, -1, -2),(-4, 0, 18),  (-15, 0, -18), (-8, -4, -6)),
    # 3. Beat 1: Apertura amplia de manos explicando ("Mira cómo es la vaina...")
    (34,  (3.8, 0, 1.5), (2.0, 0, 3),  (6.5, 0, 5),   (-6, 2, 4), (-6, 0, 35),   (14, 0, 42),  (-18, 10, 12),(-5, -2, -3),(-6, 0, 26),  (-24, 0, -30), (-14, -8, -10)),
    # 4. Beat 2: Inflexión y cambio de ritmo con manos articulando puntos
    (54,  (2.2, 0, 0.8), (0.8, 0, 1),  (2.5, 0, 2),   (-3, 1, 2), (-4, 0, 24),   (8, 0, 28),   (-8, 5, 5),   (-3, -1, -2),(-4, 0, 20),  (-16, 0, -20), (-6, -4, -4)),
    # 5. Beat 3: Énfasis apasionado con ambas palmas abiertas hacia el usuario ("¡Pilla tú!")
    (74,  (4.2, 0, 1.8), (2.2, 0, 3),  (7.0, 0, 6),   (-6, 2, 5), (-6, 0, 38),   (16, 0, 45),  (-20, 12, 14),(-6, -2, -3),(-6, 0, 30),  (-26, 0, -34), (-16, -10, -12)),
    # 6. Descenso gradual y amortiguado
    (96,  (1.8, 0, 0.5), (0.6, 0, 0),  (2.0, 0, 2),   (-2, 1, 1), (-3, 0, 18),   (6, 0, 20),   (-6, 3, 3),   (-2, 0, -1),(-2, 0, 12),   (-10, 0, -12), (-4, -2, -2)),
    # 7. Neutro perfecto
    (120, (0,0,0),       (0,0,0),      (0,0,0),       (0,0,0),    (0,0,0),       (0,0,0),      (0,0,0),      (0,0,0),    (0,0,0),       (0,0,0),       (0,0,0))
]

for f, sp2, nk, hd, l_sh, l_arm, l_fa, l_hd, r_sh, r_arm, r_fa, r_hd in explain_data:
    key_bone(b_spine2, sp2, f)
    key_bone(b_neck, nk, f)
    key_bone(b_head, hd, f)
    key_bone(b_l_sh, l_sh, f)
    key_bone(b_l_arm, l_arm, f)
    key_bone(b_l_fa, l_fa, f)
    key_bone(b_l_hand, l_hd, f)
    key_bone(b_r_sh, r_sh, f)
    key_bone(b_r_arm, r_arm, f)
    key_bone(b_r_fa, r_fa, f)
    key_bone(b_r_hand, r_hd, f)

smooth_action_curves(act_explain)

# -----------------------------------------------------------------------------------
# E. LAUGH (120 frames): Carcajada costeña rítmica con rebote de pecho y cabeza
# -----------------------------------------------------------------------------------
print("-> Creando animación cinemática: Laugh (120f)...")
act_laugh = bpy.data.actions.new("Laugh")
arm_obj.animation_data.action = act_laugh

laugh_data = [
    # f, Spine2, Neck, Head, L_Shoulder, L_Arm
    (1,   (0,0,0),       (0,0,0),      (0,0,0),       (0,0,0),     (0,0,0)),
    (12,  (2.5, 0, 0),   (1.0, 0, 0),  (3.0, 0, 0),   (-2, 0, 0),  (0, 0, 4)),
    (24,  (-5.5, 0, 0),  (-3.0, 0, 0), (-14.0, 0, 3), (-4, 0, 2),  (0, 0, 8)),
    (34,  (-1.0, 0, 0),  (-0.5, 0, 0), (-4.0, 0, 0),  (-1, 0, 0),  (0, 0, 2)),
    (46,  (-6.0, 0, 0),  (-3.5, 0, 0), (-16.0, 0, -2),(-5, 0, 2),  (0, 0, 9)),
    (56,  (-1.2, 0, 0),  (-0.5, 0, 0), (-5.0, 0, 0),  (-1, 0, 0),  (0, 0, 3)),
    (68,  (-4.0, 0, 0),  (-2.0, 0, 0), (-10.0, 0, 2), (-3, 0, 1),  (0, 0, 6)),
    (84,  (-1.0, 0, 0),  (-0.5, 0, 0), (-3.0, 0, -1), (0, 0, 0),   (0, 0, 2)),
    (100, (0.5, 0, 0),   (0.2, 0, 0),  (1.0, 0, 1),   (0, 0, 0),   (0, 0, 0)),
    (120, (0,0,0),       (0,0,0),      (0,0,0),       (0,0,0),     (0,0,0))
]

for f, sp2, nk, hd, l_sh, l_arm in laugh_data:
    key_bone(b_spine2, sp2, f)
    key_bone(b_neck, nk, f)
    key_bone(b_head, hd, f)
    key_bone(b_l_sh, l_sh, f)
    key_bone(b_l_arm, l_arm, f)

smooth_action_curves(act_laugh)

# -----------------------------------------------------------------------------------
# 5. Empaquetar pistas NLA con action_slot asignado para Blender 5.2
# -----------------------------------------------------------------------------------
print("-> Empaquetando pistas NLA con compatibilidad Blender 5.2...")
for act in [act_idle, act_wave, act_talk, act_explain, act_laugh]:
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = act.name
    strip = track.strips.new(act.name, 1, act)
    if hasattr(act, 'slots') and len(act.slots) > 0:
        strip.action_slot = act.slots[0]

# Dejar Idle como la acción activa por defecto
arm_obj.animation_data.action = act_idle

# 6. Exportar GLB de alta fidelidad
print(f"-> Exportando modelo a {OUTPUT_GLB}...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_yup=True,
    export_animations=True,
    export_nla_strips=True,
    export_def_bones=True,
    export_materials='EXPORT',
    export_attributes=True
)

print(f">>> ¡ÉXITO TOTAL! Modelo con animaciones cinemáticas exportado en: {OUTPUT_GLB}")
