"""
Costeño AI - Integrador y Optimizador del Personaje 3D Subido por el Usuario
Importa base_basic_pbr.fbx, configura materiales PBR completos,
genera Shape Keys para lip-sync y expresiones faciales,
crea el Armature de deformación con animaciones NLA y exporta a assets/character.glb.
"""

import bpy
import bmesh
import math
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "assets", "4021aca1-2d35-4ba4-9d69-3347285a59be")
FBX_PATH = os.path.join(UPLOAD_DIR, "base_basic_pbr.fbx")
OUTPUT_GLB = os.path.join(BASE_DIR, "assets", "character.glb")
BACKUP_GLB = os.path.join(BASE_DIR, "assets", "character_procedural_backup.glb")

print(">>> Iniciando integración del nuevo personaje costeño subido por el usuario...")

# 1. Respaldo del character.glb anterior si existe
if os.path.exists(OUTPUT_GLB) and not os.path.exists(BACKUP_GLB):
    import shutil
    shutil.copyfile(OUTPUT_GLB, BACKUP_GLB)
    print("Respaldo creado:", BACKUP_GLB)

# 2. Resetear escena
bpy.ops.wm.read_factory_settings(use_empty=True)
for col in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions, bpy.data.images):
    for item in list(col):
        col.remove(item, do_unlink=True)

# 3. Importar FBX
print("-> Importando FBX:", FBX_PATH)
bpy.ops.import_scene.fbx(filepath=FBX_PATH)

obj = bpy.data.objects.get("model")
if not obj:
    for o in bpy.data.objects:
        if o.type == 'MESH':
            obj = o
            break

obj.name = "Costeno_Character_Mesh"
bpy.context.view_layer.objects.active = obj
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)

# 4. Configurar Material PBR con texturas
print("-> Vinculando mapas de texturas PBR...")
mat = obj.data.materials[0] if obj.data.materials else bpy.data.materials.new(name="M_Costeno_PBR")
if not obj.data.materials:
    obj.data.materials.append(mat)

mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output_node = nodes.new("ShaderNodeOutputMaterial")
bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

# Textura Diffuse / Albedo
diff_path = os.path.join(UPLOAD_DIR, "texture_diffuse.png")
if os.path.exists(diff_path):
    diff_img = bpy.data.images.load(diff_path)
    tex_diff = nodes.new("ShaderNodeTexImage")
    tex_diff.image = diff_img
    links.new(tex_diff.outputs["Color"], bsdf_node.inputs["Base Color"])

# Textura Normal
norm_path = os.path.join(UPLOAD_DIR, "texture_normal.png")
if os.path.exists(norm_path):
    norm_img = bpy.data.images.load(norm_path)
    norm_img.colorspace_settings.name = 'Non-Color'
    tex_norm = nodes.new("ShaderNodeTexImage")
    tex_norm.image = norm_img
    norm_map = nodes.new("ShaderNodeNormalMap")
    links.new(tex_norm.outputs["Color"], norm_map.inputs["Color"])
    links.new(norm_map.outputs["Normal"], bsdf_node.inputs["Normal"])

# Textura Roughness
rough_path = os.path.join(UPLOAD_DIR, "texture_roughness.png")
if os.path.exists(rough_path):
    rough_img = bpy.data.images.load(rough_path)
    rough_img.colorspace_settings.name = 'Non-Color'
    tex_rough = nodes.new("ShaderNodeTexImage")
    tex_rough.image = rough_img
    links.new(tex_rough.outputs["Color"], bsdf_node.inputs["Roughness"])

# Textura Metallic
met_path = os.path.join(UPLOAD_DIR, "texture_metallic.png")
if os.path.exists(met_path):
    met_img = bpy.data.images.load(met_path)
    met_img.colorspace_settings.name = 'Non-Color'
    tex_met = nodes.new("ShaderNodeTexImage")
    tex_met.image = met_img
    links.new(tex_met.outputs["Color"], bsdf_node.inputs["Metallic"])

# 5. Generar Shape Keys para el Rostro (Lip-Sync y Emociones)
print("-> Creando Shape Keys para Lip-Sync y Expresiones...")
sk_basis = obj.shape_key_add(name="Basis")

