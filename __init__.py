bl_info = {
    "name" : "X4_gen_regions",
    "author" : "metame",
    "description" : "Generate regions for X4: Foundations",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from . gen_regions import Gen_Regions_Operator
from . gen_orbits import Gen_Orbits_Operator
from . gen_orbits_in_cluster import Gen_Orbits_In_Cluster_Operator
from . blender_to_anixml import Blender_To_AniXML_Operator
from . gen_ani import Gen_Ani_Operator
from . gen_panel import MyProperties
from . gen_panel import GEN_PT_Panel

from bpy.props import (StringProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       PropertyGroup,
                       )


classes = (Gen_Regions_Operator, Gen_Orbits_Operator, Gen_Orbits_In_Cluster_Operator, Blender_To_AniXML_Operator, Gen_Ani_Operator, MyProperties, GEN_PT_Panel)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()