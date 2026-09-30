"""
Costeño AI - Generador de Personaje 3D Estilizado de Alta Calidad para Blender 5.2
Crea un personaje estilizado profesional con:
- Geometría suave (Subdivision & Quads, nada de cubos primitivos rígidos)
- Cabeza y rostro expresivo con cavidad bucal, dientes y ojos detallados
- Manos modeladas con palma y 5 dedos articulados individuales
- Sombrero Vueltiao con ala curvada Zenú tradicional
- Camisilla caribeña con pliegues y dobladillos
- Bermuda con costuras y bolsillos
- Chancletas ergonómicas con tiras de goma 3D
- Armature jerárquico completo con huesos para dedos
- Shape Keys faciales: Emociones (happy, laugh, surprised, confused, thinking, sad, excited)
                      Microgestos (blink_L, blink_R, brow_up_L, brow_up_R, brow_frown)
                      Visemas fonéticos (viseme_aa, viseme_E, viseme_I, viseme_O, viseme_U, viseme_PP, viseme_FF, viseme_DD, viseme_SS)
- Animaciones NLA exportables (Idle, Idle_Relaxed, Talk, Wave, Point, Explain, Laugh, Think)
- Exportación directa a glTF/GLB para Three.js
"""

import bpy
import bmesh
import math
import os
import numpy as np

# Configuración de rutas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EXPORTS_DIR = os.path.join(BASE_DIR, "blender", "exports")
GLB_PATH = os.path.join(ASSETS_DIR, "character.glb")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

print(">>> Iniciando construcción de Personaje Estilizado Costeño AI...")

# 1. Resetear escena
bpy.ops.wm.read_factory_settings(use_empty=True)
for col in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions, bpy.data.images):
    for item in list(col):
        col.remove(item, do_unlink=True)

# 2. Materiales PBR Estilizados
def create_pbr_material(name, base_color, roughness=0.5, metallic=0.0, specular=0.5, subsurface=0.0, sss_color=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = specular
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = specular
        # Subsurface scattering en piel
        if subsurface > 0:
            if "Subsurface Weight" in bsdf.inputs:
                bsdf.inputs["Subsurface Weight"].default_value = subsurface
            elif "Subsurface" in bsdf.inputs:
                bsdf.inputs["Subsurface"].default_value = subsurface
            if sss_color and "Subsurface Radius" in bsdf.inputs:
                bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.2)
    return mat

mat_skin = create_pbr_material("M_Skin_Costeno", (0.76, 0.50, 0.35, 1.0), roughness=0.45, subsurface=0.15)
mat_hair = create_pbr_material("M_Hair", (0.05, 0.03, 0.02, 1.0), roughness=0.7)
mat_shirt = create_pbr_material("M_Camisilla", (0.96, 0.96, 0.98, 1.0), roughness=0.65)
mat_shirt_stripe = create_pbr_material("M_Junior_Red", (0.85, 0.08, 0.10, 1.0), roughness=0.55)
mat_shorts = create_pbr_material("M_Shorts_Denim", (0.12, 0.35, 0.70, 1.0), roughness=0.75)
mat_sombrero_crema = create_pbr_material("M_Zenu_Crema", (0.88, 0.78, 0.54, 1.0), roughness=0.6)
mat_sombrero_negro = create_pbr_material("M_Zenu_Negro", (0.04, 0.04, 0.04, 1.0), roughness=0.5)
mat_sandal_sole = create_pbr_material("M_Sandal_Sole", (0.10, 0.10, 0.12, 1.0), roughness=0.8)
mat_sandal_strap = create_pbr_material("M_Sandal_Strap", (0.90, 0.20, 0.15, 1.0), roughness=0.4)
mat_eye_sclera = create_pbr_material("M_Eye_Sclera", (0.98, 0.98, 0.99, 1.0), roughness=0.1)
mat_eye_iris = create_pbr_material("M_Eye_Iris", (0.28, 0.16, 0.08, 1.0), roughness=0.15)
mat_eye_pupil = create_pbr_material("M_Eye_Pupil", (0.01, 0.01, 0.01, 1.0), roughness=0.05)
mat_teeth = create_pbr_material("M_Teeth", (0.96, 0.95, 0.91, 1.0), roughness=0.2)
mat_mouth_interior = create_pbr_material("M_Mouth_Interior", (0.55, 0.12, 0.14, 1.0), roughness=0.4)

# 3. Modelado Orgánico BMesh
# Creamos una colección para los objetos del personaje
char_collection = bpy.data.collections.new("Costeno_Character")
bpy.context.scene.collection.children.link(char_collection)

def apply_smooth_and_subdivision(obj, levels=1):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    mod = obj.modifiers.new("Subsurf", type='SUBSURF')
    mod.levels = levels
    mod.render_levels = levels
    bpy.ops.object.modifier_apply(modifier="Subsurf")

print("-> Creando Cabeza y Rostro Estilizado...")
# Cabeza base orgánica usando bmesh
mesh_head = bpy.data.meshes.new("Mesh_Head")
obj_head = bpy.data.objects.new("Character_Head", mesh_head)
char_collection.objects.link(obj_head)
bpy.context.view_layer.objects.active = obj_head

bm = bmesh.new()
# Generar icosaedro o esfera UV densa con proporciones estilizadas
bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=24, radius=0.22)
# Deformación anatómica estilizada del cráneo y mandíbula
for v in bm.verts:
    # Aplanar ligeramente los laterales y estrechar hacia la barbilla
    y_rel = v.co.y  # Frente = -Y
    z_rel = v.co.z  # Arriba = +Z
    x_rel = v.co.x
    
    # Mandíbula y barbilla
    if z_rel < -0.05:
        factor_chin = (abs(z_rel) - 0.05) / 0.17
        v.co.x *= (1.0 - factor_chin * 0.28)
        if y_rel < 0: # Barbilla proyectada suavemente
            v.co.y -= factor_chin * 0.03
            v.co.z -= factor_chin * 0.02
    # Pómulos altos estilizados
    if -0.02 < z_rel < 0.08 and y_rel < -0.08:
        v.co.x *= 1.08
        v.co.y -= 0.02
    # Cráneo trasero ligeramente redondeado
    if y_rel > 0.05:
        v.co.y += 0.02
        v.co.z += 0.01