# Coordenadas clave de la boca del personaje: x ≈ 0, y ≈ -0.22, z ≈ 1.38
mouth_center_z = 1.38
mouth_center_y = -0.22

def apply_mouth_shape_key(name, deform_fn):
    sk = obj.shape_key_add(name=name)
    sk.interpolation = 'KEY_LINEAR'
    
    for i, v in enumerate(obj.data.vertices):
        # Filtro de vértices de la boca y mandíbula
        dx = v.co.x
        dy = v.co.y
        dz = v.co.z
        
        dist_x = abs(dx)
        dist_z = abs(dz - mouth_center_z)
        
        # Vértices frontales de la boca
        if dist_x < 0.22 and dist_z < 0.12 and dy < -0.14:
            # Factor de caída gaussiano/suave
            weight = math.cos(min(dist_x / 0.22, 1.0) * (math.pi / 2)) * math.cos(min(dist_z / 0.12, 1.0) * (math.pi / 2))
            disp_x, disp_y, disp_z = deform_fn(dx, dy, dz, weight)
            sk.data[i].co.x += disp_x
            sk.data[i].co.y += disp_y
            sk.data[i].co.z += disp_z

# A. Visemas para el habla
# 1. viseme_aa: Mandíbula y labio inferior bajan abriendo la boca
apply_mouth_shape_key(
    "viseme_aa",
    lambda x, y, z, w: (0, -0.015 * w, -0.045 * w if z <= mouth_center_z else 0.01 * w)
)

# 2. viseme_O: Labios redondeados en 'O'
apply_mouth_shape_key(
    "viseme_O",
    lambda x, y, z, w: (-x * 0.25 * w, -0.035 * w, -0.03 * w if z <= mouth_center_z else 0.015 * w)
)

# 3. viseme_E: Boca ancha horizontal
apply_mouth_shape_key(
    "viseme_E",
    lambda x, y, z, w: (x * 0.20 * w, -0.01 * w, -0.015 * w if z <= mouth_center_z else 0.01 * w)
)

# 4. viseme_I: Sonrisa horizontal tensa
apply_mouth_shape_key(
    "viseme_I",
    lambda x, y, z, w: (x * 0.28 * w, -0.005 * w, -0.008 * w)
)

# 5. viseme_U: Trompita / labios hacia adelante
apply_mouth_shape_key(
    "viseme_U",
    lambda x, y, z, w: (-x * 0.35 * w, -0.045 * w, -0.015 * w)
)

# 6. viseme_PP: Labios comprimidos
apply_mouth_shape_key(
    "viseme_PP",
    lambda x, y, z, w: (0, 0.015 * w, 0.018 * w if z < mouth_center_z else -0.018 * w)
)

# 7. viseme_FF: Labio inferior hacia arriba y atrás
apply_mouth_shape_key(
    "viseme_FF",
    lambda x, y, z, w: (0, 0.02 * w, 0.025 * w if z < mouth_center_z else 0)
)

# 8. viseme_DD: Boca entreabierta
apply_mouth_shape_key(
    "viseme_DD",
    lambda x, y, z, w: (x * 0.08 * w, 0, -0.02 * w if z < mouth_center_z else 0)
)

# 9. viseme_SS: Dientes juntos
apply_mouth_shape_key(
    "viseme_SS",
    lambda x, y, z, w: (x * 0.15 * w, -0.005 * w, -0.01 * w)
)

# B. Expresiones emocionales
# Happy: Comisuras suben
apply_mouth_shape_key(
    "happy",
    lambda x, y, z, w: (x * 0.15 * w, -0.01 * w, 0.035 * w if abs(x) > 0.04 else 0.01 * w)
)

# Laugh: Gran apertura alegre
apply_mouth_shape_key(
    "laugh",
    lambda x, y, z, w: (x * 0.22 * w, -0.025 * w, -0.05 * w if z <= mouth_center_z else 0.025 * w)
)

# Surprised: O grande
apply_mouth_shape_key(
    "surprised",
    lambda x, y, z, w: (-x * 0.20 * w, -0.04 * w, -0.055 * w if z <= mouth_center_z else 0.03 * w)
)

# Confused: Mueca asimétrica
apply_mouth_shape_key(
    "confused",
    lambda x, y, z, w: (0.015 * w, 0, 0.03 * w if x > 0 else -0.02 * w)
)

