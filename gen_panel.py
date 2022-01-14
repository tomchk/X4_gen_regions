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
        default="D:/X4_out/planet_builder/maps/demo_universe/demo_sectors.xml",
        maxlen=1024,
        )

    target: StringProperty(
        name="Target",
        description="Enter target folder here",
        default="D:/X4_out/X4_gen_regions/",
        maxlen=1024,
        )

    seed: StringProperty(
        name="Seed",
        description="Enter seed here. You should get the same results with the same seed.",
        default="4231",
        maxlen=1024,
        )

    densityMultiplier: StringProperty(
        name="Density Multiplier",
        description="This affects the densityfactor for all fields. 0.5 appears to be the best. Change with caution.",
        default="0.5",
        maxlen=10,
        )

class GEN_PT_Panel(bpy.types.Panel):
    bl_idname = "GEN_PT_Panel_id"
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
        layout.prop(mytool, "seed")
        layout.prop(mytool, "densityMultiplier")
        layout.separator()

        row = layout.row()
        row.operator("view3d.gen_regions", text="Generate Regions")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("view3d.gen_orbits", text="Generate Orbits")
        row = layout.row()
        row.operator("view3d.gen_orbits_in_cluster", text="Animate Cluster")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("view3d.blender_to_anixml", text="Export to AniXML")
        row = layout.row()
        row.operator("view3d.gen_ani", text="AniXML to Ani")