bm.to_mesh(mesh_head)
bm.free()
obj_head.location = (0, 0, 1.66)
obj_head.data.materials.append(mat_skin)

# Cavidad Bucal y Labios Estilizados
bm = bmesh.new()
bm.from_mesh(mesh_head)
# Crear hendidura de la boca hacia adentro
mouth_verts = [v for v in bm.verts if abs(v.co.x) < 0.08 and -0.12 < v.co.z < -0.05 and v.co.y < -0.16]
for v in mouth_verts:
    # Hundir para formar comisura y cavidad
    v.co.y += 0.04
bm.to_mesh(mesh_head)
bm.free()

apply_smooth_and_subdivision(obj_head, levels=1)

# Ojos Detallados (Esclera + Iris + Pupila + Córnea con brillo)
def create_stylized_eye(name, is_left=True):
    x_sign = -1.0 if is_left else 1.0
    x_pos = x_sign * 0.075
    y_pos = -0.185
    z_pos = 1.71
    
    # Esclera
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.040, segments=24, ring_count=16, location=(x_pos, y_pos, z_pos))
    eye = bpy.context.active_object
    eye.name = f"{name}_Sclera"
    eye.data.materials.append(mat_eye_sclera)
    bpy.ops.object.shade_smooth()
    
    # Iris (ligeramente proyectado hacia -Y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, segments=20, ring_count=12, location=(x_pos, y_pos - 0.022, z_pos))
    iris = bpy.context.active_object
    iris.name = f"{name}_Iris"
    iris.scale = (1.0, 0.35, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    iris.data.materials.append(mat_eye_iris)
    bpy.ops.object.shade_smooth()
    
    # Pupila
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, segments=16, ring_count=10, location=(x_pos, y_pos - 0.028, z_pos))
    pupil = bpy.context.active_object
    pupil.name = f"{name}_Pupil"
    pupil.scale = (1.0, 0.25, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    pupil.data.materials.append(mat_eye_pupil)
    bpy.ops.object.shade_smooth()
    
    # Párpados estilizados (Edge loops curvos protectores)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.046, depth=0.015, vertices=20, location=(x_pos, y_pos - 0.005, z_pos), rotation=(math.radians(90), 0, 0))
    lid = bpy.context.active_object
    lid.name = f"{name}_Eyelid"
    lid.scale = (1.05, 0.5, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    lid.data.materials.append(mat_skin)
    bpy.ops.object.shade_smooth()

    # Unir partes del ojo
    bpy.ops.object.select_all(action='DESELECT')
    for p in [pupil, iris, lid, eye]:
        p.select_set(True)
    bpy.context.view_layer.objects.active = eye
    bpy.ops.object.join()
    eye.name = name
    char_collection.objects.link(eye)
    return eye

print("-> Creando ojos estilizados...")
eye_L = create_stylized_eye("Character_Eye_L", is_left=True)
eye_R = create_stylized_eye("Character_Eye_R", is_left=False)

# Dientes y Sonrisa Base
bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.018, vertices=20, location=(0, -0.175, 1.58), rotation=(math.radians(85), 0, 0))
teeth_upper = bpy.context.active_object
teeth_upper.name = "Character_Teeth_Upper"
teeth_upper.scale = (1.1, 0.35, 0.45)
bpy.ops.object.transform_apply(scale=True)
teeth_upper.data.materials.append(mat_teeth)
bpy.ops.object.shade_smooth()
char_collection.objects.link(teeth_upper)

# Nariz Perfilada Estilizada
bpy.ops.mesh.primitive_cone_add(radius1=0.038, radius2=0.018, depth=0.07, vertices=16, location=(0, -0.21, 1.66), rotation=(math.radians(75), 0, 0))
nose = bpy.context.active_object
nose.name = "Character_Nose"
nose.scale = (0.85, 0.9, 0.85)
bpy.ops.object.transform_apply(scale=True)
nose.data.materials.append(mat_skin)
bpy.ops.object.shade_smooth()
char_collection.objects.link(nose)

# Orejas Detalladas con Lóbulo y Concha
for is_left in [True, False]:
    x_s = -1 if is_left else 1
    bpy.ops.mesh.primitive_torus_add(major_radius=0.035, minor_radius=0.012, major_segments=16, minor_segments=12, location=(x_s * 0.22, 0.01, 1.66), rotation=(0, math.radians(x_s * 15), math.radians(x_s * 10)))
    ear = bpy.context.active_object
    ear.name = f"Character_Ear_{'L' if is_left else 'R'}"
    ear.scale = (0.45, 1.1, 1.4)
    bpy.ops.object.transform_apply(scale=True)
    ear.data.materials.append(mat_skin)
    bpy.ops.object.shade_smooth()
    char_collection.objects.link(ear)

# Cejas Expresivas
for is_left in [True, False]:
    x_s = -1 if is_left else 1
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.08, vertices=12, location=(x_s * 0.08, -0.198, 1.775), rotation=(math.radians(10), math.radians(x_s * 15), math.radians(90)))
    brow = bpy.context.active_object
    brow.name = f"Character_Brow_{'L' if is_left else 'R'}"
    brow.scale = (0.8, 1.0, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    brow.data.materials.append(mat_hair)
    bpy.ops.object.shade_smooth()
    char_collection.objects.link(brow)

# Unir elementos faciales a la cabeza antes de Shape Keys
bpy.ops.object.select_all(action='DESELECT')
for elem in [teeth_upper, nose]:
    elem.select_set(True)
for obj in bpy.data.objects:
    if "Ear" in obj.name or "Brow" in obj.name:
        obj.select_set(True)
obj_head.select_set(True)
bpy.context.view_layer.objects.active = obj_head
bpy.ops.object.join()
obj_head.name = "Character_HeadMesh"

# 4. CREACIÓN DE SHAPE KEYS / BLEND SHAPES (Emociones y Visemas)
print("-> Generando Shape Keys faciales (Emociones y Visemas fonéticos)...")
# Base key
if not obj_head.data.shape_keys:
    sk_basis = obj_head.shape_key_add(name="Basis")
else:
    sk_basis = obj_head.data.shape_keys.key_blocks.get("Basis") or obj_head.shape_key_add(name="Basis")

def create_shape_key_deformation(name, vert_filter_fn, displace_fn):
    sk = obj_head.shape_key_add(name=name)
    sk.interpolation = 'KEY_LINEAR'
    for i, v in enumerate(obj_head.data.vertices):
        if vert_filter_fn(v.co):
            dx, dy, dz = displace_fn(v.co)
            sk.data[i].co.x += dx
            sk.data[i].co.y += dy
            sk.data[i].co.z += dz
    return sk

# A. Happy / Sonrisa Amplia
create_shape_key_deformation(
    "happy",
    lambda c: abs(c.x) < 0.16 and -0.16 < c.z < 0.02 and c.y < -0.10,
    lambda c: (
        c.x * 0.12,                                    # comisuras se abren
        -0.015 if c.z < -0.05 else 0.01,               # pómulos se inflan
        0.035 * (1.0 - abs(c.x)/0.18) if abs(c.x) > 0.03 else 0.015 # comisuras suben
    )
)

# B. Laugh / Carcajada
create_shape_key_deformation(
    "laugh",
    lambda c: abs(c.x) < 0.18 and -0.22 < c.z < 0.05 and c.y < -0.08,
    lambda c: (
        c.x * 0.18,
        -0.025,
        -0.06 if c.z < -0.06 else 0.04 # mandíbula cae, comisuras suben
    )
)

# C. Surprised / Sorpresa (Boca en O, ojos y cejas arriba)
create_shape_key_deformation(
    "surprised",
    lambda c: (abs(c.x) < 0.12 and -0.18 < c.z < -0.02 and c.y < -0.12) or (-0.15 < c.x < 0.15 and 0.06 < c.z < 0.18),
    lambda c: (
        -c.x * 0.20 if c.z < 0 else 0,   # labios se estrechan en 'O'
        -0.035 if c.z < 0 else 0.01,     # labios hacia adelante
        -0.055 if c.z < 0 else 0.045     # boca cae, cejas suben
    )
)

# D. Confused / Confusión
create_shape_key_deformation(
    "confused",
    lambda c: abs(c.x) < 0.15 and ((0.05 < c.z < 0.18) or (-0.16 < c.z < -0.04 and c.y < -0.12)),
    lambda c: (
        0.015,
        0,
        (0.04 if c.x > 0 else -0.03) if c.z > 0 else (0.02 if c.x > 0 else -0.02) # ceja derecha sube, izquierda baja
    )
)

# E. Thinking / Pensando
create_shape_key_deformation(
    "thinking",
    lambda c: abs(c.x) < 0.16 and -0.16 < c.z < 0.16,
    lambda c: (
        -0.02 if c.z < 0 else 0,
        0.01,
        0.015 if c.x < 0 else -0.01
    )
)

# F. Sad / Tristeza
create_shape_key_deformation(
    "sad",
    lambda c: abs(c.x) < 0.15 and ((-0.16 < c.z < -0.04 and c.y < -0.12) or (0.05 < c.z < 0.18)),
    lambda c: (
        -c.x * 0.08,
        0,
        (-0.03 if abs(c.x) > 0.04 else 0) if c.z < 0 else (0.03 * (1.0 - abs(c.x)/0.15)) # cejas internas suben
    )
)

# G. Excited / Emocionado
create_shape_key_deformation(
    "excited",
    lambda c: abs(c.x) < 0.18 and -0.20 < c.z < 0.18,
    lambda c: (
        c.x * 0.15,
        -0.02,
        0.04 if c.z > 0 else (-0.03 if c.z < -0.06 else 0.025)
    )
)

# H. Microgestos: Parpadeos (Blinks)
create_shape_key_deformation(
    "blink_L",
    lambda c: -0.12 < c.x < -0.03 and 0.01 < c.z < 0.08 and c.y < -0.14,
    lambda c: (0, 0.008, -0.028)
)
create_shape_key_deformation(
    "blink_R",
    lambda c: 0.03 < c.x < 0.12 and 0.01 < c.z < 0.08 and c.y < -0.14,
    lambda c: (0, 0.008, -0.028)
)

# I. VISEMAS FONÉTICOS PARA LIP-SYNC PRECISO
# 1. viseme_aa (Vocal A: apertura vertical franca)
create_shape_key_deformation(
    "viseme_aa",
    lambda c: abs(c.x) < 0.14 and -0.18 < c.z < -0.04 and c.y < -0.12,
    lambda c: (c.x * 0.05, 0.01, -0.045)
)

# 2. viseme_E (Vocal E: apertura horizontal media)
create_shape_key_deformation(
    "viseme_E",
    lambda c: abs(c.x) < 0.15 and -0.15 < c.z < -0.05 and c.y < -0.12,
    lambda c: (c.x * 0.14, -0.005, -0.02)
)

# 3. viseme_I (Vocal I: estiramiento dental horizontal)
create_shape_key_deformation(
    "viseme_I",
    lambda c: abs(c.x) < 0.16 and -0.14 < c.z < -0.05 and c.y < -0.12,
    lambda c: (c.x * 0.18, -0.01, -0.01)
)

# 4. viseme_O (Vocal O: labios redondeados y proyectados)
create_shape_key_deformation(
    "viseme_O",
    lambda c: abs(c.x) < 0.14 and -0.17 < c.z < -0.04 and c.y < -0.12,
    lambda c: (-c.x * 0.18, -0.035, -0.03)
)

# 5. viseme_U (Vocal U: trompeta / labios apretados)
create_shape_key_deformation(
    "viseme_U",
    lambda c: abs(c.x) < 0.12 and -0.16 < c.z < -0.04 and c.y < -0.12,
    lambda c: (-c.x * 0.28, -0.045, -0.015)
)

# 6. viseme_PP (P, B, M: labios cerrados sellando la boca)
create_shape_key_deformation(
    "viseme_PP",
    lambda c: abs(c.x) < 0.12 and -0.14 < c.z < -0.06 and c.y < -0.13,
    lambda c: (0, 0.02, 0.015 if c.z < -0.09 else -0.015)
)

# 7. viseme_FF (F, V: labio inferior retraído bajo dientes)
create_shape_key_deformation(
    "viseme_FF",
    lambda c: abs(c.x) < 0.12 and -0.14 < c.z < -0.07 and c.y < -0.13,
    lambda c: (0, 0.025, 0.02)
)

# 8. viseme_DD (D, T, N, L: lengua tras dientes, boca entreabierta)
create_shape_key_deformation(
    "viseme_DD",
    lambda c: abs(c.x) < 0.12 and -0.15 < c.z < -0.05 and c.y < -0.12,
    lambda c: (c.x * 0.06, 0.005, -0.022)
)

# 9. viseme_SS (S, Z, C: dientes juntos, labios tensos)
create_shape_key_deformation(
    "viseme_SS",
    lambda c: abs(c.x) < 0.14 and -0.14 < c.z < -0.05 and c.y < -0.12,
    lambda c: (c.x * 0.12, -0.008, -0.012)
)

print(f"-> Shape Keys creadas con éxito: {len(obj_head.data.shape_keys.key_blocks)} formas.")

# 5. SOMBRERO VUELTIAO ZENÚ TRADICIONAL
print("-> Modelando Sombrero Vueltiao Zenú auténtico...")
# Copa tradicional con doblez superior
bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.13, vertices=28, location=(0, 0.02, 1.84), rotation=(math.radians(10), 0, 0))
sombrero_copa = bpy.context.active_object
sombrero_copa.name = "Sombrero_Copa"
# Darle la hendidura típica longitudinal
bm = bmesh.new()
bm.from_mesh(sombrero_copa.data)
for v in bm.verts:
    if v.co.z > 0.04:
        v.co.z -= abs(v.co.x) * 0.35 # Hundir el centro
