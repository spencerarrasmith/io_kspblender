# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from struct import unpack
import os.path
import math

import bpy
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Quaternion

from . import properties
from . import part_dir
from . import right_scale
from . import ksparser
from .ksparser import *

def import_craft(self, context, filepath):
    operator = self
    undo = bpy.context.user_preferences.edit.use_global_undo
    bpy.context.user_preferences.edit.use_global_undo = False

    print("\n")
    print("         A          ")
    print("        / \\        ")
    print("       | 0 |        ")
    print("       |___|        ")
    print("       |___|        ")
    print("       |KSP|        ")
    print("      /|   |\\      ")
    print("     /| \\_/ |\\    ")
    print("    /_|  W  |_\\    ")
    print("       @WWW@        ")
    print("     @@WWWWW@@      ")
    print("    @ @@@@ @@@ @    ")
    print("  @   @  @@  @   @  ")
    print("\n")

    partdir = part_dir.make()
    rightscale = right_scale.make()
    craft = import_parts(filepath)
    fairing_fixer(craft.partslist)
    scale_fixer(craft,10)
    stage_grouper()
    #unselectable_fixer()
    print( "All done")
    
    bpy.context.user_preferences.edit.use_global_undo = undo
    return {'FINISHED'}

def import_parts(filepath):

    dir = os.path.dirname(__file__)
    partdir = part_dir.make()
    rightscale = right_scale.make()
    kspdirfile = open(dir+'\\kspdir.txt')
    ksp = kspdirfile.read()
    
    for obj in bpy.context.scene.objects:
        obj.select = False

    craft = kspcraft(filepath)

    print(craft.ship + ' ready for takeoff\n')
    print(str(craft.num_parts()) + ' parts found...')
    
    partslist = craft.partslist
    doneparts = {}                                                                                          # keep track of parts that have already been imported so I can save time
    doneobj = set(bpy.data.objects)                                                                         # know which objects have gone through the cleaning process
    scn = bpy.context.scene                                                                                 # the active scene
    #cursor_loc = get_cursor_location()

    #to_ground = partslist[0].pos[2]
    
    for part in partslist:
        if os.path.isfile(ksp+partdir[part.partName][0]):                                                      # make sure the part file exists so nothing crashes
            print("\n----------------------------------------------------\n")                               # to make console output easier to look at
            if part.partName not in doneparts:                                                              # if part has not been imported...
                print("Importing "+part.partName+" as "+part.part)                                                               # ...say so on the console
                bpy.ops.import_object.ksp_mu(filepath=ksp+partdir[part.partName][0])                               # call the importer
                newpart = bpy.context.active_object                                                             # set the imported part object to active. from here on, part refers to the part data structure and object to the blender object
                newpart.select = True
                newpart.name = part.part                                                                        # rename the object according to the part name (including the number)
                newpart.location = Vector(part.pos)#+cursor_loc                                                          # move the object
                newpart.rotation_quaternion = part.rotQ                                                         # rotate the object
                if part.partName in rightscale:
                    newpart.select = True
                    newpart.scale = rightscale[part.partName]
                    bpy.ops.object.transform_apply(location = False, rotation = False, scale = True)
                    print("Scale corrected")
                
                #setup to make lod parts
                #meme = bpy.data.meshes.new(part.partName+"_low")
                #objobj = bpy.data.objects.new(part.partName+"_low",meme)
                #objobj.location = newpart.location
                #scn.objects.link(objobj)
                
                print("\n")
                
                # Set a bunch of properties
                newpart["partName"] = part.partName
                newpart["partClass"] = partdir[part.partName][1]
                newpart["mir"] = part.mir
                newpart["symMethod"] = part.symMethod
                newpart["istg"] = part.istg
                newpart["dstg"] = part.dstg
                newpart["sidx"] = part.sidx
                newpart["sqor"] = part.sqor
                newpart["attm"] = part.attm
                newpart["modCost"] = part.modCost
                newpart["modMass"] = part.modMass
                newpart["modSize"] = part.modSize
                newpart["ship"] = craft.ship
                #newpart["linklist"] = part.linklist
                #newpart["attNlist"] = part.attNlist
                #newpart["symlist"] = part.symlist
                #newpart["srfNlist"] = part.srfNlist ### FIX THESE
                newpart["tgt"] = part.tgt
                newpart["tgtpos"] = part.tgtpos
                newpart["tgtrot"] = part.tgtrot
                newpart["tgtdir"] = part.tgtdir
                
                
            else:                                                                                           # but if part has been imported...
                hiddenlist = []                                                                                 # clunky workaround
                for obj in bpy.data.objects:                                                                    # hidden objects cannot be modified (duplication is what I want to do)
                    if not obj.is_visible(scn):                                                                     # find all hidden objects
                        hiddenlist.append(obj)                                                                      # create a big stupid list
                        scn.objects.active = obj                                                                    # always need to do this to get things to actually happen to objects
                        obj.hide = False                                                                            # unhide each one
                bpy.ops.object.select_all(action = 'DESELECT')                                                  # deselect everything
                print("Duplicating "+part.partName+" as "+part.part+"\n")                                                        # let me know if the part is just being duplicated
                oldpart = bpy.data.objects[doneparts[part.partName]]                                            # have to select the object (2 step process)
                oldpart.select = True
                bpy.context.scene.objects.active = oldpart
                print(oldpart)
                bpy.ops.object.select_grouped(type = 'CHILDREN_RECURSIVE')                                      # select all children of the parent object (the empty), which deselects the parent
                bpy.data.objects[doneparts[part.partName]].select = True                                        # so reselect the parent
                
                bpy.ops.object.duplicate_move_linked()                                                          # duplicate the whole family
                copiedpart = oldpart.name + ".001"                                                             # the duplicate will be called something.001 always
                bpy.ops.object.select_all(action = 'DESELECT')                                                  # deselect everything
                newpart = bpy.data.objects[copiedpart]                                                          # and select just the parent (again, multi-step process)
                newpart.select = True
                bpy.context.scene.objects.active = newpart
                print(bpy.context.active_object)
                newpart.name = part.part                                                                        # rename it
                newpart.location = Vector(part.pos)#+cursor_loc                                                          # move it
                newpart.rotation_quaternion = part.rotQ                                                         # rotate it
                for obj in hiddenlist:                                                                          # hide all that annoying stuff again
                    obj.hide = True
        
        else:
            print("Failed to load "+part.partName+"... Probably an unsupported mod. Let me know what part it was!\n")                                   # if the part doesn't exist, let me know
        
        if part.partName not in doneparts:                                                                  # if the part hasn't been imported before...
            doneparts[part.partName] = part.part                                                            # ...it has now

        objlist = set([obj for obj in bpy.data.objects if obj not in doneobj])                              # find all the newly added objects
        
        doneobj = set(bpy.data.objects)                                                                     # done dealing with all the objects that are now in the scene (except for the ones I'm about to work with in objlist)
        emptysize = []
                
        if partdir[part.partName][1] == "strut":
            add_strut(part,objlist)
            
        elif partdir[part.partName][1] == "fuelline":
            add_fuelline(part,objlist)
            
        elif partdir[part.partName][1] == "launchclamp":
            add_launchclamp(part,objlist)
                    
        else:    
            for obj in objlist:                                                                                 # for all the unprocesses objects
                print(obj.name)                                                                                     # let me know which one we're on
                obj['ship'] = craft.ship
                if obj.type == 'EMPTY':                                                                             # if it's an Empty object
                    if obj.parent != None:                                                                              # if the Empty is not top-level
                        obj.hide = True                                                                                     # hide that shyet
                        print(obj.name + " Hidden\n")                                                                       # and tell me that they're gone
                    else:                                                                                               # but if it is top level
                        obj.empty_draw_type = 'SPHERE'                                                                      # make that shyet a sphere
                        obj.empty_draw_size = 0                                                                             # a hella tiny sphere
                if obj.type == 'MESH':                                                                              # if it's a Mesh object
                    scn.objects.active = obj                                                                            # make it active
                    if "KSP" not in obj.name:
                        if obj.data.materials:
                            material_fixer(obj,part)
                            #print(1)
                        #while len(obj.data.materials) > 0:
                            #obj.data.materials.pop(0, update_data=True)
                            #bpy.ops.object.material_slot_remove()
                    bpy.ops.object.mode_set(mode='EDIT')                                                                # go into edit mode
                    bpy.ops.mesh.remove_doubles(threshold = 0.0001)                                                     # remove double vertices
                    bpy.ops.mesh.normals_make_consistent(inside = False)                                                # fix normals
                    bpy.ops.object.mode_set(mode='OBJECT')                                                              # leave edit mode
                    
                    obj.select = True
                    bpy.ops.object.shade_smooth()
                    obj.data.use_auto_smooth = True
                    obj.data.auto_smooth_angle = .610865
                    bpy.ops.object.select_all(action = 'DESELECT')
                    
                    if len(obj.data.polygons) == 0:                                                                     # and if it's one of them stupid fake meshes with no faces
                        obj.hide = True                                                                                 # gtfo
                        obj.hide_render = True
                       
                    root = obj
                    meshrad = math.sqrt((obj.dimensions[0]/2)**2 + (obj.dimensions[1]/2)**2 + (obj.dimensions[2]/2)**2)  # find the radius of the parent Empty such that it encloses the object
                    emptysize.append(meshrad)
                    
                if "coll" in obj.name or "COL" in obj.name or "Col" in obj.name or "fair" in obj.name and 'KSP' not in obj.name:         # if it is named anything to do with collider, I'll have none of it
                    obj.hide = True                                                                                     # gtfo
                    obj.hide_render = True                                                                              # really gtfo (don't even render)
                    #object.select = True                                                                               # and if I'm really mad
                    #bpy.ops.object.delete()                                                                            # I could just delete it
                    if obj.type != 'EMPTY':                                                                             # and if it is a mesh (the empties have already been hidden, so this is a double-tap on them)...
                        print(obj.name + " Hidden\n")                                                                       # ...let me know
                
                action_fixer(obj)
                
