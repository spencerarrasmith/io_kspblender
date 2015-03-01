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

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy.props import BoolVectorProperty, CollectionProperty, PointerProperty
from bpy.props import FloatVectorProperty, IntProperty
from mathutils import Vector,Matrix,Quaternion

class KSPBProperties(bpy.types.PropertyGroup):
    ship = StringProperty(name = "ship", default = "UFO")

class KSPBPropertiesPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_label = 'KSPB Properties'

    @classmethod
    def poll(cls, context):
        return True

    def draw(self,context):
        layout = self.layout
        kspbprops = context.active_object.kspbproperties
        row = layout.row()
        col = row.column()
        col.prop(kspbprops, "ship")
        

def register():
    bpy.types.Object.kspbproperties = PointerProperty(type=KSPBProperties)

def unregister():
    pass