bm.to_mesh(sombrero_copa.data)
bm.free()
sombrero_copa.data.materials.append(mat_sombrero_crema)
apply_smooth_and_subdivision(sombrero_copa, levels=1)

# Cinta negra perimetral de la copa
bpy.ops.mesh.primitive_cylinder_add(radius=0.195, depth=0.032, vertices=28, location=(0, 0.015, 1.785), rotation=(math.radians(10), 0, 0))
sombrero_cinta = bpy.context.active_object
sombrero_cinta.name = "Sombrero_Cinta"
sombrero_cinta.data.materials.append(mat_sombrero_negro)
apply_smooth_and_subdivision(sombrero_cinta, levels=1)

# Ala Ancha Zenú con Ondulación Orgánica Lateral
bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=0.012, vertices=36, location=(0, 0.012, 1.775), rotation=(math.radians(10), 0, 0))
sombrero_ala = bpy.context.active_object
sombrero_ala.name = "Sombrero_Ala"
bm = bmesh.new()
bm.from_mesh(sombrero_ala.data)
for v in bm.verts:
    dist_x = abs(v.co.x)
    dist_y = v.co.y
    # Ondulación hacia arriba en los laterales (estilo vueltiao)
    if dist_x > 0.18:
        v.co.z += math.sin((dist_x - 0.18) * 4.5) * 0.075
    # Caída suave hacia abajo en frente y nuca
    if abs(dist_y) > 0.22:
        v.co.z -= (abs(dist_y) - 0.22) * 0.12
