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

        GenerateAniXML()

        return {'FINISHED'}

# START ORBIT ANIMATION GENERATION
def AddOrbitAnim(obj,radius=1E7,frames=108000,numKeyframes=60,rotationCenterX=0,rotationCenterY=0,angleStart=0,angleEnd=360):
    angle = radians(angleStart)
    omega = radians(angleEnd)/numKeyframes

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


def keyFrameOutput(index,coordElem,fcs):
    for p in fcs[index].keyframe_points:
        frameNode = etree.SubElement(coordElem, 'frame', {'id': str(p.co[0]), 'value': str(p.co[1]), 'interpolation': p.interpolation.replace('CONSTANT','STEP')})
        etree.SubElement(frameNode, 'handle_right', {'X': str(p.handle_right[0]), 'Y': str(p.handle_right[1])})
        etree.SubElement(frameNode, 'handle_left', {'X': str(p.handle_left[0]), 'Y': str(p.handle_left[1])})


def GenerateAniXML():
    aniXML = etree.Element('root')
    dataNode = etree.SubElement(aniXML, 'data')
    metadataNode = etree.SubElement(aniXML, 'metadata')
    
    for obj in bpy.context.selected_objects:
        if len(obj.name) > 0: #TODO Change this, and adjust axes? if obj.name.startswith("part_asteroids"):
            fcurves = obj.animation_data.action.fcurves
            partNode = etree.SubElement(dataNode, 'part', {'name': obj.name})
            catNode = etree.SubElement(partNode, 'category', {'name': "misc"})
            aniNode = etree.SubElement(catNode, 'animation', {'subname': "loop"})
            locNode = etree.SubElement(aniNode, 'location')
            rotEulerNode = etree.SubElement(aniNode, 'rotation_euler')
            conNode = etree.SubElement(metadataNode, 'connection', {'name': obj.name})
            aniMetaNode = etree.SubElement(conNode, 'animation', {'subname': "loop"})
            frame_start, frame_end = map(int, obj.animation_data.action.frame_range)
            etree.SubElement(aniMetaNode, 'frames', {'start': str(frame_start), 'end': str(frame_end)}) # TODO
            
            # Loop through all fcurves of the object animation
            for xyz in range(len(fcurves)):
                if fcurves[xyz].data_path == 'location':
                    if xyz == 0:
                        X = etree.SubElement(locNode, 'X')
                        keyFrameOutput(xyz,X,fcurves)
                    if xyz == 1:
                        Y = etree.SubElement(locNode, 'Y')
                        keyFrameOutput(xyz,Y,fcurves)
                    if xyz == 2:
                        Z = etree.SubElement(locNode, 'Z')
                        keyFrameOutput(xyz,Z,fcurves)
                if fcurves[xyz].data_path == 'rotation_euler':
                    if xyz == 0:
                        X = etree.SubElement(rotEulerNode, 'X')
                        keyFrameOutput(xyz,X,fcurves)
                    if xyz == 1:
                        Y = etree.SubElement(rotEulerNode, 'Y')
                        keyFrameOutput(xyz,Y,fcurves)
                    if xyz == 2:
                        Z = etree.SubElement(rotEulerNode, 'Z')
                        keyFrameOutput(xyz,Z,fcurves)
                if fcurves[xyz].data_path != 'location' and fcurves[xyz].data_path != 'rotation_euler': # TODO Handle better; Not finished!
                    otherDataPathNode = etree.SubElement(aniNode, fcurves[xyz].data_path)
                    if xyz == 0:
                        X = etree.SubElement(otherDataPathNode, 'X')
                        keyFrameOutput(xyz,X,fcurves)
                    if xyz == 1:
                        Y = etree.SubElement(otherDataPathNode, 'Y')
                        keyFrameOutput(xyz,Y,fcurves)
                    if xyz == 2:
                        Z = etree.SubElement(otherDataPathNode, 'Z')
                        keyFrameOutput(xyz,Z,fcurves)

                #print("%s[%i]" % (fcurves[xyz].data_path, fcurves[xyz].array_index)) # data_path is location, rotation_euler, etc.; array_index is x=0, y=1, z=2

    targetPath = r'D:/X4_out/X4_gen_regions/' # TODO Testing ONLY
    aniXMLFile = (targetPath + 'testout.anixml')
    os.makedirs(os.path.dirname(aniXMLFile), exist_ok=True)
    with open(aniXMLFile, "w") as f:
        f.write(prettify(aniXML))
    f.close()
