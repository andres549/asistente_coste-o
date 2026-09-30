"""
Costeño AI - Generador de Escenario 3D Caribeño de Barranquilla de Alta Calidad
Construye una ciudad caribeña estilizada, colorida y detallada calibrada para el campo de visión de la cámara:
- Fachadas coloniales completas a profundidad óptima (Z = -6.2) para que se aprecie la arquitectura entera
- Primer piso con portones y ventanas con rejas de hierro
- Segundo piso con gran balcón colonial de madera, ventanas de arco y buganvilias fucsias en flor
- Tejas de barro cocido / terracota en los aleros
- Guirnaldas festivas con banderines del Carnaval de Barranquilla (rojo, amarillo, verde, azul)
- Silueta de iglesia colonial de fondo con campanario y cruz
- Palmeras tropicales caribeñas enmarcando la plaza
- Farol colonial y banco de parque sobre adoquines
- Exportación a assets/environment.glb
"""

import bpy
import bmesh
import math
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
GLB_PATH = os.path.join(ASSETS_DIR, "environment.glb")

print(">>> Construyendo Ciudad Caribeña Panorámica de Barranquilla...")

bpy.ops.wm.read_factory_settings(use_empty=True)
for col in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions, bpy.data.images):
    for item in list(col):
        col.remove(item, do_unlink=True)