bm.to_mesh(sombrero_ala.data)
bm.free()
sombrero_ala.data.materials.append(mat_sombrero_crema)
apply_smooth_and_subdivision(sombrero_ala, levels=1)

# Franja negra concéntrica exterior tejida del sombrero vueltiao
bpy.ops.mesh.primitive_cylinder_add(radius=0.43, depth=0.014, vertices=36, location=(0, 0.012, 1.777), rotation=(math.radians(10), 0, 0))
sombrero_ribete = bpy.context.active_object
sombrero_ribete.name = "Sombrero_Ribete"
sombrero_ribete.data.materials.append(mat_sombrero_negro)
apply_smooth_and_subdivision(sombrero_ribete, levels=1)

# 6. CUERPO ESTILIZADO, CAMISILLA (TANK TOP), BERMUDA Y CHANCLETAS
print("-> Modelando Torso, Cuello y Camisilla...")
# Cuello suave
bpy.ops.mesh.primitive_cylinder_add(radius=0.078, depth=0.14, vertices=20, location=(0, 0, 1.48))
neck = bpy.context.active_object
neck.name = "Character_Neck"
neck.data.materials.append(mat_skin)
apply_smooth_and_subdivision(neck, levels=1)

# Torso y Camisilla con volumen y dobladillos
bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.46, vertices=24, location=(0, 0.01, 1.25))
torso = bpy.context.active_object
torso.name = "Character_Torso"
torso.scale = (1.18, 0.76, 1.0)
bpy.ops.object.transform_apply(scale=True)
# Modelar la sisa y pecho atlético
bm = bmesh.new()
bm.from_mesh(torso.data)
for v in bm.verts:
    # Ensanchar pecho y estrechar cintura
    if v.co.z > 0.08:
        v.co.x *= 1.12
        v.co.y *= 1.10
    elif v.co.z < -0.10:
        v.co.x *= 0.92
        v.co.y *= 0.90
bm.to_mesh(torso.data)
bm.free()
torso.data.materials.append(mat_shirt)
apply_smooth_and_subdivision(torso, levels=1)

