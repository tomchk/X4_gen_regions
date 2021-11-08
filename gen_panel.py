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
        description="Paste full file path here",
        default="",
        maxlen=1024,
        )

    target: StringProperty(
        name="Target",
        description="Enter target folder here",
        default="",
        maxlen=1024,
        )


class Gen_PT_Panel(bpy.types.Panel):
    bl_idname = "Gen_PT_Panel"
    bl_label = "X4 Generator Panel"
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
        row = layout.row()
        row.operator("view3d.gen_orbits", text="Generate Orbits")
        row = layout.row()
        row.operator("view3d.gen_orbits_in_cluster", text="Animate Cluster")
