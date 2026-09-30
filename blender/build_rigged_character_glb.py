"""
Costeño AI - Compilador Maestro del Personaje Riggeado de Mixamo (baselo.fbx)
Configura materiales PBR completos, escala a metros,
crea animaciones NLA profesionales (Idle, Wave, Talk, Explain, Laugh)
y exporta el modelo maestro a assets/character.glb.
"""

import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FBX_PATH = os.path.join(BASE_DIR, "assets", "baselo.fbx")
TEX_DIR = os.path.join(BASE_DIR, "assets", "4021aca1-2d35-4ba4-9d69-3347285a59be")
OUTPUT_GLB = os.path.join(BASE_DIR, "assets", "character.glb")

print(">>> Compilando personaje costeño riggeado con animaciones NLA...")

# 1. Resetear escena
bpy.ops.wm.read_factory_settings(use_empty=True)
for col in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions, bpy.data.images):
    for item in list(col):
        col.remove(item, do_unlink=True)

# 2. Importar FBX de Mixamo
print("-> Importando FBX de Mixamo:", FBX_PATH)
bpy.ops.import_scene.fbx(filepath=FBX_PATH)

arm_obj = bpy.data.objects.get("Armature")
mesh_obj = bpy.data.objects.get("model")

if not arm_obj or not mesh_obj:
    for o in bpy.data.objects:
        if o.type == 'ARMATURE': arm_obj = o
        elif o.type == 'MESH': mesh_obj = o

# Escalar a metros (1.90 m)
arm_obj.scale = (1.0, 1.0, 1.0)
mesh_obj.scale = (1.0, 1.0, 1.0)
mesh_obj.name = "Costeno_Mesh"
arm_obj.name = "Costeno_Rig"

# 3. Configurar Material PBR Completo
print("-> Configurando mapas PBR (Diffuse, Normal, Roughness, Metallic)...")
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

# Diffuse
diff_file = os.path.join(TEX_DIR, "texture_diffuse.png")
if os.path.exists(diff_file):
    tex_diff = nodes.new("ShaderNodeTexImage")
    tex_diff.image = bpy.data.images.load(diff_file)
    links.new(tex_diff.outputs["Color"], bsdf_node.inputs["Base Color"])

# Normal
norm_file = os.path.join(TEX_DIR, "texture_normal.png")
if os.path.exists(norm_file):
    tex_norm = nodes.new("ShaderNodeTexImage")
    tex_norm.image = bpy.data.images.load(norm_file)
    tex_norm.image.colorspace_settings.name = 'Non-Color'
    norm_map = nodes.new("ShaderNodeNormalMap")
    links.new(tex_norm.outputs["Color"], norm_map.inputs["Color"])
    links.new(norm_map.outputs["Normal"], bsdf_node.inputs["Normal"])

# Roughness
rough_file = os.path.join(TEX_DIR, "texture_roughness.png")
if os.path.exists(rough_file):
    tex_rough = nodes.new("ShaderNodeTexImage")
    tex_rough.image = bpy.data.images.load(rough_file)
    tex_rough.image.colorspace_settings.name = 'Non-Color'
    links.new(tex_rough.outputs["Color"], bsdf_node.inputs["Roughness"])

# Metallic
met_file = os.path.join(TEX_DIR, "texture_metallic.png")
if os.path.exists(met_file):
    tex_met = nodes.new("ShaderNodeTexImage")
    tex_met.image = bpy.data.images.load(met_file)
    tex_met.image.colorspace_settings.name = 'Non-Color'
    links.new(tex_met.outputs["Color"], bsdf_node.inputs["Metallic"])

# 4. Crear Animaciones NLA Profesionales
print("-> Creando Clips NLA: Idle, Wave, Talk, Explain, Laugh...")
bpy.context.view_layer.objects.active = arm_obj
arm_obj.animation_data_create()

# Limpiar acciones anteriores
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

def set_bone_key(pb, euler_deg, frame):
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)

pb_spine = arm_obj.pose.bones.get("mixamorig:Spine1")
pb_chest = arm_obj.pose.bones.get("mixamorig:Spine2")
pb_neck = arm_obj.pose.bones.get("mixamorig:Neck")
pb_head = arm_obj.pose.bones.get("mixamorig:Head")
pb_l_arm = arm_obj.pose.bones.get("mixamorig:LeftArm")
pb_l_forearm = arm_obj.pose.bones.get("mixamorig:LeftForeArm")
pb_l_hand = arm_obj.pose.bones.get("mixamorig:LeftHand")

