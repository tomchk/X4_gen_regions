""" Run:
python "ani_parser.py"
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
from struct import unpack
import os

import xml.etree.ElementTree as etree
from xml.dom import minidom

def prettify(elem):
    rough_string = etree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

sourceFile = (r'D:\Games\Steam\steamapps\common\X4 Foundations\X4_extracted\extensions\ego_dlc_terran\assets\environments\cluster\CLUSTER_101_DATA.ANI')
targetPath = './'

aniXML = etree.Element('root')
dataNode = etree.SubElement(aniXML, 'data')
metadataNode = etree.SubElement(aniXML, 'metadata')

# Header size in bytes
HEADER_SIZE = 16

with open(sourceFile, 'rb') as reader:
    headerData = unpack('IIII', reader.read(HEADER_SIZE))
    header = {
        'NumAnims': headerData[0],
        'KeyOffsetBytes': headerData[1],
        'Version': headerData[2],
        'Padding': headerData[3],
    }
    print(header)

    animDesc = []
    for i in range(header['NumAnims']):
        animData = unpack('64s64sIIIIIfII', reader.read(160))
        animDesc.append({
            'Name': animData[0].decode().split('\x00')[0],
            'Subname': animData[1].decode().split('\x00')[0],
            'NumPosKeys': animData[2],
            'NumRotKeys': animData[3],
            'NumScaleKeys': animData[4],
            'NumPreScaleKeys': animData[5],
            'NumPostScaleKeys': animData[6],
            'Duration': animData[7]
        })
        print(animDesc)

    #Cycle through each animation, processing positions, rotation, etc. keyframes of each
    for i in range(header['NumAnims']):
        partNode = etree.SubElement(dataNode, 'part', {'name': animDesc[i]['Name']})
        catNode = etree.SubElement(partNode, 'category', {'name': "misc"})
        aniNode = etree.SubElement(catNode, 'animation', {'subname': animDesc[i]['Subname']})
        conNode = etree.SubElement(metadataNode, 'connection', {'name': animDesc[i]['Name']})
        aniMetaNode = etree.SubElement(conNode, 'animation', {'subname': animDesc[i]['Subname']})
        etree.SubElement(aniMetaNode, 'frames', {'start': "0", 'end': "108000"}) #TODO Improve this

        locNode = etree.SubElement(aniNode, 'location')
        XA = etree.SubElement(locNode, 'X')
        YA = etree.SubElement(locNode, 'Y')
        ZA = etree.SubElement(locNode, 'Z')
        for iia in range(animDesc[i]['NumPosKeys']):
            kfDataA = unpack('fff4s4s4sffffffffffffffffffI3f3fI', reader.read(128))
            keyframesListA = ['PositionX','PositionY','PositionZ','InterpolationTypesX','InterpolationTypesY','InterpolationTypesZ','Time','CPX1x','CPX1y','CPX2x','CPX2y','CPY1x','CPY1y','CPY2x','CPY2y','CPZ1x','CPZ1y','CPZ2x','CPZ2y','Tension','Continuity','Bias','EaseIn','EaseOut','DerivIn','DerivOut','AngleKey']
            keyframesA = {}
            for iiia in range(len(keyframesListA)):
                keyframesA[keyframesListA[iiia]] = kfDataA[iiia]
            print(keyframesA)
            frameLocX = etree.SubElement(XA, 'frame', {'id': str(int(keyframesA['Time']*30))})
            frameLocY = etree.SubElement(YA, 'frame', {'id': str(int(keyframesA['Time']*30))})
            frameLocZ = etree.SubElement(ZA, 'frame', {'id': str(int(keyframesA['Time']*30))})

        rotNode = etree.SubElement(aniNode, 'rotation_euler')
        XB = etree.SubElement(locNode, 'X')
        YB = etree.SubElement(locNode, 'Y')
        ZB = etree.SubElement(locNode, 'Z')
        for iib in range(animDesc[i]['NumRotKeys']):
            frameRotX = etree.SubElement(XB, 'frame')
            frameRotY = etree.SubElement(YB, 'frame')
            frameRotZ = etree.SubElement(ZB, 'frame')
            kfDataB = unpack('fff4s4s4sffffffffffffffffffI3f3fI', reader.read(128))
            keyframesListB = ['RotationX','RotationY','RotationZ','InterpolationTypesX','InterpolationTypesY','InterpolationTypesZ','Time','CPX1x','CPX1y','CPX2x','CPX2y','CPY1x','CPY1y','CPY2x','CPY2y','CPZ1x','CPZ1y','CPZ2x','CPZ2y','Tension','Continuity','Bias','EaseIn','EaseOut','DerivIn','DerivOut','AngleKey']
            keyframesB = {}
            for iiib in range(len(keyframesListB)):
                keyframesB[keyframesListB[iiib]] = kfDataB[iiib]
            print(keyframesB)

aniXMLFile = (targetPath + 'target_ani.xml')
os.makedirs(os.path.dirname(aniXMLFile), exist_ok=True)
with open(aniXMLFile, "w") as f:
    f.write(prettify(aniXML))
f.close()