#        for obj in objlist:
#            if "KSP" not in obj.name and obj.type == 'MESH':
#                if obj.data.materials:
#                    materialpreserver.main(obj,part)
        
        scn.objects.active = bpy.data.objects[part.part]
        if emptysize:
            radius = max(emptysize)
        else:
            radius = bpy.context.active_object.empty_draw_size
            if radius < .25:
                radius = 0.25
        bpy.data.objects[part.part].empty_draw_size = radius
    
    bpy.ops.object.select_all(action = 'DESELECT')
    print("\n----------------------------------------------------\n") 

    return craft
    
    #have craft and part classes imported from their own file, copy this structure
    #if not mu.read(filepath):
    #    bpy.context.user_preferences.edit.use_global_undo = undo
    #    operator.report({'ERROR'},
    #        "Unrecognized format: %s %d" % (mu.magic, mu.version))
    #    return {'CANCELLED'}

    #create_textures(mu, os.path.dirname(filepath))
    #create_materials(mu)
    #mu.objects = {}
    #obj = create_object(mu, mu.obj, None, create_colliders, [])
    #bpy.context.scene.objects.active = obj
    #obj.select = True

        
def fairing_fixer(partslist):
    """Unhides fairings if there is a part connected to the bottom of the engine"""
    partdir = part_dir.make()
    for part in partslist:
        if partdir[part.partName][1] == "engine":
            for attN in part.attNlist:
                if attN.loc == "bottom":
                    root = bpy.data.objects[part.part]
                    queue = [child for child in root.children]
                    while len(queue) > 0:
                        current = queue.pop(0)
                        if "fair" in current.name:
                            current.hide = False
                            current.hide_render = False
                        for child in current.children:
                            queue.append(child)


