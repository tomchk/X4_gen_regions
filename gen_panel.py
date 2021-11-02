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

from bpy.props import (StringProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       PropertyGroup,
                       )


class MyProperties(PropertyGroup):

    source: StringProperty(
        name="Source",
        description="Paste clusters.xml full file path here",
        default="",
        maxlen=1024,
        )

    target: StringProperty(
        name="Target",
        description="Enter Target Folder here",
        default="",
        maxlen=1024,
        )


class Gen_PT_Panel(bpy.types.Panel):
    bl_idname = "Gen_PT_Panel"
    bl_label = "Generator Panel"
    bl_category = "Generator" #"Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_context = "objectmode"  

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
       
        layout.prop(mytool, "source")
        layout.prop(mytool, "target")
        layout.separator()

        row = layout.row()
        row.operator("view3d.gen_regions", text="Generate Regions")