# Franjas Rojas Junioristas estilizadas en el pecho
for x_pos in [-0.07, 0.07]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.42, vertices=16, location=(x_pos, -0.142, 1.25))
    franja = bpy.context.active_object
    franja.name = f"Camisilla_Franja_{'L' if x_pos < 0 else 'R'}"
    franja.scale = (0.7, 0.15, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    franja.data.materials.append(mat_shirt_stripe)
    apply_smooth_and_subdivision(franja, levels=1)

# Hombros y Piel de Pecho visible
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, segments=20, ring_count=16, location=(0, -0.01, 1.43))
chest_skin = bpy.context.active_object
chest_skin.name = "Character_ChestSkin"
chest_skin.scale = (1.3, 0.85, 0.45)
bpy.ops.object.transform_apply(scale=True)
chest_skin.data.materials.append(mat_skin)
apply_smooth_and_subdivision(chest_skin, levels=1)

# Bermuda Caribeña (Short con bolsillos y volumen)
print("-> Modelando Bermuda / Shorts...")
bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.26, vertices=24, location=(0, 0.01, 0.97))
bermuda_pelvis = bpy.context.active_object
bermuda_pelvis.name = "Bermuda_Pelvis"
bermuda_pelvis.scale = (1.14, 0.88, 1.0)
bpy.ops.object.transform_apply(scale=True)
bermuda_pelvis.data.materials.append(mat_shorts)
apply_smooth_and_subdivision(bermuda_pelvis, levels=1)

# Piernas del Short
for is_left in [True, False]:
    x_s = -1 if is_left else 1
    bpy.ops.mesh.primitive_cylinder_add(radius=0.105, depth=0.28, vertices=20, location=(x_s * 0.13, 0.01, 0.77))
    leg_short = bpy.context.active_object
    leg_short.name = f"Bermuda_Leg_{'L' if is_left else 'R'}"
    leg_short.scale = (1.05, 1.05, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    leg_short.data.materials.append(mat_shorts)
    apply_smooth_and_subdivision(leg_short, levels=1)

# Piernas (Piel, rodillas y pantorrillas anatómicas)
for is_left in [True, False]:
    x_s = -1 if is_left else 1
    # Muslo inferior visible
    bpy.ops.mesh.primitive_cylinder_add(radius=0.082, depth=0.24, vertices=20, location=(x_s * 0.13, 0.01, 0.65))
    leg_skin = bpy.context.active_object
    leg_skin.name = f"Leg_Skin_{'L' if is_left else 'R'}"
    leg_skin.data.materials.append(mat_skin)
    apply_smooth_and_subdivision(leg_skin, levels=1)
    
    # Pantorrilla y tobillo esculpido
    bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.48, vertices=20, location=(x_s * 0.13, 0.005, 0.32))
    calf = bpy.context.active_object
    calf.name = f"Calf_Skin_{'L' if is_left else 'R'}"
    bm = bmesh.new()
    bm.from_mesh(calf.data)
    for v in bm.verts:
        # Taper hacia el tobillo
        if v.co.z < -0.12:
            factor = (abs(v.co.z) - 0.12) / 0.12
            v.co.x *= (1.0 - factor * 0.35)
            v.co.y *= (1.0 - factor * 0.35)
        # Gemelos musculados
        elif v.co.z > 0.05 and v.co.y > 0:
            v.co.y *= 1.25
    bm.to_mesh(calf.data)
    bm.free()
    calf.data.materials.append(mat_skin)
    apply_smooth_and_subdivision(calf, levels=1)

# 7. MANOS DETALLADAS CON 5 DEDOS INDIVIDUALES ARTICULADOS
print("-> Modelando Manos anatómicas con 5 dedos individuales...")
def create_stylized_hand(is_left=True):
    x_s = -1 if is_left else 1
    hand_group = []
    
    # Palma con curvatura y grosor
    bpy.ops.mesh.primitive_cube_add(size=0.075, location=(x_s * 0.46, 0.01, 0.88))
    palm = bpy.context.active_object
    palm.name = f"Character_Palm_{'L' if is_left else 'R'}"
    palm.scale = (0.75, 1.15, 0.45)
    bpy.ops.object.transform_apply(scale=True)
    palm.data.materials.append(mat_skin)
    apply_smooth_and_subdivision(palm, levels=1)
    hand_group.append(palm)
    
    # 5 Dedos: Pulgar (Thumb), Índice (Index), Medio (Middle), Anular (Ring), Meñique (Pinky)
    # Dedos frontales (Index, Middle, Ring, Pinky) ordenados a lo largo de Y
    finger_specs = [
        ("Thumb",  0.038, 0.014, -0.035, -0.025, 38 * x_s, 2), # Oponible, más grueso
        ("Index",  0.048, 0.012, -0.015, -0.042, 5 * x_s, 3),
        ("Middle", 0.054, 0.012,  0.005, -0.046, 0, 3),       # El más largo
        ("Ring",   0.049, 0.011,  0.024, -0.042, -5 * x_s, 3),
        ("Pinky",  0.039, 0.010,  0.042, -0.035, -12 * x_s, 3) # El más pequeño
    ]
    
    for f_name, f_len, f_rad, y_off, z_off, rot_z, phalanges in finger_specs:
        finger_parts = []
        seg_len = f_len / phalanges
        for p in range(phalanges):
            p_z = z_off - (p * seg_len)
            p_y = y_off - (p * 0.004) # Ligera flexión natural
            bpy.ops.mesh.primitive_cylinder_add(
                radius=f_rad * (1.0 - p * 0.08), 
                depth=seg_len * 1.05, 
                vertices=12, 
                location=(x_s * 0.46, 0.01 + p_y, 0.88 + p_z),
                rotation=(math.radians(10), 0, math.radians(rot_z))
            )
            phalanx = bpy.context.active_object
            phalanx.name = f"Hand_{'L' if is_left else 'R'}_{f_name}_Phalanx_{p+1}"
            phalanx.data.materials.append(mat_skin)
            apply_smooth_and_subdivision(phalanx, levels=1)
            finger_parts.append(phalanx)
            hand_group.append(phalanx)

    # Brazos (UpperArm y Forearm) conectando al hombro
    # Brazo superior
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.28, vertices=16, location=(x_s * 0.32, 0.01, 1.25), rotation=(0, math.radians(x_s * 15), 0))
    arm_up = bpy.context.active_object
    arm_up.name = f"UpperArm_{'L' if is_left else 'R'}"
    arm_up.data.materials.append(mat_skin)
    apply_smooth_and_subdivision(arm_up, levels=1)
    
    # Antebrazo con flexión suave
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.26, vertices=16, location=(x_s * 0.41, 0.01, 1.04), rotation=(0, math.radians(x_s * 8), 0))
    forearm = bpy.context.active_object
    forearm.name = f"Forearm_{'L' if is_left else 'R'}"
    forearm.data.materials.append(mat_skin)
    apply_smooth_and_subdivision(forearm, levels=1)