def add_strut(part,objlist):
    scn = bpy.context.scene   
    
    root = bpy.data.objects[part.part]
    root.children[0].hide = True
    for child in root.children[0].children:
        if "anchor" in child.name:
            anchor = child
        if "target" in child.name:
            target = child
            target.empty_draw_type = 'SPHERE'
            target.empty_draw_size = .25
        if "strut" in child.name:
            bpy.ops.object.select_all(action = 'DESELECT')
            newstrut = child.children[0]
            newstrut.select = True
            scn.objects.active = newstrut
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
            bpy.ops.object.select_all(action = 'DESELECT')
     
    if newstrut.constraints:
        scn.objects.active = newstrut
        newstrut.constraints.clear()
        const = newstrut.constraints.new("STRETCH_TO")
    else:
        const = newstrut.constraints.new("STRETCH_TO")
    const.target = target
    const.bulge = 0
           
    anchor.delta_location = Vector(part.attPos)
    anchor.delta_rotation_quaternion = Quaternion(part.attRot)
    target.location = Vector(part.tgtpos)
    target.rotation_quaternion = Quaternion(part.tgtrot)
    
    for obj in objlist:
        if obj.type == 'MESH':
            scn.objects.active = obj 
            if obj.data.materials:
                material_fixer(obj,part)
                
            bpy.ops.object.mode_set(mode='EDIT')                                                                # go into edit mode
            bpy.ops.mesh.remove_doubles(threshold = 0.0001)                                                     # remove double vertices
            bpy.ops.mesh.normals_make_consistent(inside = False)                                                # fix normals
            bpy.ops.object.mode_set(mode='OBJECT')                                                              # leave edit mode
            
            obj.select = True
            bpy.ops.object.shade_smooth()
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = .610865
            bpy.ops.object.select_all(action = 'DESELECT')
            
        if obj.parent == None:
            obj.empty_draw_type = 'SPHERE'
            obj.empty_draw_size = .25
        if "coll" in obj.name:
            obj.hide = True
            obj.hide_render = True
        if "obj_strut" in obj.name and obj.type == 'MESH' and obj.data.materials:
            strutmat = obj.data.materials[0]

    strutlen = (anchor.location - target.location).magnitude*10
    print(strutlen)
    newstrut.data.vertices[1].co.y = strutlen
    print(newstrut.data.vertices[1].co.y)
    newstrut.data.vertices[5].co.y = strutlen
    newstrut.data.vertices[6].co.y = strutlen
    newstrut.data.vertices[7].co.y = strutlen
    
    target.children[0].data.materials[0] = strutmat
    
    gl0 = strutmat.node_tree.nodes['Glossy BSDF']
    
    for link in strutmat.node_tree.links:
        if link.to_node == gl0:
            strutmat.node_tree.links.remove(link)
    
    co0 = strutmat.node_tree.nodes.new('ShaderNodeRGB')
    co0.location = (800,150)
    strutmat.node_tree.nodes["RGB"].outputs[0].default_value = (0.3, 0.3, 0.3, 1)
    strutmat.node_tree.links.new(co0.outputs['Color'],gl0.inputs['Color'])
    gl0.inputs[1].default_value=.2
    
    
