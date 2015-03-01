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

bl_info = {
    "name": "KSPBlender .craft Import (KSP)",
    "author": "Spencer Arrasmith",
    "blender": (2, 7, 3),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import KSP .craft file",
    "warning": "beta build",
    "wiki_url": "",
    "tracker_url": "",
#    "support": 'OFFICIAL',
    "category": "Import-Export"}


if "bpy" in locals():
    import imp
    if "import_craft" in locals():
        imp.reload(import_craft)

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy.props import FloatVectorProperty, PointerProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper, path_reference_mode, axis_conversion

from . import properties

class ImportCraft(bpy.types.Operator, ImportHelper):
    '''Import KSP .craft file'''
    bl_idname = "import_object.ksp_craft"
    bl_label = "Import Craft"
    bl_description = """Import KSP .craft file"""
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".craft"
    filter_glob = StringProperty(default="*.craft", options={'HIDDEN'})

    
    def execute(self, context):
        from . import import_craft
        keywords = self.as_keywords (ignore=("filter_glob",))
        return import_craft.import_craft(self,context,**keywords)


def menu_func_import(self, context):
    self.layout.operator(ImportCraft.bl_idname, text="KSP Craft (.craft)")


class SelectShipOperator(bpy.types.Operator):
    bl_idname = "object.select_ship"
    bl_label = "Select Ship"
    
    def execute(self,context):
        scn = bpy.context.scene
        selected = bpy.context.selected_objects
        shippart = selected.pop(0)
        bpy.ops.object.select_all(action = 'DESELECT')
        shippart.select = True
        
        for obj in bpy.data.objects:
            if not obj.parent:
                if obj["ship"] == shippart["ship"]:
                    obj.select = True
                    
        return {'FINISHED'}
        

class DeletePartOperator(bpy.types.Operator):
    bl_idname = "object.delete_part"
    bl_label = "Delete Part"

    def execute(self,context):
        scn = bpy.context.scene
        kill = bpy.context.selected_objects

        for obj in kill:
            if obj.parent == None:
                queue = [obj]

                while queue:
                    current = queue.pop(0)
                    current.hide_select = False
                    current.hide = False
                    current.select = True
                    scn.objects.active = current
                    for child in current.children:
                        queue.append(child)
                        
                bpy.ops.object.delete(use_global = False)
        return {'FINISHED'}

    
class ToggleDeployOperator(bpy.types.Operator):
    bl_idname = "object.toggle_deploy"
    bl_label = "Toggle Deploy"

    def execute(self,context):
        scn = bpy.context.scene
        toggle = bpy.context.selected_objects
        selection = toggle
        
        while toggle:
            curobj = toggle.pop(0)
            for child in curobj.children:
                toggle.append(child)
                
            scn.objects.active = curobj
            curobj.select = True
            if curobj.animation_data:
                for track in curobj.animation_data.nla_tracks:
                    for strip in track.strips:
                        strip.use_reverse = not(strip.use_reverse)
                        
            curobj.select = False
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.context.scene.frame_current=1
        bpy.context.scene.frame_current=0
        for object in selection:
            object.select = True
        return {'FINISHED'}

    
class ToggleEditableOperator(bpy.types.Operator):
    bl_idname = "object.toggle_editable"
    bl_label = "Toggle Editable"

    def execute(self,context):
        scn = bpy.context.scene
        editable = bpy.context.selected_objects
        
        while editable:
            curobj = editable.pop(0)
            for child in curobj.children:
                editable.append(child)
                
            if curobj.type == "MESH" and curobj.hide == False:
                scn.objects.active = curobj
                curobj.select = True
                curobj.hide_select = not(curobj.hide_select)
                
        return {'FINISHED'}


class SelectAllOfThisPartOperator(bpy.types.Operator):
    bl_idname = "object.select_part"
    bl_label = "Select All of This Part"
    
    def execute(self,context):
        scn = bpy.context.scene
        selected = bpy.context.selected_objects
        
        for obj in bpy.data.objects:
            if not obj.parent and 'partName' in obj.keys():
                for sel_obj in selected:
                    if obj['partName'] == sel_obj['partName']:
                        obj.select = True
        
        return {'FINISHED'}

#class LoadFlagPartOperator(bpy.types.Operator):
#    bl_idname = "object.load_flag"
#    bl_label = "Load Flag"
    
    #filename = StringProperty(name="Flag Image", subtype="FILE_PATH")
    
    
#    def execute(self,context):
#        loadflag.main()
#        return {'FINISHED'}
    
# EnableEditingOperator
# DisableEditingOperator
# ChangeSymmetryOperator
# JoinAllMeshesOperator
# SetMaterialAllOperator





class KSPBMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_KSPBMenu"
    bl_label = "KSPBlender Menu"
    
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.shade_smooth", text="Shade Smooth")
        layout.operator("object.shade_flat", text="Shade Flat")
        layout.separator()
        layout.operator_menu_enum("object.modifier_add", "type")
        layout.separator()
        layout.operator_menu_enum("object.constraint_add", "type")
        layout.separator()
        layout.menu("VIEW3D_MT_transform")
        layout.separator()
        layout.operator("object.select_ship", text="Select Ship")
        layout.operator("object.select_part", text="Select All Of This Part")
        layout.operator("object.delete_part", text="Delete Part")
        layout.operator("object.toggle_deploy", text="Toggle Deploy")
        layout.operator("object.toggle_editable", text="Toggle Editable")
        

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    properties.register()

    km = bpy.context.window_manager.keyconfigs.default.keymaps['3D View']
    kmi = km.keymap_items.new('wm.call_menu', 'K', 'PRESS')
    kmi.properties.name = "OBJECT_MT_KSPBMenu"

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    properties.unregister()
    for kmi in km.keymap_items:
        if kmi.idname == "wm.call_menu" and kmi.properties.name == "OBJECT_MT_KSPBMenu":
            km.keymap_items.remove(kmi)


if __name__ == "__main":
    register()
