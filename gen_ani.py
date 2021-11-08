""" Run:
python "gen_ani.py"
"""
import bpy
from struct import pack
import os

import xml.etree.ElementTree as etree

class Gen_Ani_Operator(bpy.types.Operator):
    bl_idname = "view3d.gen_ani"
    bl_label = "Convert AniXML to Ani"
    bl_description = "Only Convert AniXML to Ani"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mytool = context.scene.my_tool
        source = mytool.source
        target = mytool.target

        AniXMLtoAni(target)

        return {'FINISHED'}


def AniXMLtoAni(targetPath):
    sourceFile = (targetPath + 'output.anixml') #r'D:\X4_out\X4_gen_regions\output.anixml'
    # sourceFile = (r'./target_ani.xml')
    # targetPath = './'

    aniFile = (targetPath + 'output.ani')
    os.makedirs(os.path.dirname(aniFile), exist_ok=True)

    aniXML = etree.parse(sourceFile)
    numAnims = len(aniXML.findall("./data/part"))

    numPosKeys = []
    numRotKeys = []
    duration = []

    InterpolationTypeNameDict = {b'\x00\x00\x00\x00':"UNKNOWN", b'\x01\x00\x00\x00':"STEP", b'\x02\x00\x00\x00':"LINEAR", b'\x03\x00\x00\x00':"QUADRATIC", b'\x04\x00\x00\x00':"CUBIC", b'\x05\x00\x00\x00':"BEZIER", b'\x06\x00\x00\x00':"BEZIER_LINEARTIME", b'\x07\x00\x00\x00':"TCB"}

    with open(aniFile, 'wb') as writer:
        writer.write(pack('IIII', numAnims, 16+numAnims*160, 1, 0)) # Write header
        for i in range(numAnims):
            partName = aniXML.findall("./data/part")[i].attrib['name']
            subName = aniXML.find("./data/part[@name='" + partName + "']/category/animation").attrib['subname']
            numPosKeys.append(len(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame")))
            numRotKeys.append(len(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame")))
            duration.append(int((int(aniXML.find("./metadata/connection[@name='" + partName + "']/animation/frames").attrib['end']) - int(aniXML.find("./metadata/connection[@name='" + partName + "']/animation/frames").attrib['start']))/30))
            writer.write(pack('64s64sIIIIIfII', # Write AnimDesc
                partName.encode(),
                subName.encode(),
                numPosKeys[i],
                numRotKeys[i],
                0,
                0,
                0,
                int(duration[i]),
                0,
                0
            ))

        # #Cycle through each animation, processing positions, rotation, etc. keyframes of each
        for i in range(numAnims):
            partName = aniXML.findall("./data/part")[i].attrib['name']
            for iia in range(numPosKeys[i]):
                writer.write(pack('fff4s4s4sffffffffffffffffffIffffffI',
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame")[iia].attrib['value']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Y/frame")[iia].attrib['value']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Z/frame")[iia].attrib['value']),
                    list(InterpolationTypeNameDict.keys())[list(InterpolationTypeNameDict.values()).index(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame")[iia].attrib['interpolation'])],
                    list(InterpolationTypeNameDict.keys())[list(InterpolationTypeNameDict.values()).index(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Y/frame")[iia].attrib['interpolation'])],
                    list(InterpolationTypeNameDict.keys())[list(InterpolationTypeNameDict.values()).index(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Z/frame")[iia].attrib['interpolation'])],
                    float(float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame")[iia].attrib['id'])/30),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame/handle_right")[iia].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame/handle_right")[iia].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame/handle_left")[iia].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/X/frame/handle_left")[iia].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Y/frame/handle_right")[iia].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Y/frame/handle_right")[iia].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Y/frame/handle_left")[iia].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Y/frame/handle_left")[iia].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Z/frame/handle_right")[iia].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Z/frame/handle_right")[iia].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Z/frame/handle_left")[iia].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/location/Z/frame/handle_left")[iia].attrib['Y']),
                    0,
                    0,
                    0,
                    0,
                    0,
                    int(0),
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    int(0)
            ))

            for iib in range(numRotKeys[i]):
                writer.write(pack('fff4s4s4sffffffffffffffffffIffffffI',
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame")[iib].attrib['value']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Y/frame")[iib].attrib['value']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Z/frame")[iib].attrib['value']),
                    list(InterpolationTypeNameDict.keys())[list(InterpolationTypeNameDict.values()).index(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame")[iib].attrib['interpolation'])],
                    list(InterpolationTypeNameDict.keys())[list(InterpolationTypeNameDict.values()).index(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Y/frame")[iib].attrib['interpolation'])],
                    list(InterpolationTypeNameDict.keys())[list(InterpolationTypeNameDict.values()).index(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Z/frame")[iib].attrib['interpolation'])],
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame")[iib].attrib['id'])/30,
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame/handle_right")[iib].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame/handle_right")[iib].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame/handle_left")[iib].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/X/frame/handle_left")[iib].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Y/frame/handle_right")[iib].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Y/frame/handle_right")[iib].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Y/frame/handle_left")[iib].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Y/frame/handle_left")[iib].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Z/frame/handle_right")[iib].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Z/frame/handle_right")[iib].attrib['Y']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Z/frame/handle_left")[iib].attrib['X']),
                    float(aniXML.findall("./data/part[@name='" + partName + "']/category/animation/rotation_euler/Z/frame/handle_left")[iib].attrib['Y']),
                    0,
                    0,
                    0,
                    0,
                    0,
                    int(0),
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    int(0)
            ))