def add_fuelline(part,objlist):     
    scn = bpy.context.scene
    
    root = bpy.data.objects[part.part]
    root.rotation_quaternion = Quaternion(part.rotQ)
    print(root.rotation_quaternion)
    print(part.rotQ)
    root.children[0].hide = True
    for child in root.children[0].children:
        if "anchor" in child.name:
            anchor = child
        if "target" in child.name:
            target = child
            target.empty_draw_type = 'SPHERE'
            target.empty_draw_size = .25
        if "line" in child.name:
            bpy.ops.object.select_all(action = 'DESELECT')
            newfuelline = child.children[0]
            newfuelline.select = True
            scn.objects.active = newfuelline
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
            bpy.ops.object.select_all(action = 'DESELECT')

    if newfuelline.constraints:
        scn.objects.active = newfuelline
        newfuelline.constraints.clear()
        const = newfuelline.constraints.new("STRETCH_TO")
    else:
        const = newfuelline.constraints.new("STRETCH_TO")
    const.target = target.children[1]
    const.bulge = 0  

    anchor.delta_location = Vector(part.attPos)
    anchor.rotation_quaternion = Quaternion(part.attRot)
    target.location = Vector(part.tgtpos)
    target.rotation_quaternion = Quaternion(part.tgtrot)
    
    for obj in objlist:
        if obj.type == 'MESH':
            scn.objects.active = obj 
            if obj.data.materials:
                material_fixer(obj,part)
                
            bpy.ops.object.mode_set(mode='EDIT')                                                                # go into edit mode
            bpy.ops.mesh.remove_doubles(threshold = 0.0001)                                                     # remove double vertices
            bpy.ops.mesh.normals_make_consistent(inside = False)                                                # fix normals
            bpy.ops.object.mode_set(mode='OBJECT')                                                              # leave edit mode
            
            obj.select = True
            bpy.ops.object.shade_smooth()
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = .610865
            bpy.ops.object.select_all(action = 'DESELECT')
            
        if obj.parent == None:
            obj.empty_draw_type = 'SPHERE'
            obj.empty_draw_size = .25
        if "coll" in obj.name:
            obj.hide = True
            obj.hide_render = True
        if "Cap" in obj.name and obj.type == 'EMPTY':
            obj.hide = True
    
    fuellen = (target.location - anchor.location).magnitude*10
    newfuelline.data.vertices[5].co.y = fuellen
    newfuelline.data.vertices[6].co.y = fuellen
    newfuelline.data.vertices[7].co.y = fuellen
    newfuelline.data.vertices[8].co.y = fuellen
    newfuelline.data.vertices[9].co.y = fuellen
   
    
    #newfuelline.parent.rotation_quaternion = Vector((1,0,0,-1))
    #newfuelline.parent.delta_rotation_quaternion = -Quaternion(part.attRot0)
    #newfuelline.parent.rotation_mode = 'XYZ'
    #newfuelline.parent.delta_rotation_euler = Vector((math.pi/2,.95*math.asin((target.location[2]-anchor.location[2])/((anchor.location-target.location).magnitude)),0.05))
    #newfuelline.parent.delta_rotation_euler = Vector((0,math.asin((target.location[2]-anchor.location[2])/((anchor.location-target.location).magnitude)),0))
    
    #newfuelline.parent.delta_rotation_euler = Quaternion(part.attRot0).to_euler()
    #newfuelline.parent.rotation_mode = 'QUATERNION'
    #newfuelline.parent.delta_rotation_euler = Vector((0,0,math.asin((target.location[0]-anchor.location[0])/((target.location-anchor.location).length))))

    
