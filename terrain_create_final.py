import bpy
import bmesh
import random

def rand(n=1):
    return random.uniform(0,1)*n

def partially_clean():

    bpy.ops.object.select_all(action="SELECT")

    bpy.ops.object.delete()

    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


def create_material(name):
    material = bpy.data.materials.new(name=name)
    
    material.use_nodes = True
    
    principled_bsdf_node = material.node_tree.nodes["Principled BSDF"]
    
    principled_bsdf_node.inputs["Base Color"].default_value = (rand(),rand(),rand(), 1)
    
    principled_bsdf_node.inputs["Metallic"].default_value = rand()
    
    principled_bsdf_node.inputs["Roughness"].default_value = rand()
    
    return material

def create_terrain_material():
    material = bpy.data.materials.new(name="Terrain Material")
    
    material.use_nodes = True
    
    output_node = material.node_tree.nodes["Material Output"]
    
    water_bsdf_node = material.node_tree.nodes["Principled BSDF"]
    
    ##########CUSTOMIZABLE#########
    # this is the water bsdf
    ##########CUSTOMIZABLE#########
    
    water_bsdf_node.inputs["Base Color"].default_value = (0.00587631, 0.140829, 0.373786, 1)
    
    water_land_mix_node = material.node_tree.nodes.new(type="ShaderNodeMixShader")
    
    material.node_tree.links.new(water_bsdf_node.outputs["BSDF"],water_land_mix_node.inputs[1])
    
    material.node_tree.links.new(water_land_mix_node.outputs["Shader"],output_node.inputs["Surface"])
    
    # water land seperator
    
    texture_coordinate_node = material.node_tree.nodes.new(type="ShaderNodeTexCoord")
    
    water_separate_xyz_node = material.node_tree.nodes.new(type="ShaderNodeSeparateXYZ")
    
    ##########CUSTOMIZABLE#########
    # this is the water separate rate
    ##########CUSTOMIZABLE#########
    
    water_separate_color_node = material.node_tree.nodes.new(type="ShaderNodeValToRGB")
    
    water_separate_color_node.color_ramp.elements[1].position=0.01
    
    material.node_tree.links.new(texture_coordinate_node.outputs["Generated"],water_separate_xyz_node.inputs["Vector"])
    
    material.node_tree.links.new(water_separate_xyz_node.outputs["Z"],water_separate_color_node.inputs["Fac"])
    
    material.node_tree.links.new(water_separate_color_node.outputs["Color"],water_land_mix_node.inputs["Fac"])
    
    #grass rock mixer
    grass_rock_mix_node = material.node_tree.nodes.new(type="ShaderNodeMixShader")
    
    #sand rock mixer
    sand_rock_mix_node = material.node_tree.nodes.new(type="ShaderNodeMixShader")
    
    ##########CUSTOMIZABLE#########
    # this is the rock bsdf
    ##########CUSTOMIZABLE#########
    
    rock_bsdf_node = material.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    
    rock_bsdf_node.inputs["Base Color"].default_value = (0.134636, 0.134636, 0.134636, 1)
    
    material.node_tree.links.new(rock_bsdf_node.outputs["BSDF"],sand_rock_mix_node.inputs[2])
    
    material.node_tree.links.new(sand_rock_mix_node.outputs["Shader"],grass_rock_mix_node.inputs[1])
    
    material.node_tree.links.new(grass_rock_mix_node.outputs["Shader"],water_land_mix_node.inputs[2])
    
    #geometry
    geometry_node = material.node_tree.nodes.new(type="ShaderNodeNewGeometry")
    
    grass_separate_xyz_node = material.node_tree.nodes.new(type="ShaderNodeSeparateXYZ")
    
    ##########CUSTOMIZABLE#########
    # this is the grass separate rate
    ##########CUSTOMIZABLE#########
    
    grass_separate_color_node = material.node_tree.nodes.new(type="ShaderNodeValToRGB")
    
    grass_separate_color_node.color_ramp.elements[0].position=0.631
    
    ##########CUSTOMIZABLE#########
    # this is the grass bsdf
    ##########CUSTOMIZABLE#########
    
    grass_bsdf_node = material.node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
    
    grass_bsdf_node.inputs["Color"].default_value = (0.192554, 0.378511, 0.137267, 1)
    
    material.node_tree.links.new(grass_bsdf_node.outputs["BSDF"],grass_rock_mix_node.inputs[2])
    
    material.node_tree.links.new(geometry_node.outputs["Normal"],grass_separate_xyz_node.inputs["Vector"])
    
    material.node_tree.links.new(grass_separate_xyz_node.outputs["Z"],grass_separate_color_node.inputs["Fac"])
    
    material.node_tree.links.new(grass_separate_color_node.outputs["Color"],grass_rock_mix_node.inputs["Fac"])
    
    
    
    sand_separate_xyz_node = material.node_tree.nodes.new(type="ShaderNodeSeparateXYZ")
    
    ##########CUSTOMIZABLE#########
    # this is the sand separate rate
    ##########CUSTOMIZABLE#########
    
    sand_separate_color_node = material.node_tree.nodes.new(type="ShaderNodeValToRGB")
    
    sand_separate_color_node.color_ramp.elements[1].position=0.05
    
    ##########CUSTOMIZABLE#########
    # this is the sand bsdf
    ##########CUSTOMIZABLE#########
    
    sand_bsdf_node = material.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    
    sand_bsdf_node.inputs["Base Color"].default_value = (0.321486, 0.311237, 0.147633, 1)
    
    material.node_tree.links.new(sand_bsdf_node.outputs["BSDF"],sand_rock_mix_node.inputs[1])
    
    material.node_tree.links.new(texture_coordinate_node.outputs["Generated"],sand_separate_xyz_node.inputs["Vector"])
    
    material.node_tree.links.new(sand_separate_xyz_node.outputs["Z"],sand_separate_color_node.inputs["Fac"])
    
    material.node_tree.links.new(sand_separate_color_node.outputs["Color"],sand_rock_mix_node.inputs["Fac"])
    
    return material

def add_object():
    d=0.5
    s=0.5
    iter=10
    min=0
    max=1

    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

    obj = bpy.context.object
    me = obj.data

    # Code taken from https://docs.blender.org/api/current/bmesh.html

    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(me)   # fill it in from a Mesh

    props = bpy.context.active_object

    for i in range(iter):
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
        for v in bm.verts:
            r = random.uniform(-d,d)
            v.co.z += r
            if i == iter-2:
                if v.co.z>max:
                    v.co.z=max
                elif v.co.z<min:
                    v.co.z=min
        d *= (1-s)
    bm.to_mesh(me)
    bm.free()  # free and prevent further access

def main():
    
    partially_clean()
    
#    material = create_material("test")
    material = create_terrain_material()
    
    add_object()
    
    mesh_obj = bpy.context.active_object
    
    mesh_obj.data.materials.append(material)

main()