# A. Idle (Ciclo de respiración caribeña y balanceo suave)
act_idle = bpy.data.actions.new("Idle")
arm_obj.animation_data.action = act_idle
for f, rot_c, rot_h, rot_a in [
    (1, (0,0,0), (0,0,0), (0,0,0)),
    (30, (2.0, 0, 0), (-1.2, 0, 1.0), (-2.0, -1.0, -2.0)),
    (60, (0,0,0), (0,0,0), (0,0,0))
]:
    if pb_chest: set_bone_key(pb_chest, rot_c, f)
    if pb_head: set_bone_key(pb_head, rot_h, f)
    if pb_l_arm: set_bone_key(pb_l_arm, rot_a, f)

# B. Wave (Saludo costeño alegre con el brazo libre)
act_wave = bpy.data.actions.new("Wave")
arm_obj.animation_data.action = act_wave
if pb_l_arm and pb_l_forearm:
    # Inicio
    set_bone_key(pb_l_arm, (0, 0, 0), 1)
    set_bone_key(pb_l_forearm, (0, 0, 0), 1)
    if pb_head: set_bone_key(pb_head, (0, 0, 0), 1)
    
    # Levantar brazo
    set_bone_key(pb_l_arm, (-25, -20, -45), 15)
    set_bone_key(pb_l_forearm, (-35, 0, -40), 15)
    if pb_head: set_bone_key(pb_head, (-5, 10, 8), 15)
    
    # Onda hacia afuera
    set_bone_key(pb_l_forearm, (-45, 0, -60), 25)
    # Onda hacia adentro
    set_bone_key(pb_l_forearm, (-25, 0, -25), 35)
    # Onda hacia afuera
    set_bone_key(pb_l_forearm, (-45, 0, -60), 45)
    
    # Regreso suave a reposo
    set_bone_key(pb_l_arm, (0, 0, 0), 60)
    set_bone_key(pb_l_forearm, (0, 0, 0), 60)
    if pb_head: set_bone_key(pb_head, (0, 0, 0), 60)

# C. Talk (Gesticulación animada conversacional)
act_talk = bpy.data.actions.new("Talk")
arm_obj.animation_data.action = act_talk
for f, rot_h, rot_c, rot_fa in [
    (1, (0,0,0), (0,0,0), (0,0,0)),
    (15, (4, 3, 2), (2, 0, 1), (-15, -8, -12)),
    (35, (-3, -2, -2), (-1, 0, -1), (-8, 5, 8)),
    (60, (0,0,0), (0,0,0), (0,0,0))
]:
    if pb_head: set_bone_key(pb_head, rot_h, f)
    if pb_chest: set_bone_key(pb_chest, rot_c, f)
    if pb_l_forearm: set_bone_key(pb_l_forearm, rot_fa, f)

# D. Explain (Gesto explicativo amplio)
act_explain = bpy.data.actions.new("Explain")
arm_obj.animation_data.action = act_explain
for f, rot_h, rot_arm, rot_fa in [
    (1, (0,0,0), (0,0,0), (0,0,0)),
    (25, (-3, 6, 4), (-18, -12, -25), (-25, -10, -20)),
    (45, (2, -4, -2), (-12, -8, -18), (-18, -5, -15)),
    (60, (0,0,0), (0,0,0), (0,0,0))
]:
    if pb_head: set_bone_key(pb_head, rot_h, f)
    if pb_l_arm: set_bone_key(pb_l_arm, rot_arm, f)
    if pb_l_forearm: set_bone_key(pb_l_forearm, rot_fa, f)

# E. Laugh (Carcajada: cabeza y pecho rebotando de alegría)
act_laugh = bpy.data.actions.new("Laugh")
arm_obj.animation_data.action = act_laugh
for f, rot_h, rot_c in [
    (1, (0,0,0), (0,0,0)),
    (15, (-12, 0, 3), (-6, 0, 0)),
    (28, (-16, 0, -2), (-4, 0, 0)),
    (42, (-10, 0, 2), (-5, 0, 0)),
    (60, (0,0,0), (0,0,0))
]:
    if pb_head: set_bone_key(pb_head, rot_h, f)
    if pb_chest: set_bone_key(pb_chest, rot_c, f)

# Empaquetar pistas NLA para exportación GLB completa
for act in [act_idle, act_wave, act_talk, act_explain, act_laugh]:
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = act.name
    track.strips.new(act.name, 1, act)

# 5. Ancla para la Burbuja 3D
head_end = arm_obj.pose.bones.get("mixamorig:HeadTop_End") or arm_obj.pose.bones.get("mixamorig:Head")

# 6. Exportar a GLB
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

print(f">>> ¡ÉXITO TOTAL! Personaje Mixamo animado y exportado en: {OUTPUT_GLB}")