def add_launchclamp(part,objlist):   
    scn = bpy.context.scene
    root = bpy.data.objects[part.part]

    mat = root.matrix_local
    for child in root.children[0].children:
        if "girder" in child.name:
            girder = child
            for grandchild in girder.children:
                if "ground" in grandchild.name:
                    ground = grandchild
                    groundmesh = ground.children[0]
                    bpy.ops.object.select_all(action = 'DESELECT')
                    scn.objects.active = ground
                    ground.select = True
                    ground.delta_location = (0,.94,0) 
                    if not len(ground.constraints):
                        const = ground.constraints.new("LIMIT_LOCATION")
                        const.use_min_z  = True
                        const.use_max_z  = True
                        const.min_z  = 5
                        const.max_z  = 5
                    bpy.ops.object.select_all(action = 'DESELECT')
                    ground.location = (ground.location[0],ground.location[1],-mat.to_translation()[2]-ground.location[2])
        if "ground" in child.name:
            ground = child
            groundmesh = ground.children[0]
            ground.parent = girder
            bpy.ops.object.select_all(action = 'DESELECT')
            scn.objects.active = ground
            ground.select = True
            ground.delta_location = (0,.94,0) 
            if not len(ground.constraints):
                const = ground.constraints.new("LIMIT_LOCATION")
                const.use_min_z  = True
                const.use_max_z  = True
                const.min_z  = 5
                const.max_z  = 5
            bpy.ops.object.select_all(action = 'DESELECT')
            ground.location = (ground.location[0],ground.location[1],-mat.to_translation()[2]-ground.location[2])
        if "cap" in child.name:
            for grandchild in child.children:
                if "_mesh" in grandchild.name:
                    capmesh = grandchild
    for child in root.children[0].children:
        if "girder" in child.name:
            girder = child
            bpy.ops.object.select_all(action = 'DESELECT')
            newgirder = child.children[0].children[0]
            newgirder.select = True
            scn.objects.active = newgirder
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
            
            bpy.ops.object.mode_set(mode='EDIT')                                                                # go into edit mode
            bpy.ops.mesh.remove_doubles(threshold = 0.0001)                                                     # remove double vertices
            bpy.ops.mesh.normals_make_consistent(inside = False)                                                # fix normals
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')                                                              # leave edit mode
            
            botverts = [0,3,4,8,9,10,11,12,13,14,15,25,26,28,29,31]
            topverts = [1,2,5,6,7,16,17,18,19,20,21,22,23,24,27,30]
            bpy.ops.object.select_all(action = 'DESELECT')
            scn.objects.active = newgirder
            newgirder.select = True
            
            
            for vert in botverts:
                newgirder.data.vertices[vert].select = True
                newgirder.data.vertices[vert].co.y = -mat.to_translation()[2]
                #newgirder.data.vertices[vert].co.y = newgirder.data.vertices[1].co.y
                newgirder.data.vertices[vert].select = False
            if not len(newgirder.vertex_groups):
                bpy.ops.object.vertex_group_add()
                newgirder.vertex_groups[0].name = 'bottom'
                bpy.ops.object.vertex_group_set_active(group = 'bottom')
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.vertex_group_assign()
                #bpy.ops.view3d.snap_cursor_to_selected()
                
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.editmode_toggle()
            
                for vert in topverts:
                    newgirder.data.vertices[vert].select = True
                bpy.ops.object.vertex_group_add()
                newgirder.vertex_groups[1].name = 'top'
                bpy.ops.object.vertex_group_set_active(group = 'top')
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.vertex_group_assign()
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.editmode_toggle()
            
            if len(newgirder.modifiers) == 0:
                bpy.ops.object.modifier_add(type='HOOK')
                #bpy.ops.object.modifier_add(type='HOOK')
            
            bpy.context.object.modifiers[0].name = "bottom_hook"
            bpy.context.object.modifiers[0].object = groundmesh
            bpy.context.object.modifiers[0].vertex_group = "bottom"
            bpy.context.object.modifiers[0].force = 1
            
            #bpy.context.object.modifiers[1].name = "top_hook"
            #bpy.context.object.modifiers[1].object = capmesh
            #bpy.context.object.modifiers[1].vertex_group = "top"
            #bpy.context.object.modifiers[1].force = 0
            
            bpy.ops.object.select_all(action = 'DESELECT')   
            
        
        
    girder.rotation_mode = 'XYZ'
    mate = mat.to_euler()
    girder.rotation_euler = Vector((-mate[0],0,mate[1]))
    
    
    #bpy.ops.object.select_all(action = 'DESELECT')
    #newroot = root.children[0]
    #scn.objects.active = newroot
    #newroot.select = True
    #bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    #bpy.ops.object.select_all(action = 'DESELECT')
    
    #FIX EVENTUALLY... CONTROL EMPTY IS OFF SOMEWHERE RANDOM
   
    #rootname = root.name
    #root.name = "oldroot"
    #newroot.name = rootname
    #root.parent = newroot
    #root.hide = True
    
    for obj in objlist:
        if obj.type == 'MESH':
            scn.objects.active = obj 
            if obj.data.materials:
                material_fixer(obj,part)
              
            bpy.ops.object.mode_set(mode='EDIT')                                                                # go into edit mode
            bpy.ops.mesh.remove_doubles(threshold = 0.0001)                                                     # remove double vertices
            bpy.ops.mesh.normals_make_consistent(inside = False)                                                # fix normals
            bpy.ops.object.mode_set(mode='OBJECT')                                                              # leave edit mode
            
            obj.select = True
            bpy.ops.object.shade_smooth()
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = .610865
            bpy.ops.object.select_all(action = 'DESELECT')
            
            if len(obj.data.polygons) == 0:
                obj.hide = True
                obj.hide_render = True  
            
        if obj.type == 'EMPTY':
            if obj.parent == None:
                obj.empty_draw_type = 'SPHERE'
                obj.empty_draw_size = 1
            else:
                obj.hide = True
        if "coll" in obj.name:
            if obj.type == 'MESH' and obj.data.materials:
                strutmat = obj.data.materials[0]
            obj.hide = True
            obj.hide_render = True
        if "Cap" in obj.name and obj.type == 'EMPTY':
            obj.hide = True
        
        action_fixer(obj)
        obj.select = False
        scn.objects.active = None
    
    bpy.ops.object.select_all(action = 'DESELECT')
    
    #for vert in verts:
        #newgirder.data.vertices[vert].co.y = -mat.to_translation()[2]
        
    #ground.delta_location = Vector((0,0,-1))

    