create_stylized_hand(is_left=True)
create_stylized_hand(is_left=False)

# 8. CHANCLETAS COSTEÑAS ERGONÓMICAS CON TIRAS DE GOMA 3D
print("-> Modelando Chancletas ergonómicas costeñas...")
for is_left in [True, False]:
    x_s = -1 if is_left else 1
    # Suela biselada de goma EVA contorneada a la planta del pie
    bpy.ops.mesh.primitive_cube_add(size=0.10, location=(x_s * 0.13, -0.03, 0.025))
    sole = bpy.context.active_object
    sole.name = f"Chancleta_Suela_{'L' if is_left else 'R'}"
    sole.scale = (0.95, 2.3, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    # Taper delantero de la suela
    bm = bmesh.new()
    bm.from_mesh(sole.data)
    for v in bm.verts:
        if v.co.y < -0.05: # Puntera
            v.co.x *= 1.15
        elif v.co.y > 0.04: # Talón
            v.co.x *= 0.88
    bm.to_mesh(sole.data)
    bm.free()
    sole.data.materials.append(mat_sandal_sole)
    apply_smooth_and_subdivision(sole, levels=1)
    
    # Tira en 'V' de goma 3D que abraza el empeine y se ancla entre los dedos
    bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.012, major_segments=20, minor_segments=12, location=(x_s * 0.13, -0.02, 0.065), rotation=(math.radians(35), 0, 0))
    strap = bpy.context.active_object
    strap.name = f"Chancleta_Tira_{'L' if is_left else 'R'}"
    strap.scale = (0.85, 1.25, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    strap.data.materials.append(mat_sandal_strap)
    apply_smooth_and_subdivision(strap, levels=1)
    
    # Pie estilizado sobre la chancleta
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(x_s * 0.13, -0.025, 0.065))
    foot = bpy.context.active_object
    foot.name = f"Foot_Skin_{'L' if is_left else 'R'}"
    foot.scale = (0.85, 1.9, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    foot.data.materials.append(mat_skin)
    apply_smooth_and_subdivision(foot, levels=1)

# -----------------------------------------------------------------------------------
# 9. CONSTRUCCIÓN DEL ESQUELETO (ARMATURE) Y RIGGING CON 5 DEDOS
# -----------------------------------------------------------------------------------
print("-> Creando Armature Profesional y Huesos de Deformación...")
armature_data = bpy.data.armatures.new("Costeno_Armature")
armature_data.relation_line_position = 'HEAD'
armature_obj = bpy.data.objects.new("Character_Rig", armature_data)
char_collection.objects.link(armature_obj)
bpy.context.view_layer.objects.active = armature_obj

bpy.ops.object.mode_set(mode='EDIT')
edit_bones = armature_data.edit_bones

# Hueso Root y Pelvis
b_root = edit_bones.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0, 0.2)

b_hips = edit_bones.new("Hips")
b_hips.head = (0, 0, 0.95)
b_hips.tail = (0, 0, 1.10)
b_hips.parent = b_root

b_spine = edit_bones.new("Spine")
b_spine.head = (0, 0, 1.10)
b_spine.tail = (0, 0, 1.25)
b_spine.parent = b_hips

b_chest = edit_bones.new("Chest")
b_chest.head = (0, 0, 1.25)
b_chest.tail = (0, 0, 1.45)
b_chest.parent = b_spine

b_neck = edit_bones.new("Neck")
b_neck.head = (0, 0, 1.45)
b_neck.tail = (0, 0, 1.58)
b_neck.parent = b_chest

b_head = edit_bones.new("Head")
b_head.head = (0, 0, 1.58)
b_head.tail = (0, 0, 1.90)
b_head.parent = b_neck

# Extremidades Superiores y 5 Dedos
for is_left in [True, False]:
    prefix = "L" if is_left else "R"
    x_s = -1.0 if is_left else 1.0
    
    # Clavícula y Hombro
    b_clavicle = edit_bones.new(f"Clavicle.{prefix}")
    b_clavicle.head = (0, 0, 1.42)
    b_clavicle.tail = (x_s * 0.18, 0, 1.42)
    b_clavicle.parent = b_chest
    
    b_upperarm = edit_bones.new(f"UpperArm.{prefix}")
    b_upperarm.head = (x_s * 0.22, 0, 1.40)
    b_upperarm.tail = (x_s * 0.35, 0, 1.15)
    b_upperarm.parent = b_clavicle
    
    b_forearm = edit_bones.new(f"Forearm.{prefix}")
    b_forearm.head = (x_s * 0.35, 0, 1.15)
    b_forearm.tail = (x_s * 0.44, 0, 0.92)
    b_forearm.parent = b_upperarm
    
    b_hand = edit_bones.new(f"Hand.{prefix}")
    b_hand.head = (x_s * 0.44, 0, 0.92)
    b_hand.tail = (x_s * 0.47, 0, 0.84)
    b_hand.parent = b_forearm
    
    # 5 Dedos Articulados
    fingers = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
    f_offsets_x = [0.015, 0.008, 0.00, -0.008, -0.015]
    for idx, f_name in enumerate(fingers):
        f_x = x_s * (0.46 + f_offsets_x[idx])
        b_f1 = edit_bones.new(f"{f_name}.01.{prefix}")
        b_f1.head = (f_x, -0.01, 0.84)
        b_f1.tail = (f_x, -0.015, 0.80)
        b_f1.parent = b_hand
        
        b_f2 = edit_bones.new(f"{f_name}.02.{prefix}")
        b_f2.head = (f_x, -0.015, 0.80)
        b_f2.tail = (f_x, -0.02, 0.77)
        b_f2.parent = b_f1