def create_mat(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat

# Paleta Caribeña Vibrante y Tradicional
mat_yellow     = create_mat("M_Amarillo_Mango",    (0.96, 0.74, 0.18, 1.0), roughness=0.7)
mat_turquoise  = create_mat("M_Azul_Turquesa",     (0.16, 0.68, 0.80, 1.0), roughness=0.7)
mat_coral      = create_mat("M_Rosa_Coral",        (0.95, 0.46, 0.38, 1.0), roughness=0.7)
mat_mint       = create_mat("M_Verde_Menta",       (0.32, 0.76, 0.58, 1.0), roughness=0.7)
mat_peach      = create_mat("M_Melocoton",         (0.96, 0.60, 0.34, 1.0), roughness=0.7)
mat_bg_church  = create_mat("M_Iglesia_Fondo",     (0.88, 0.84, 0.74, 1.0), roughness=0.85)

mat_trim       = create_mat("M_Moldura_Blanca",    (0.98, 0.98, 0.96, 1.0), roughness=0.4)
mat_roof_tile  = create_mat("M_Teja_Terracota",    (0.80, 0.30, 0.14, 1.0), roughness=0.65)
mat_wood       = create_mat("M_Madera_Colonial",   (0.36, 0.20, 0.12, 1.0), roughness=0.6)
mat_iron       = create_mat("M_Hierro_Forjado",    (0.12, 0.12, 0.14, 1.0), roughness=0.35, metallic=0.85)

mat_flowers_bg = create_mat("M_Buganvilia_Rosa",   (0.95, 0.10, 0.55, 1.0), roughness=0.45)
mat_flowers_cy = create_mat("M_Flor_Cayena",       (0.98, 0.15, 0.12, 1.0), roughness=0.4)
mat_grass      = create_mat("M_Cesped_Tropical",   (0.22, 0.66, 0.22, 1.0), roughness=0.75)
mat_leaves     = create_mat("M_Hojas_Palma",       (0.15, 0.60, 0.18, 1.0), roughness=0.45)
mat_trunk      = create_mat("M_Tronco_Palma",      (0.44, 0.32, 0.22, 1.0), roughness=0.85)

mat_flag_y     = create_mat("M_Banderin_Amarillo", (1.00, 0.86, 0.05, 1.0), roughness=0.45)
mat_flag_r     = create_mat("M_Banderin_Rojo",     (0.94, 0.15, 0.18, 1.0), roughness=0.45)
mat_flag_g     = create_mat("M_Banderin_Verde",    (0.12, 0.74, 0.24, 1.0), roughness=0.45)
mat_flag_b     = create_mat("M_Banderin_Azul",     (0.15, 0.58, 0.96, 1.0), roughness=0.45)

mat_pavement   = create_mat("M_Adoquines_Plaza",   (0.74, 0.70, 0.62, 1.0), roughness=0.8)
mat_curb       = create_mat("M_Bordillo_Piedra",   (0.85, 0.80, 0.74, 1.0), roughness=0.65)
mat_lamp_glass = create_mat("M_Cristal_Farol",     (0.98, 0.92, 0.68, 1.0), roughness=0.1)

env_col = bpy.data.collections.new("Costeno_Environment")
bpy.context.scene.collection.children.link(env_col)

def smooth(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

def add_box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    smooth(o)
    env_col.objects.link(o)
    return o

# PROFUNDIDAD DE LAS FACHADAS (Blender Y = 6.2 -> glTF Z = -6.2)
# A esta distancia, con la cámara a Z=+3.8, la separación es 10 metros,
# permitiendo que el encuadre vertical (7.8m de alto) abarque la plaza, ambas plantas,
# el balcón con flores, las tejas y los banderines del carnaval.
WALL_Y = 6.2

# -----------------------------------------------------------------------------------
# A. SUELO DE LA PLAZA Y ACERA COLONIAL
# -----------------------------------------------------------------------------------
print("-> Creando Plaza y Adoquines...")
bpy.ops.mesh.primitive_plane_add(size=36.0, location=(0, 2.0, 0))
ground = bpy.context.active_object
ground.name = "Plaza_Ground"
ground.data.materials.append(mat_pavement)
smooth(ground)
env_col.objects.link(ground)

# Acera elevada y bordillo
add_box("Plaza_Curb", (0, -1.8, 0.08), (32.0, 0.35, 0.16), mat_curb)
add_box("Plaza_Sidewalk", (0, 2.2, 0.05), (32.0, 7.8, 0.10), mat_pavement)

# -----------------------------------------------------------------------------------
# B. FACHADAS COLONIALES EN PERSPECTIVA PERFECTA
# -----------------------------------------------------------------------------------
print("-> Creando Fachadas Coloniales Caribeñas...")

# 1. Edificio Central (Amarillo Mango Colonial, Gran Balcón y Molduras)
# X: -2.2 a +2.6 (Ancho 4.8m, Alto 7.6m)
add_box("Facade_Center_Wall", (0.2, WALL_Y, 3.8), (4.8, 0.6, 7.6), mat_yellow)
add_box("Facade_Center_Cornice", (0.2, WALL_Y - 0.32, 7.65), (5.1, 0.8, 0.4), mat_trim)
add_box("Facade_Center_Pediment", (0.2, WALL_Y - 0.28, 8.15), (2.6, 0.7, 0.6), mat_trim)
add_box("Facade_Center_Roof", (0.2, WALL_Y, 7.95), (5.0, 1.1, 0.3), mat_roof_tile)

# Gran Balcón Colonial de Madera Central
BALCONY_Y = WALL_Y - 0.95
add_box("Balcony_Floor", (0.2, BALCONY_Y, 3.8), (3.8, 1.6, 0.2), mat_wood)
add_box("Balcony_Railing_Front", (0.2, BALCONY_Y - 0.75, 4.35), (3.8, 0.08, 0.9), mat_iron)
add_box("Balcony_Railing_Left", (-1.65, BALCONY_Y, 4.35), (0.08, 1.6, 0.9), mat_iron)
add_box("Balcony_Railing_Right", (2.05, BALCONY_Y, 4.35), (0.08, 1.6, 0.9), mat_iron)

# Ménsulas de soporte talladas bajo el balcón
for xm in [-1.2, 0.2, 1.6]:
    add_box(f"Balcony_Corbel_{xm}", (xm, BALCONY_Y + 0.1, 3.35), (0.24, 1.0, 0.7), mat_wood)

# Puerta-Ventana doble de madera del balcón
add_box("Balcony_Door_Frame", (0.2, WALL_Y - 0.32, 4.95), (1.9, 0.15, 2.1), mat_trim)
add_box("Balcony_Door_L", (-0.35, WALL_Y - 0.35, 4.95), (0.75, 0.08, 1.95), mat_wood)
add_box("Balcony_Door_R", (0.75, WALL_Y - 0.35, 4.95), (0.75, 0.08, 1.95), mat_wood)

# Buganvilias fucsias en cascada sobre la barandilla (vibrante sabor caribeño)
for i, xb in enumerate([-1.3, -0.7, -0.1, 0.5, 1.1, 1.7]):
    h = 0.45 + (i % 3) * 0.22
    add_box(f"Bougainvillea_Clump_{i}", (xb, BALCONY_Y - 0.8, 4.0 - h * 0.4), (0.55, 0.4, h), mat_flowers_bg)

# Portón de Entrada en Planta Baja
add_box("Portal_Frame", (0.2, WALL_Y - 0.32, 1.35), (2.1, 0.18, 2.5), mat_trim)
add_box("Portal_Door", (0.2, WALL_Y - 0.35, 1.3), (1.75, 0.1, 2.3), mat_wood)
add_box("Street_Plaque", (2.0, WALL_Y - 0.35, 2.2), (0.6, 0.05, 0.38), mat_trim)

# 2. Edificio Izquierdo (Azul Turquesa Caribeño con Ventanales)
# X: -7.6 a -2.2 (Ancho 5.4m, Alto 7.2m)
add_box("Facade_Left_Wall", (-4.9, WALL_Y + 0.1, 3.6), (5.4, 0.6, 7.2), mat_turquoise)
add_box("Facade_Left_Cornice", (-4.9, WALL_Y - 0.25, 7.25), (5.6, 0.75, 0.35), mat_trim)
add_box("Facade_Left_Roof", (-4.9, WALL_Y + 0.15, 7.5), (5.5, 1.1, 0.3), mat_roof_tile)

for xw in [-6.4, -3.5]:
    add_box(f"L_Win2_Frame_{xw}", (xw, WALL_Y - 0.22, 5.1), (1.5, 0.16, 2.0), mat_trim)
    add_box(f"L_Win2_Shutters_{xw}", (xw, WALL_Y - 0.26, 5.1), (1.2, 0.08, 1.75), mat_wood)
    add_box(f"L_Planter_{xw}", (xw, WALL_Y - 0.35, 4.0), (1.4, 0.32, 0.26), mat_trim)
    add_box(f"L_Flower_{xw}", (xw, WALL_Y - 0.4, 4.2), (1.3, 0.24, 0.22), mat_flowers_cy)

for xw in [-6.4, -3.5]:
    add_box(f"L_Win1_Frame_{xw}", (xw, WALL_Y - 0.22, 1.8), (1.5, 0.16, 2.1), mat_trim)
    add_box(f"L_Win1_Grille_{xw}", (xw, WALL_Y - 0.32, 1.8), (1.3, 0.1, 1.9), mat_iron)

# 3. Edificio Derecho (Rosa Coral Tropical con Balconcillo Francés)
# X: +2.6 a +8.0 (Ancho 5.4m, Alto 7.0m)
add_box("Facade_Right_Wall", (5.3, WALL_Y + 0.1, 3.5), (5.4, 0.6, 7.0), mat_coral)
add_box("Facade_Right_Cornice", (5.3, WALL_Y - 0.25, 7.05), (5.6, 0.75, 0.35), mat_trim)
add_box("Facade_Right_Roof", (5.3, WALL_Y + 0.15, 7.3), (5.5, 1.1, 0.3), mat_roof_tile)

for xw in [4.0, 6.6]:
    add_box(f"R_Win2_Frame_{xw}", (xw, WALL_Y - 0.22, 4.9), (1.5, 0.16, 2.0), mat_trim)
    add_box(f"R_Win2_Door_{xw}", (xw, WALL_Y - 0.26, 4.9), (1.2, 0.08, 1.75), mat_wood)
    add_box(f"R_Balcony_Rail_{xw}", (xw, WALL_Y - 0.38, 4.35), (1.45, 0.16, 0.85), mat_iron)

for xw in [4.0, 6.6]:
    add_box(f"R_Win1_Frame_{xw}", (xw, WALL_Y - 0.22, 1.8), (1.5, 0.16, 2.1), mat_trim)
    add_box(f"R_Win1_Door_{xw}", (xw, WALL_Y - 0.28, 1.8), (1.25, 0.08, 1.9), mat_wood)

# 4. Edificios Extremos Panorámicos para Llenar Todo el Ancho
add_box("Facade_FarLeft", (-12.0, WALL_Y + 0.4, 3.5), (8.0, 0.8, 7.0), mat_mint)
add_box("FarLeft_Roof", (-12.0, WALL_Y + 0.5, 7.15), (8.1, 1.2, 0.35), mat_roof_tile)

add_box("Facade_FarRight", (12.0, WALL_Y + 0.4, 3.5), (8.0, 0.8, 7.0), mat_peach)
add_box("FarRight_Roof", (12.0, WALL_Y + 0.5, 7.15), (8.1, 1.2, 0.35), mat_roof_tile)

# -----------------------------------------------------------------------------------
# C. SILUETA URBANA DE SEGUNDO PLANO (Blender Y = 10.5 -> glTF Z = -10.5)
# Acentúa la profundidad y la escala de la ciudad de Barranquilla
# -----------------------------------------------------------------------------------
print("-> Creando Silueta Urbana de Fondo (Iglesia y Cúpula)...")
BG_Y = 10.5
add_box("Church_Tower_Base", (5.2, BG_Y, 5.5), (3.0, 3.0, 11.0), mat_bg_church)
add_box("Church_Belfry", (5.2, BG_Y, 11.6), (2.5, 2.5, 2.0), mat_bg_church)

bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=1.8, vertices=16, location=(5.2, BG_Y, 13.1))
cupola = bpy.context.active_object
cupola.name = "Church_Cupola"
cupola.data.materials.append(mat_roof_tile)
smooth(cupola)
env_col.objects.link(cupola)

add_box("Church_Cross_V", (5.2, BG_Y, 14.5), (0.12, 0.12, 1.0), mat_iron)
add_box("Church_Cross_H", (5.2, BG_Y, 14.7), (0.65, 0.12, 0.12), mat_iron)

add_box("Skyline_Block_L", (-7.5, BG_Y + 0.5, 6.0), (7.0, 2.2, 9.5), mat_yellow)
add_box("Skyline_Block_R", (10.0, BG_Y + 0.8, 5.6), (6.5, 2.2, 9.0), mat_peach)

# -----------------------------------------------------------------------------------
# D. BANDERINES DEL CARNAVAL DE BARRANQUILLA (Guirnaldas Festivas)
# -----------------------------------------------------------------------------------
print("-> Creando Banderines Festivos del Carnaval...")
flag_mats = [mat_flag_y, mat_flag_r, mat_flag_g, mat_flag_b]

def create_carnival_flags(line_name, start_x, end_x, y_pos, base_z, num_flags=18):
    for i in range(num_flags):
        t = i / (num_flags - 1)
        x = start_x + (end_x - start_x) * t
        sag = math.sin(t * math.pi) * 0.75
        z = base_z - sag
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.42, vertices=3, location=(x, y_pos, z), rotation=(math.radians(180), 0, math.radians(12 * math.sin(i * 1.5))))
        flag = bpy.context.active_object
        flag.name = f"{line_name}_{i}"
        flag.scale = (0.75, 0.04, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        flag.data.materials.append(flag_mats[i % 4])
        smooth(flag)
        env_col.objects.link(flag)

create_carnival_flags("Carnival_Flag_Row1", -7.5, 7.5, WALL_Y - 1.8, 6.2, num_flags=18)
create_carnival_flags("Carnival_Flag_Row2", -6.5, 6.5, WALL_Y - 3.2, 5.4, num_flags=16)

# -----------------------------------------------------------------------------------
# E. PALMERAS REALES CARIBEÑAS (Encuadran la escena)
# -----------------------------------------------------------------------------------
print("-> Modelando Palmeras Tropicales...")
def create_palm(name, x, y, rot_deg=0):
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.24, vertices=20, location=(x, y, 0.12))
    planter = bpy.context.active_object
    planter.name = f"{name}_Planter"
    planter.data.materials.append(mat_curb)
    smooth(planter)
    env_col.objects.link(planter)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.92, depth=0.2, vertices=16, location=(x, y, 0.2))
    grass = bpy.context.active_object
    grass.name = f"{name}_Grass"
    grass.data.materials.append(mat_grass)
    smooth(grass)
    env_col.objects.link(grass)
    
    # Tronco estilizado con curvatura elegante
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=5.2, vertices=16, location=(x, y, 2.7), rotation=(math.radians(6), 0, math.radians(rot_deg)))
    trunk = bpy.context.active_object
    trunk.name = f"{name}_Trunk"
    bm = bmesh.new()
    bm.from_mesh(trunk.data)
    for v in bm.verts:
        if v.co.z > 0:
            f = v.co.z / 2.6
            v.co.x *= (1.0 - f * 0.34)
            v.co.y *= (1.0 - f * 0.34)
    bm.to_mesh(trunk.data)
    bm.free()
    trunk.data.materials.append(mat_trunk)
    smooth(trunk)
    env_col.objects.link(trunk)
    
    top_z = 5.2
    for i in range(9):
        ang = math.radians(i * (360 / 9))
        rx = x + math.cos(ang) * 1.65
        ry = y + math.sin(ang) * 1.65
        rz = top_z - 0.3
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=3.2, vertices=12, location=(rx, ry, rz), rotation=(math.radians(40), math.radians(12), ang))
        frond = bpy.context.active_object
        frond.name = f"{name}_Frond_{i}"
        frond.scale = (0.35, 1.0, 0.04)
        bpy.ops.object.transform_apply(scale=True)
        frond.data.materials.append(mat_leaves)
        smooth(frond)
        env_col.objects.link(frond)