def material_fixer(obj,part):
    
    #kill preexisting at some point

    scn = bpy.context.scene
    scn.objects.active = obj
    mat = obj.data.materials[0]
    
    if "Material Output" in mat.node_tree.nodes:
        return
    
    mat.name = part.partName+"_"+obj.name
    
    tx0 = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    im0 = mat.node_tree.nodes.new('ShaderNodeTexImage')
    ma0 = mat.node_tree.nodes.new('ShaderNodeMath')
    gl0 = mat.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    om0 = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    
    location = [(550,250),(800,450),(1050,350),(1300,300),(1550,300),(800,150),(800,-150),(1300,0),(1800,300)]
    
    tx0.location = location[0]
    mat.node_tree.links.new(tx0.outputs['UV'],im0.inputs['Vector'])
    
    
    ma0.location = location[2]
    mat.node_tree.links.new(ma0.outputs['Value'],gl0.inputs['Roughness'])
    ma0.operation = "DIVIDE"
    ma0.inputs[0].default_value = 1
    
    
    gl0.location = location[3]
    mat.node_tree.links.new(gl0.outputs['BSDF'],om0.inputs['Surface'])
    
    om0.location = location[4]
    
    im0.location = location[1]
    mat.node_tree.links.new(im0.outputs['Color'],gl0.inputs['Color'])
    mat.node_tree.links.new(im0.outputs['Color'],ma0.inputs[1])
    for node in mat.node_tree.nodes:
        if node.label == "mainTex":
            imA = node
            texname = part.part+"_"+obj.name+"_tex"
            imgname = part.part+"_"+obj.name+"_img"
            possible_img = [image for image in bpy.data.images if imA.texture.name in image.name]
            
            if imA.texture.image:  
                im0.image = imA.texture.image
                im0.image.name = imgname
                im0.image.use_alpha = False
            if possible_img:
                im0.image = possible_img[-1]
                im0.image.name = imgname
                im0.image.use_alpha = False
            else:
                print('Failed to find image texture')
            
            possible_tex = [tex for tex in bpy.data.textures if im0.image.name in tex.name]
            if possible_tex:
                imA.texture = possible_tex[-1]
            imA.texture.name = texname
            imA.texture.use_alpha = False
            
        if node.label == "bumpMap":
            im1 = mat.node_tree.nodes.new('ShaderNodeTexImage')
            im1.location = location[5]
            im1.label = "Bump Texture"
            mat.node_tree.links.new(tx0.outputs['UV'],im1.inputs['Vector'])
            mat.node_tree.links.new(im1.outputs['Color'],om0.inputs['Displacement'])
            #may need to scale this down
            
            imB = node.material.active_texture
            texname = part.part+"_"+obj.name+"_bump"
            imgname = part.part+"_"+obj.name+"_imgb"
            possible_img = [image for image in bpy.data.images if imB.name in image.name]
            if imB.image:  
                im1.image = imB.image
                im1.image.name = imgname
            if possible_img:
                im1.image = possible_img[-1]
                im1.image.name = imgname
            else:
                print('Failed to find bump texture')
        
        if node.label == "emissive":
            im2 = mat.node_tree.nodes.new('ShaderNodeTexImage')
            im2.location = location[6]
            im2.label = "Emissive Texture"
            em0 = mat.node_tree.nodes.new('ShaderNodeEmission')
            em0.location = location[7]
            as0 = mat.node_tree.nodes.new('ShaderNodeAddShader')
            as0.location = location[4]
            om0.location = location[8]
            
            mat.node_tree.links.new(tx0.outputs['UV'],im2.inputs['Vector'])
            mat.node_tree.links.new(im2.outputs['Color'],em0.inputs['Strength'])
            mat.node_tree.links.new(im0.outputs['Color'],em0.inputs['Color'])
            mat.node_tree.links.new(em0.outputs['Emission'],as0.inputs[1])
            mat.node_tree.links.new(gl0.outputs['BSDF'],as0.inputs[0])
            mat.node_tree.links.new(as0.outputs['Shader'],om0.inputs['Surface'])
            
            imE = node
            texname = part.part+"_"+obj.name+"_bump"
            imgname = part.part+"_"+obj.name+"_imgb"
            possible_img = [image for image in bpy.data.images if imE.texture.name in image.name]
            if imE.texture.image:  
                im2.image = imE.texture.image
                im2.image.name = imgname
            if possible_img:
                im2.image = possible_img[-1]
                im2.image.name = imgname
            else:
                print('Failed to find emissive texture')

    
