""" Run:
python "gen_ani.py"
"""
"""
// Note that these add up to exactly 128 bytes
  float ValueX, ValueY, ValueZ;                          /< The key's actual value (position, rotation, etc.). 12*/
  InterpolationType InterpolationX;                      /< The type of interpolation for the x part of the key. 20/
  InterpolationType InterpolationY;                      /**< The type of interpolation for the y part of the key. 24/
  InterpolationType InterpolationZ;                      /< The type of interpolation for the z part of the key. 28*/
  float Time;

  /< 32 Time in s of the key frame - based on the start of the complete animation. - This value is also used as a unique identifier for the key meaning that two keys with the same time are considered the same! - We use a float rather than an XTIME to safe memory, because floating point precision is good enough for key times. /

  float CPX1x, CPX1y;                                    /**< First control point for the x value. 8/
  float CPX2x, CPX2y;                                    /< Second control point for the x value. 16*/
  float CPY1x, CPY1y;                                /< First control point for the y value. 24/
  float CPY2x, CPY2y;                                /**< Second control point for the y value. 32/
  float CPZ1x, CPZ1y;                                /< First control point for the z value. 40*/
  float CPZ2x, CPZ2y;                                /< Second control point for the z value. 48*/
  float Tens = 0;                                            /< Tension. 4*/
  float Cont = 0;                                            /< Continuity. 8/
  float Bias = 0;                                            /**< Bias. 12/
  float EaseIn = 0;                                        /< Ease In. 16*/
  float EaseOut = 0;                                        /< Ease Out. 20*/
  int Deriv =
      0;                                            /< 24 Indicates whether derivatives have been calculated already. Is mutable to allow it being altered in the CalculateDerivatives() method. */
  float DerivInX = 0, DerivInY = 0, DerivInZ =
      0;                    /< 12 Derivative In value. Is mutable to allow it being altered in the CalculateDerivatives() method. /
  float DerivOutX = 0, DerivOutY = 0, DerivOutZ =
      0;                /**< 24 Derivative Out value.  Is mutable to allow it being altered in the CalculateDerivatives() method./
  uint32_t AngleKey;                                        /** 28        // this will be set to non null if there is a key */
"""
from struct import pack, unpack
import os

import xml.etree.ElementTree as etree
from xml.dom import minidom

def prettify(elem):
    rough_string = etree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

sourceFile = (r'./target_ani.xml')
targetPath = './'

aniFile = (targetPath + 'target.ani')
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
    #     locNode = etree.SubElement(aniNode, 'location')
    #     XA = etree.SubElement(locNode, 'X')
    #     YA = etree.SubElement(locNode, 'Y')
    #     ZA = etree.SubElement(locNode, 'Z')
        for iia in range(numPosKeys[i]):
            writer.write(pack('fff4s4s4sffffffffffffffffffI3f3fI',
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
                0,
                0,
                0,
                0,0,0,0,0 #TODO: Why so many? Check this!
           ))

        for iib in range(numRotKeys[i]):
            writer.write(pack('fff4s4s4sffffffffffffffffffI3f3fI',
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
                0,
                0,
                0,
                0,0,0,0,0
           ))
