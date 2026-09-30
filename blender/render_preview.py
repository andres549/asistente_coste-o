import bpy
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.film_transparent = False

base_dir = r"C:\Users\User\.gemini\antigravity\scratch\costeno-ai"
char_path = os.path.join(base_dir, "assets", "character.glb")
bg_path = os.path.join(base_dir, "assets", "courtyard_bg.jpg")
out_path = os.path.join(base_dir, "assets", "render_scene_preview.png")

bpy.ops.import_scene.gltf(filepath=char_path)

# Set up World background with courtyard image
world = bpy.data.worlds.new("CourtyardWorld")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

bg_node = nodes.new(type='ShaderNodeBackground')
output_node = nodes.new(type='ShaderNodeOutputWorld')
tex_node = nodes.new(type='ShaderNodeTexEnvironment')

if os.path.exists(bg_path):
    tex_node.image = bpy.data.images.load(bg_path)

links.new(tex_node.outputs['Color'], bg_node.inputs['Color'])
links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])
bg_node.inputs['Strength'].default_value = 1.0

# Add Camera
cam_data = bpy.data.cameras.new("MainCam")
cam_data.lens = 48
cam_obj = bpy.data.objects.new("MainCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_obj.location = (0.18, -3.1, 1.38)
cam_obj.rotation_euler = (1.5708, 0, 0)

# Sunlight
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.5
sun_data.color = (1.0, 0.96, 0.90)
sun_obj = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (0.785, 0.35, -0.6)

# Fill light
fill_data = bpy.data.lights.new("Fill", type='POINT')
fill_data.energy = 80
fill_data.color = (1.0, 0.94, 0.88)
fill_obj = bpy.data.objects.new("Fill", fill_data)
fill_obj.location = (0.1, -1.8, 1.45)
scene.collection.objects.link(fill_obj)

# Ground shadow plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground.is_shadow_catcher = True

scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("Render finished:", out_path)