def scale_fixer(craft,scale):
    scn = bpy.context.scene
    for part in craft.partslist:
        obj = bpy.data.objects[part.part]
        scn.objects.active = obj
        obj_loc = obj.location
        obj_sca = obj.scale
        obj.location = (scale*obj_loc[0],scale*obj_loc[1],scale*obj_loc[2])
        obj.scale = (scale*obj_sca[0],scale*obj_sca[1],scale*obj_sca[2])
        
    bpy.ops.transform.resize()    

def action_fixer(obj):
    scn = bpy.context.scene
    scn.objects.active = obj
    obj.select = True
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks:
            for strip in track.strips:
                strip_len = strip.frame_end - strip.frame_start
                strip.frame_start = -strip_len-1
                strip.frame_end = -1
                strip.use_reverse = True
    bpy.context.scene.frame_current=1
    bpy.context.scene.frame_current=0
    
def unselectable_fixer():
    scn = bpy.context.scene
    for obj in bpy.data.objects:
        if not obj.parent:
            scn.objects.active = obj
            obj.select = True
            bpy.ops.object.select_grouped(type = 'CHILDREN_RECURSIVE')
            for child in bpy.context.selected_objects:
                child.hide_select = True

def stage_grouper():
    bpy.ops.object.select_all(action = 'DESELECT')
    dstgar = []
    for obj in bpy.data.objects:
        if len(obj.values())>5:
            if obj['dstg'] not in dstgar:
                dstgar.append(obj['dstg'])
    for i in dstgar:
        for obj in bpy.data.objects:
            if len(obj.values())>5:
                if obj['dstg'] == i:
                    obj.select = True
        bpy.ops.group.create()
        bpy.ops.object.select_all(action = 'DESELECT')
