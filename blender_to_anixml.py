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


class Blender_To_AniXML_Operator(bpy.types.Operator):
    bl_idname = "view3d.blender_to_anixml"
    bl_label = "Only Export Animations"
    bl_description = "Only Export Selected Animations for X4 (no generation)"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mytool = context.scene.my_tool
        source = mytool.source
        target = mytool.target
        
        GenerateAniXML(target)

        return {'FINISHED'}


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


def GenerateAniXML(targetPath):
    aniXML = etree.Element('root')
    dataNode = etree.SubElement(aniXML, 'data')
    metadataNode = etree.SubElement(aniXML, 'metadata')
    
    for obj in bpy.context.selected_objects:
        if len(obj.name) > 0: #TODO Change this, and adjust axes? if obj.name.startswith("part_asteroids"):
            fcurves = obj.animation_data.action.fcurves
            partNode = etree.SubElement(dataNode, 'part', {'name': obj.name})
            blenderSubName = obj.animation_data.action.name
            if blenderSubName.startswith(('playonce','cutscene','gamestart','mode','repeat','signal','doors','cockpit','flaps','gun','turret','weapon','scaling','landing','docking','loop_random','deactivated','activating','active','deactivating','lock','unlock','chair','switch','tlop','flip','flop','wave','scra','tran_','anim_stand','anim_sit','anim_tool','anim_locker','anim_1h','anim_2h','anim_marshal')):
                subName = obj.animation_data.action.name
            else:
                subName = 'loop'
            idx = subName.find('_')
            if idx > 0:
                catNode = etree.SubElement(partNode, 'category', {'name': subName[0:idx]}) # Category is a string before _ of subname, if any
            else:
                catNode = etree.SubElement(partNode, 'category', {'name': "misc"}) # Now we only assume misc if _ is not present or is the first character
            aniNode = etree.SubElement(catNode, 'animation', {'subname': subName})
            conNode = etree.SubElement(metadataNode, 'connection', {'name': obj.name})
            aniMetaNode = etree.SubElement(conNode, 'animation', {'subname': subName})
            frame_start, frame_end = map(int, obj.animation_data.action.frame_range)
            etree.SubElement(aniMetaNode, 'frames', {'start': str(frame_start), 'end': str(frame_end)})
            
            # Loop through all fcurves of the object animation
            for xyz in range(len(fcurves)):
                if fcurves[xyz].data_path == 'location':
                    if len(aniNode.findall("./location")) == 0: locNode = etree.SubElement(aniNode, 'location')
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
                    if len(aniNode.findall("./rotation_euler")) == 0: rotEulerNode = etree.SubElement(aniNode, 'rotation_euler')
                    if xyz == 0:
                        X = etree.SubElement(rotEulerNode, 'X')
                        keyFrameOutput(xyz,X,fcurves)
                    if xyz == 1:
                        Y = etree.SubElement(rotEulerNode, 'Y')
                        keyFrameOutput(xyz,Y,fcurves)
                    if xyz == 2:
                        Z = etree.SubElement(rotEulerNode, 'Z')
                        keyFrameOutput(xyz,Z,fcurves)
                if fcurves[xyz].data_path == 'scale':
                    if len(aniNode.findall("./scale")) == 0: scaleNode = etree.SubElement(aniNode, 'scale')
                    if xyz == 0:
                        X = etree.SubElement(scaleNode, 'X')
                        keyFrameOutput(xyz,X,fcurves)
                    if xyz == 1:
                        Y = etree.SubElement(scaleNode, 'Y')
                        keyFrameOutput(xyz,Y,fcurves)
                    if xyz == 2:
                        Z = etree.SubElement(scaleNode, 'Z')
                        keyFrameOutput(xyz,Z,fcurves)
                # else:
                #     if len(aniNode.findall("./" + fcurves[xyz].data_path)) == 0: otherDataPathNode = etree.SubElement(aniNode, fcurves[xyz].data_path)
                #     if xyz == 0:
                #         X = etree.SubElement(otherDataPathNode, 'X')
                #         keyFrameOutput(xyz,X,fcurves)
                #     if xyz == 1:
                #         Y = etree.SubElement(otherDataPathNode, 'Y')
                #         keyFrameOutput(xyz,Y,fcurves)
                #     if xyz == 2:
                #         Z = etree.SubElement(otherDataPathNode, 'Z')
                #         keyFrameOutput(xyz,Z,fcurves)

                print("%s[%i]" % (fcurves[xyz].data_path, fcurves[xyz].array_index)) # data_path is location, rotation_euler, etc.; array_index is x=0, y=1, z=2

    aniXMLFile = (targetPath + 'output.anixml')
    os.makedirs(os.path.dirname(aniXMLFile), exist_ok=True)
    with open(aniXMLFile, "w") as f:
        f.write(prettify(aniXML))
    f.close()
