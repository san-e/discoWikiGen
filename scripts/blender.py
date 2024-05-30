import bpy
import math
from mathutils import Vector
from PIL import Image

context = bpy.context
scene = context.scene

# Function to import a GLTF file
def import_gltf(filepath):
    bpy.ops.import_scene.gltf(filepath=filepath)

# Function to add a camera
def add_camera():
    bpy.ops.object.camera_add(location=(0, 0, 0))
    scene.camera = context.object
    context.object.data.clip_end = 100000
    return context.object

# Function to add "Track To" constraint to the camera
def add_track_to_constraint(camera, target):
    context.view_layer.objects.active = camera
    bpy.ops.object.constraint_add(type='TRACK_TO')
    constraint = camera.constraints[-1]
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    return constraint

# Function to place the camera at a 45° angle and adjust its distance
def position_camera(camera, target):
    # Calculate the bounding box of the target
    bbox_corners = [target.matrix_world @ Vector(corner) for corner in target.bound_box]
    bbox_center = sum(bbox_corners, Vector()) / 8
    bbox_size = max((bbox_corners[i] - bbox_corners[j]).length for i in range(8) for j in range(i + 1, 8))
    
    # Position the camera
    angle_45 = math.radians(45)
    distance = bbox_size * 5  # Adjust the distance factor as needed
    camera.location = bbox_center + Vector((distance * math.cos(angle_45), distance * math.sin(angle_45), distance * 0.5))
    camera.data.lens = 35  # Set a default focal length, adjust as needed

# Function to load an HDRI
def load_hdri(filepath):
    # Set the environment node tree
    world = scene.world
    world.use_nodes = True
    env_node_tree = world.node_tree
    nodes = env_node_tree.nodes
    
    # Clear existing nodes
    for node in nodes:
        nodes.remove(node)
    
    # Add Background node
    background_node = nodes.new(type='ShaderNodeBackground')
    
    # Add Environment Texture node
    env_texture_node = nodes.new(type='ShaderNodeTexEnvironment')
    env_texture_node.image = bpy.data.images.load(filepath)
    env_texture_node.location = -300, 0
    
    # Add Output node
    output_node = nodes.new(type='ShaderNodeOutputWorld')
    output_node.location = 200, 0
    
    # Link nodes
    env_node_tree.links.new(env_texture_node.outputs['Color'], background_node.inputs['Color'])
    env_node_tree.links.new(background_node.outputs['Background'], output_node.inputs['Surface'])

# Main function
def main(gltf_filepath, hdri_filepath):
    # Step 1: Import GLTF file
    import_gltf(gltf_filepath)
    
    # Step 2: Get the imported object (assuming it's the only object in the scene after import)
    imported_objects = [obj for obj in context.selected_objects]
    if not imported_objects:
        print("No objects imported")
        return
    imported_object = imported_objects[0]
    
    # Step 3: Create a camera
    camera = add_camera()
    
    # Step 4: Add "Track To" constraint
    add_track_to_constraint(camera, imported_object)
    
    # Step 5: Place the camera at a 45° angle and adjust its distance
    position_camera(camera, imported_object)
    
    # Step 6: Load HDRI
    load_hdri(hdri_filepath)

ships = {"xd"}
for ship_name in ships:
    # Replace 'path_to_your_file.gltf' and 'path_to_your_hdri.hdr' with the actual paths to your GLTF and HDRI files
    main(r"A:\Programme\Librelancer\out.glb", r"A:\Benutzer\Tim\Downloads\golden_bay_4k.hdr")

    image_folder = scene.render.filepath
    scene.render.filepath = scene.render.filepath + f"{ship_name}.png"
    bpy.ops.render.render(write_still = True)

    max_size = (scene.render.resolution_x, 300)

    im = Image.open(scene.render.filepath)    
    im = im.crop(im.getbbox())
    im.thumbnail(max_size)
    im.save(scene.render.filepath)

    scene.render.filepath = image_folder

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for material in bpy.data.materials:
            bpy.data.materials.remove(material)
            
    for texture in bpy.data.textures:
            bpy.data.textures.remove(texture)
    
    for image in bpy.data.images:
            bpy.data.images.remove(image)    