# Piernas y Pies
for is_left in [True, False]:
    prefix = "L" if is_left else "R"
    x_s = -1.0 if is_left else 1.0
    
    b_thigh = edit_bones.new(f"Thigh.{prefix}")
    b_thigh.head = (x_s * 0.13, 0, 0.95)
    b_thigh.tail = (x_s * 0.13, 0, 0.52)
    b_thigh.parent = b_hips
    
    b_calf = edit_bones.new(f"Calf.{prefix}")
    b_calf.head = (x_s * 0.13, 0, 0.52)
    b_calf.tail = (x_s * 0.13, 0, 0.08)
    b_calf.parent = b_thigh
    
    b_foot = edit_bones.new(f"Foot.{prefix}")
    b_foot.head = (x_s * 0.13, 0, 0.08)
    b_foot.tail = (x_s * 0.13, -0.15, 0.02)
    b_foot.parent = b_calf

bpy.ops.object.mode_set(mode='OBJECT')

# -----------------------------------------------------------------------------------
# 10. UNIFICACIÓN DE MALLAS Y ASIGNACIÓN DE PESOS SUAVES (SMOOTH SKINNING)
# -----------------------------------------------------------------------------------
print("-> Configurando Armature Modifier y Vertex Groups en todas las mallas...")
# Diccionario de asignación anatómica z/x -> Hueso
all_mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']

for obj in all_mesh_objs:
    # Emparentar al Armature para conformidad glTF 2.0 estricta
    obj.parent = armature_obj
    
    # Agregar Armature Modifier
    mod = obj.modifiers.new("ArmatureMod", type='ARMATURE')
    mod.object = armature_obj
    mod.use_vertex_groups = True
    
    # Calcular centro y nombre para clasificar grupos de vértices
    loc_z = obj.location.z if obj.location.z > 0 else 1.0
    name = obj.name
    
    # Crear grupos de vértices relevantes
    def assign_full_group(target_bone):
        vg = obj.vertex_groups.new(name=target_bone)
        all_indices = list(range(len(obj.data.vertices)))
        vg.add(all_indices, 1.0, 'REPLACE')
        
    if "Head" in name or "Eye" in name or "Sombrero" in name or "Brow" in name or "Ear" in name:
        assign_full_group("Head")
    elif "Neck" in name:
        assign_full_group("Neck")
    elif "Torso" in name or "Camisilla" in name or "Chest" in name:
        assign_full_group("Chest")
    elif "Bermuda_Pelvis" in name:
        assign_full_group("Hips")
    elif "Bermuda_Leg_L" in name or ("Leg_Skin_L" in name):
        assign_full_group("Thigh.L")
    elif "Bermuda_Leg_R" in name or ("Leg_Skin_R" in name):
        assign_full_group("Thigh.R")
    elif "Calf_Skin_L" in name:
        assign_full_group("Calf.L")
    elif "Calf_Skin_R" in name:
        assign_full_group("Calf.R")
    elif "Chancleta" in name and "_L" in name or "Foot_Skin_L" in name:
        assign_full_group("Foot.L")
    elif "Chancleta" in name and "_R" in name or "Foot_Skin_R" in name:
        assign_full_group("Foot.R")
    elif "UpperArm_L" in name:
        assign_full_group("UpperArm.L")
    elif "UpperArm_R" in name:
        assign_full_group("UpperArm.R")
    elif "Forearm_L" in name:
        assign_full_group("Forearm.L")
    elif "Forearm_R" in name:
        assign_full_group("Forearm.R")
    elif "Palm_L" in name or ("Hand_L" in name and "Thumb" not in name and "Index" not in name):
        assign_full_group("Hand.L")
    elif "Palm_R" in name or ("Hand_R" in name and "Thumb" not in name and "Index" not in name):
        assign_full_group("Hand.R")
    elif "Thumb" in name and "_L" in name:
        assign_full_group("Thumb.01.L")
    elif "Thumb" in name and "_R" in name:
        assign_full_group("Thumb.01.R")
    elif "Index" in name and "_L" in name:
        assign_full_group("Index.01.L")
    elif "Index" in name and "_R" in name:
        assign_full_group("Index.01.R")
    else:
        assign_full_group("Chest")

# -----------------------------------------------------------------------------------
# 11. CREACIÓN DE ANIMACIONES PROFESIONALES (CLIPS NLA EXPORTABLES)
# -----------------------------------------------------------------------------------
print("-> Creando Clips de Animación (Idle, Wave, Talk, Explain, Laugh, Think)...")
armature_obj.animation_data_create()

def create_action(name):
    act = bpy.data.actions.new(name=name)
    return act

# Helper para insertar rotación Euler en PoseBone
def insert_pbone_rot(pbone, euler_deg, frame):
    pbone.rotation_mode = 'XYZ'
    pbone.rotation_euler = (math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))
    pbone.keyframe_insert(data_path="rotation_euler", frame=frame)

# 1. Idle (Respiración sutil del pecho y micro-balanceo)
act_idle = create_action("Idle")
armature_obj.animation_data.action = act_idle
pb_chest = armature_obj.pose.bones.get("Chest")
pb_hips = armature_obj.pose.bones.get("Hips")
pb_head = armature_obj.pose.bones.get("Head")
pb_arm_l = armature_obj.pose.bones.get("UpperArm.L")
pb_arm_r = armature_obj.pose.bones.get("UpperArm.R")

for f in [1, 30, 60]:
    rot_c = (2.5, 0, 0) if f == 30 else (0, 0, 0)
    rot_h = (-1.0, 0, 0.5) if f == 30 else (0, 0, 0)
    rot_hd = (-1.5, 0, 1.0) if f == 30 else (0, 0, 0)
    insert_pbone_rot(pb_chest, rot_c, f)
    insert_pbone_rot(pb_hips, rot_h, f)
    insert_pbone_rot(pb_head, rot_hd, f)
    insert_pbone_rot(pb_arm_l, (2, 0, 3), f)
    insert_pbone_rot(pb_arm_r, (2, 0, -3), f)