# Thinking: Labios fruncidos hacia un lado
apply_mouth_shape_key(
    "thinking",
    lambda x, y, z, w: (-0.025 * w, -0.01 * w, 0.015 * w if x < 0 else -0.01 * w)
)

# Excited: Sonrisa amplia radiante
apply_mouth_shape_key(
    "excited",
    lambda x, y, z, w: (x * 0.25 * w, -0.02 * w, 0.04 * w if abs(x) > 0.03 else -0.02 * w)
)

print(f"-> Shape Keys creadas: {len(obj.data.shape_keys.key_blocks)}")

# 6. Crear Armature Jerárquico para Seguimiento de Mirada, Respiración y Gestos
print("-> Creando Armature de Animación...")
arm_data = bpy.data.armatures.new("Costeno_Rig")
arm_obj = bpy.data.objects.new("Costeno_Armature", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj

bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

b_root = eb.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0, 0.2)

b_hips = eb.new("Hips")
b_hips.head = (0, 0, 0.95)
b_hips.tail = (0, 0, 1.15)
b_hips.parent = b_root

b_spine = eb.new("Spine")
b_spine.head = (0, 0, 1.15)
b_spine.tail = (0, 0, 1.30)
b_spine.parent = b_hips

b_chest = eb.new("Chest")
b_chest.head = (0, 0, 1.30)
b_chest.tail = (0, 0, 1.48)
b_chest.parent = b_spine

b_neck = eb.new("Neck")
b_neck.head = (0, 0, 1.48)
b_neck.tail = (0, 0, 1.58)
b_neck.parent = b_chest

b_head = eb.new("Head")
b_head.head = (0, 0, 1.58)
b_head.tail = (0, 0, 1.95)
b_head.parent = b_neck

# Extremidades
for prefix, x_s in [("L", -1.0), ("R", 1.0)]:
    b_arm = eb.new(f"UpperArm.{prefix}")
    b_arm.head = (x_s * 0.22, 0, 1.35)
    b_arm.tail = (x_s * 0.55, -0.15, 1.15)
    b_arm.parent = b_chest
    
    b_leg = eb.new(f"Thigh.{prefix}")
    b_leg.head = (x_s * 0.16, 0, 0.95)
    b_leg.tail = (x_s * 0.16, -0.10, 0.10)
    b_leg.parent = b_hips

bpy.ops.object.mode_set(mode='OBJECT')

# 7. Asignar Pesos de Deformación (Vertex Groups)
print("-> Asignando pesos de deformación al personaje...")
obj.parent = arm_obj
mod = obj.modifiers.new("ArmatureMod", type='ARMATURE')
mod.object = arm_obj
mod.use_vertex_groups = True

# Crear vertex groups con gradientes suaves por altura anatómica Z
bone_heights = [
    ("Root", 0.0, 0.3),
    ("Thigh.L", 0.1, 0.95, -1.0),
    ("Thigh.R", 0.1, 0.95, 1.0),
    ("Hips", 0.85, 1.15),
    ("Spine", 1.10, 1.30),
    ("Chest", 1.25, 1.48),
    ("Neck", 1.45, 1.58),
    ("Head", 1.52, 2.05),
    ("UpperArm.L", 1.05, 1.45, -1.0),
    ("UpperArm.R", 1.05, 1.45, 1.0),
]

# Inicializar grupos
for b in arm_data.bones:
    obj.vertex_groups.new(name=b.name)

# Asignar cada vértice según su proximidad anatómica
vg_head = obj.vertex_groups["Head"]
vg_chest = obj.vertex_groups["Chest"]
vg_spine = obj.vertex_groups["Spine"]
vg_hips = obj.vertex_groups["Hips"]
vg_arm_l = obj.vertex_groups["UpperArm.L"]
vg_arm_r = obj.vertex_groups["UpperArm.R"]
vg_leg_l = obj.vertex_groups["Thigh.L"]
vg_leg_r = obj.vertex_groups["Thigh.R"]