create_palm("Palm_L", -4.8, 0.5, rot_deg=18)
create_palm("Palm_R", 4.8, 0.8, rot_deg=-22)

# -----------------------------------------------------------------------------------
# F. MOBILIARIO URBANO: FAROL DOBLE Y BANCO
# -----------------------------------------------------------------------------------
print("-> Añadiendo Faroles y Banco...")
add_box("Lamp_Post_Base", (-2.8, -0.6, 0.22), (0.44, 0.44, 0.44), mat_iron)
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=3.4, vertices=16, location=(-2.8, -0.6, 1.95))
lpost = bpy.context.active_object
lpost.name = "Lamp_Post_Shaft"
lpost.data.materials.append(mat_iron)
smooth(lpost)
env_col.objects.link(lpost)

for xl in [-3.15, -2.45]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.48, vertices=6, location=(xl, -0.6, 3.6))
    lglass = bpy.context.active_object
    lglass.name = f"Lamp_Glass_{xl}"
    lglass.data.materials.append(mat_lamp_glass)
    smooth(lglass)
    env_col.objects.link(lglass)

add_box("Park_Bench_Seat", (2.6, -0.4, 0.48), (2.2, 0.55, 0.08), mat_wood)
add_box("Park_Bench_Back", (2.6, -0.15, 0.85), (2.2, 0.08, 0.5), mat_wood)
for xb in [1.7, 3.5]:
    add_box(f"Bench_Leg_{xb}", (xb, -0.35, 0.24), (0.08, 0.5, 0.48), mat_iron)

# -----------------------------------------------------------------------------------
# G. EXPORTACIÓN GLB
# -----------------------------------------------------------------------------------
print(f"-> Exportando Escenario Completo a {GLB_PATH}...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=GLB_PATH,
    export_format='GLB',
    use_selection=True,
    export_yup=True,
    export_materials='EXPORT',
    export_attributes=True
)

print(f">>> ¡ÉXITO TOTAL! Escenario Caribeño generado y exportado en: {GLB_PATH}")
