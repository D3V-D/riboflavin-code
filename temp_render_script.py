
import bpy
import os

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU' 
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.cycles.samples = 16 
scene.render.filepath = "/workspace/rendered_frames/frame_0044.png"

# Clear default layout objects completely
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- 1. Microscope Background Slide (The Glass Substrate) ---
# This adds a white/light-grey backdrop plane underneath the domain so shadows cast correctly
bpy.ops.mesh.primitive_plane_add(size=500, location=(64, 64, 20))
slide_plane = bpy.context.object
slide_plane.name = "Microscope_Slide"

slide_mat = bpy.data.materials.new(name="SlideMaterial")
slide_mat.use_nodes = True
# Set a bright backlit microscope field appearance (matching the light blue/white bg)
slide_mat.node_tree.nodes.get("Principled BSDF").inputs['Base Color'].default_value = (0.88, 0.92, 0.95, 1.0)
slide_mat.node_tree.nodes.get("Principled BSDF").inputs['Roughness'].default_value = 0.9
slide_plane.data.materials.append(slide_mat)

# --- 2. Camera Setup ---
camera = bpy.data.cameras.new("MicroscopeCamera")
camera_obj = bpy.data.objects.new("MicroscopeCamera", camera)
scene.collection.objects.link(camera_obj)
scene.camera = camera_obj
camera_obj.location = (64, 64, 200)  
camera_obj.rotation_euler = (0, 0, 0)

# --- 3. Bright Translucent Lighting Environment ---
# Strong overhead lighting to illuminate the background plate
light_data = bpy.data.lights.new("MainBright", 'AREA')
light_obj = bpy.data.objects.new("MainBright", light_data)
scene.collection.objects.link(light_obj)
light_obj.location = (64, 64, 180)
light_obj.data.energy = 50000  
light_obj.data.size = 150

# Ambient world light to guarantee zero flat clay-grey zones
scene.world.use_nodes = True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.9, 0.93, 0.96, 1.0)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value = 1.5

# --- 4. Import Crystal Mesh & Apply Transmission Shader ---
bpy.ops.wm.obj_import(filepath="/workspace/riboflavin_meshes/frame_0044.obj")
mesh_objects = [obj for obj in scene.objects if obj.type == 'MESH' and obj != slide_plane]

if mesh_objects:
    crystal_obj = mesh_objects[0]
    bpy.context.view_layer.objects.active = crystal_obj
    crystal_obj.select_set(True)

    # Create the high-absorption material network manually
    mat = bpy.data.materials.new(name="RiboflavinMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nodes used to emulate the microscope slides
    node_glass = nodes.new('ShaderNodeBsdfGlass')
    # Saturated yellow-brown tincture typical of dense riboflavin crystals
    node_glass.inputs['Color'].default_value = (0.15, 0.08, 0.01, 1.0) 
    node_glass.inputs['Roughness'].default_value = 0.4
    node_glass.inputs['IOR'].default_value = 1.6

    node_absorb = nodes.new('ShaderNodeVolumeAbsorption')
    # Strong dark-amber volume choke for dense overlapping regions
    node_absorb.inputs['Color'].default_value = (0.1, 0.4, 0.9, 1.0) 
    node_absorb.inputs['Density'].default_value = 12.0

    node_output = nodes.new('ShaderNodeOutputMaterial')

    # Hook up surfaces
    links.new(node_glass.outputs['BSDF'], node_output.inputs['Surface'])
    links.new(node_absorb.outputs['Volume'], node_output.inputs['Volume'])

    crystal_obj.data.materials.append(mat)

# Execute background render to file destination
bpy.ops.render.render(write_still=True)