for i, v in enumerate(obj.data.vertices):
    z = v.co.z
    x = v.co.x
    
    if z >= 1.50:
        vg_head.add([i], 1.0, 'REPLACE')
    elif 1.28 <= z < 1.50:
        if abs(x) > 0.28:
            if x < 0:
                vg_arm_l.add([i], 0.9, 'REPLACE')
            else:
                vg_arm_r.add([i], 0.9, 'REPLACE')
        else:
            w_h = (z - 1.28) / (1.50 - 1.28)
            vg_head.add([i], w_h * 0.4, 'REPLACE')
            vg_chest.add([i], 1.0 - w_h * 0.4, 'REPLACE')
    elif 1.10 <= z < 1.28:
        if abs(x) > 0.32:
            if x < 0:
                vg_arm_l.add([i], 0.9, 'REPLACE')
            else:
                vg_arm_r.add([i], 0.9, 'REPLACE')
        else:
            vg_spine.add([i], 1.0, 'REPLACE')
    elif 0.85 <= z < 1.10:
        vg_hips.add([i], 1.0, 'REPLACE')
    else:
        if x < 0:
            vg_leg_l.add([i], 1.0, 'REPLACE')
        else:
            vg_leg_r.add([i], 1.0, 'REPLACE')

# 8. Animaciones NLA
print("-> Creando Clips NLA (Idle, Talk, Wave, Laugh, Point)...")
arm_obj.animation_data_create()

def insert_rot(pb, deg, frame):
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (math.radians(deg[0]), math.radians(deg[1]), math.radians(deg[2]))
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)

pb_chest = arm_obj.pose.bones.get("Chest")
pb_head = arm_obj.pose.bones.get("Head")
pb_arm_r = arm_obj.pose.bones.get("UpperArm.R")
pb_arm_l = arm_obj.pose.bones.get("UpperArm.L")

# Idle (Respiración y balanceo suave)
act_idle = bpy.data.actions.new("Idle")
arm_obj.animation_data.action = act_idle
for f, rot_c, rot_h in [(1, (0,0,0), (0,0,0)), (30, (2.2, 0, 0), (-1.2, 0, 0.8)), (60, (0,0,0), (0,0,0))]:
    insert_rot(pb_chest, rot_c, f)
    insert_rot(pb_head, rot_h, f)

# Talk (Gesticulación animada)
act_talk = bpy.data.actions.new("Talk")
arm_obj.animation_data.action = act_talk
insert_rot(pb_head, (0,0,0), 1)
insert_rot(pb_head, (4, 0, 2.5), 15)
insert_rot(pb_head, (-2.5, 0, -2.5), 35)
insert_rot(pb_head, (0,0,0), 60)
insert_rot(pb_chest, (1.5, 0, 1), 15)
insert_rot(pb_chest, (-1, 0, -1), 35)
insert_rot(pb_chest, (0,0,0), 60)

# Wave (Saludo costeño)
act_wave = bpy.data.actions.new("Wave")
arm_obj.animation_data.action = act_wave
insert_rot(pb_arm_r, (0,0,0), 1)
insert_rot(pb_arm_r, (15, -15, -45), 15)
insert_rot(pb_arm_r, (25, -20, -65), 30)
insert_rot(pb_arm_r, (15, -15, -45), 45)
insert_rot(pb_arm_r, (0,0,0), 60)

# Laugh (Carcajada)
act_laugh = bpy.data.actions.new("Laugh")
arm_obj.animation_data.action = act_laugh
insert_rot(pb_head, (-12, 0, 0), 15)
insert_rot(pb_chest, (-6, 0, 0), 15)
insert_rot(pb_head, (-16, 0, 0), 28)
insert_rot(pb_chest, (-4, 0, 0), 28)
insert_rot(pb_head, (0,0,0), 60)
insert_rot(pb_chest, (0,0,0), 60)

# Empaquetar NLA strips
for act in [act_idle, act_talk, act_wave, act_laugh]:
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = act.name
    track.strips.new(act.name, 1, act)

# 9. Exportar a GLB
print(f"-> Exportando personaje a {OUTPUT_GLB}...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_yup=True,
    export_animations=True,
    export_nla_strips=True,
    export_def_bones=True,
    export_morph=True,
    export_morph_normal=True,
    export_materials='EXPORT',
    export_attributes=True
)

print(f">>> ¡ÉXITO! Personaje integrado y exportado correctamente en: {OUTPUT_GLB}")