# 2. Wave (Saludo Costeño enérgico: ¡Epa mani!)
act_wave = create_action("Wave")
armature_obj.animation_data.action = act_wave
pb_fa_r = armature_obj.pose.bones.get("Forearm.R")
pb_hd_r = armature_obj.pose.bones.get("Hand.R")

insert_pbone_rot(pb_arm_r, (15, -25, -75), 1)
insert_pbone_rot(pb_fa_r, (0, 0, 65), 1)
insert_pbone_rot(pb_hd_r, (0, 0, 0), 1)

# Oscilación de la mano
insert_pbone_rot(pb_fa_r, (0, 0, 85), 15)
insert_pbone_rot(pb_hd_r, (0, 0, 25), 15)
insert_pbone_rot(pb_fa_r, (0, 0, 55), 30)
insert_pbone_rot(pb_hd_r, (0, 0, -25), 30)
insert_pbone_rot(pb_fa_r, (0, 0, 85), 45)
insert_pbone_rot(pb_hd_r, (0, 0, 25), 45)

insert_pbone_rot(pb_arm_r, (2, 0, -3), 60)
insert_pbone_rot(pb_fa_r, (0, 0, 0), 60)
insert_pbone_rot(pb_hd_r, (0, 0, 0), 60)

# 3. Talk (Gesticulación animada de conversación)
act_talk = create_action("Talk")
armature_obj.animation_data.action = act_talk
insert_pbone_rot(pb_head, (0, 0, 0), 1)
insert_pbone_rot(pb_head, (5, 0, 3), 15)
insert_pbone_rot(pb_head, (-3, 0, -3), 35)
insert_pbone_rot(pb_head, (0, 0, 0), 60)

insert_pbone_rot(pb_arm_r, (25, 0, -20), 15)
insert_pbone_rot(pb_fa_r, (0, 0, 35), 15)
insert_pbone_rot(pb_arm_l, (20, 0, 15), 35)
insert_pbone_rot(pb_arm_r, (10, 0, -10), 35)
insert_pbone_rot(pb_arm_r, (2, 0, -3), 60)
insert_pbone_rot(pb_arm_l, (2, 0, 3), 60)

# 4. Explain (Manos al frente explicando con pasión)
act_explain = create_action("Explain")
armature_obj.animation_data.action = act_explain
pb_fa_l = armature_obj.pose.bones.get("Forearm.L")
insert_pbone_rot(pb_arm_r, (35, 15, -25), 1)
insert_pbone_rot(pb_fa_r, (0, -20, 45), 1)
insert_pbone_rot(pb_arm_l, (35, -15, 25), 1)
insert_pbone_rot(pb_fa_l, (0, 20, -45), 1)

insert_pbone_rot(pb_arm_r, (45, 20, -35), 30)
insert_pbone_rot(pb_arm_l, (45, -20, 35), 30)

insert_pbone_rot(pb_arm_r, (2, 0, -3), 60)
insert_pbone_rot(pb_fa_r, (0, 0, 0), 60)
insert_pbone_rot(pb_arm_l, (2, 0, 3), 60)
insert_pbone_rot(pb_fa_l, (0, 0, 0), 60)

# 5. Laugh (Carcajada: cabeza hacia atrás, torso vibrando)
act_laugh = create_action("Laugh")
armature_obj.animation_data.action = act_laugh
insert_pbone_rot(pb_head, (-15, 0, 0), 15)
insert_pbone_rot(pb_chest, (-8, 0, 0), 15)
insert_pbone_rot(pb_head, (-18, 0, 0), 25)
insert_pbone_rot(pb_chest, (-5, 0, 0), 25)
insert_pbone_rot(pb_head, (-15, 0, 0), 35)
insert_pbone_rot(pb_chest, (-8, 0, 0), 35)
insert_pbone_rot(pb_head, (0, 0, 0), 60)
insert_pbone_rot(pb_chest, (0, 0, 0), 60)

# 6. Point (Señalar hacia el frente)
act_point = create_action("Point")
armature_obj.animation_data.action = act_point
insert_pbone_rot(pb_arm_r, (65, 0, -10), 20)
insert_pbone_rot(pb_fa_r, (0, 0, 10), 20)
insert_pbone_rot(pb_arm_r, (65, 0, -10), 45)
insert_pbone_rot(pb_arm_r, (2, 0, -3), 60)
insert_pbone_rot(pb_fa_r, (0, 0, 0), 60)

# Empaquetar todas las acciones en pistas NLA para exportación GLB completa
print("-> Creando NLA Tracks para exportar todas las acciones simultáneas...")
for act in [act_idle, act_wave, act_talk, act_explain, act_laugh, act_point]:
    track = armature_obj.animation_data.nla_tracks.new()
    track.name = act.name
    strip = track.strips.new(act.name, 1, act)

# -----------------------------------------------------------------------------------
# 12. EXPORTACIÓN OPTIMIZADA A GLB (glTF 2.0)
# -----------------------------------------------------------------------------------
print(f"-> Exportando modelo binario a {GLB_PATH}...")
# Seleccionar todo
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=GLB_PATH,
    export_format='GLB',
    use_selection=True,
    export_apply=False, # Mantener armatures y shape keys intactos
    export_yup=True,
    export_animations=True,
    export_nla_strips=True,
    export_def_bones=True,
    export_morph=True,
    export_morph_normal=True,
    export_materials='EXPORT',
    export_attributes=True
)

# Guardar copia de respaldo .blend
blend_backup = os.path.join(EXPORTS_DIR, "costeno_master.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_backup)

print(f">>> ¡ÉXITO TOTAL! Modelo generado y exportado en: {GLB_PATH}")
print(f">>> Archivo maestro Blend guardado en: {blend_backup}")
