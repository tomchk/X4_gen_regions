import bpy
from bpy_extras import object_utils
from math import (
    sin, cos, pi, radians
)
import mathutils.geometry
from mathutils import Matrix, Vector
import mathutils.noise as Noise

import re
import os
import datetime
from pathlib import Path
from xml.dom import minidom

from . blender_to_anixml import GenerateAniXML

try:
    from lxml import etree
    print("running with lxml.etree")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
            print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
                print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                    print("running with ElementTree")
                except ImportError:
                    print("Failed to import ElementTree from any known place")


class Gen_Orbits_Operator(bpy.types.Operator):
    bl_idname = "view3d.gen_orbits"
    bl_label = "Generate Orbits"
    bl_description = "Generate Orbits for X4"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mytool = context.scene.my_tool
        source = mytool.source
        target = mytool.target
        radius = 1E7 #TODO get from UI or cluster xML
        
        for obj in bpy.context.selected_objects:
            if len(obj.name) > 0: #TODO Change this, and adjust axes? if obj.name.startswith("part_asteroids"):
                AddOrbitAnim(obj,radius,1200,60,0,0)

        GenerateAniXML(target)

        return {'FINISHED'}

# START ORBIT ANIMATION GENERATION
def AddOrbitAnim(obj,radius=1E7,frames=108000,numKeyframes=60,rotationCenterX=0,rotationCenterY=0,angleStart=0,angleEnd=360):
    angle = radians(angleStart)
    omega = radians(angleEnd-angleStart)/numKeyframes

    obj.location.x = rotationCenterX + radius * cos(angle) # Starting x
    obj.location.z = rotationCenterY - radius * sin(angle) # Starting y, at least for DAEs from converter

    i = 0
    while angle <= radians(angleEnd):
        obj.keyframe_insert(data_path="location",frame=i)
        angle = angle + omega
        obj.location.x = obj.location.x + radius * omega * cos(angle + pi / 2) # New x
        obj.location.z = obj.location.z - radius * omega * sin(angle + pi / 2) # New y
        i += frames/numKeyframes
# END ORBIT ANIMATION GENERATION


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = etree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
