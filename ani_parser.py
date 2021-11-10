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

# sourceFile = (r'D:\Games\Steam\steamapps\common\X4 Foundations\X4_extracted\extensions\ego_dlc_terran\assets\environments\cluster\CLUSTER_101_DATA.ANI')
# sourceFile = r'C:\Games\Steam\steamapps\common\X Rebirth\extensions\skyhook\assets\environments\cluster\cluster_new_data.ani'
sourceFile = r'D:\Games\Steam\steamapps\common\X4 Foundations\X4_extracted\assets\units\size_s\SHIP_ARG_S_HEAVYFIGHTER_02_DATA.ANI'
targetPath = './'

aniXML = etree.Element('root')
dataNode = etree.SubElement(aniXML, 'data')
metadataNode = etree.SubElement(aniXML, 'metadata')

# Header size in bytes
HEADER_SIZE = 16
InterpolationTypeNameDict = {b'\x00\x00\x00\x00':"UNKNOWN", b'\x01\x00\x00\x00':"STEP", b'\x02\x00\x00\x00':"LINEAR", b'\x03\x00\x00\x00':"QUADRATIC", b'\x04\x00\x00\x00':"CUBIC", b'\x05\x00\x00\x00':"BEZIER", b'\x06\x00\x00\x00':"BEZIER_LINEARTIME", b'\x07\x00\x00\x00':"TCB"}

with open(sourceFile, 'rb') as reader:
    headerData = unpack('IIII', reader.read(HEADER_SIZE))
    header = {
        'NumAnims': headerData[0],
        'KeyOffsetBytes': headerData[1], #This is just 16 + NumAnims*160
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
    keyframesListA = ['PositionX','PositionY','PositionZ','InterpolationTypeX','InterpolationTypeY','InterpolationTypeZ','Time','CPX1x','CPX1y','CPX2x','CPX2y','CPY1x','CPY1y','CPY2x','CPY2y','CPZ1x','CPZ1y','CPZ2x','CPZ2y','Tension','Continuity','Bias','EaseIn','EaseOut','Deriv','DerivInX','DerivInY','DerivInZ','DerivOutX','DerivOutY','DerivOutZ','AngleKey']
    keyframesListB = ['RotationX','RotationY','RotationZ','InterpolationTypeX','InterpolationTypeY','InterpolationTypeZ','Time','CPX1x','CPX1y','CPX2x','CPX2y','CPY1x','CPY1y','CPY2x','CPY2y','CPZ1x','CPZ1y','CPZ2x','CPZ2y','Tension','Continuity','Bias','EaseIn','EaseOut','Deriv','DerivInX','DerivInY','DerivInZ','DerivOutX','DerivOutY','DerivOutZ','AngleKey']

    #Cycle through each animation, processing positions, rotation, etc. keyframes of each
    for i in range(header['NumAnims']):
        if len(dataNode.findall("./part[@name='" + animDesc[i]['Name'] + "']")) == 0: 
            partNode = etree.SubElement(dataNode, 'part', {'name': animDesc[i]['Name']})
        idx = animDesc[i]['Subname'].find('_')
        if len(partNode.findall("./category")) == 0: 
            if idx > 0:
                catNode = etree.SubElement(partNode, 'category', {'name': animDesc[i]['Subname'][0:idx]}) # Category is a string before _ of subname, if any
            else:
                catNode = etree.SubElement(partNode, 'category', {'name': "misc"}) # Now we only assume misc if _ is not present or is the first character
        aniNode = etree.SubElement(catNode, 'animation', {'subname': animDesc[i]['Subname']})

        metaConNode = etree.SubElement(metadataNode, 'connection', {'name': animDesc[i]['Name']})
        metaAniNode = etree.SubElement(metaConNode, 'animation', {'subname': animDesc[i]['Subname']})
        etree.SubElement(metaAniNode, 'frames', {'start': str(0), 'end': str(int(animDesc[i]['Duration'])*30)}) #TODO Improve this -- can't just assume duration is same as end!

        locNode = etree.SubElement(aniNode, 'location')
        XA = etree.SubElement(locNode, 'X')
        YA = etree.SubElement(locNode, 'Y')
        ZA = etree.SubElement(locNode, 'Z')
        for iia in range(animDesc[i]['NumPosKeys']):
            kfDataA = unpack('fff4s4s4sffffffffffffffffffIffffffI', reader.read(128))
            keyframesA = {}
            for iiia in range(len(keyframesListA)):
                keyframesA[keyframesListA[iiia]] = kfDataA[iiia]
            frameLocX = etree.SubElement(XA, 'frame', {'id': str(int(keyframesA['Time']*30)), 'value': str(keyframesA['PositionX']), 'interpolation': InterpolationTypeNameDict[keyframesA['InterpolationTypeX']]})
            handleRightLocX = etree.SubElement(frameLocX, 'handle_right', {'X': str(keyframesA['CPX1x']), 'Y': str(keyframesA['CPX1y'])})
            handleLeftLocX = etree.SubElement(frameLocX, 'handle_left', {'X': str(keyframesA['CPX2x']), 'Y': str(keyframesA['CPX2y'])})
            frameLocY = etree.SubElement(YA, 'frame', {'id': str(int(keyframesA['Time']*30)), 'value': str(keyframesA['PositionY']), 'interpolation': InterpolationTypeNameDict[keyframesA['InterpolationTypeY']]})
            handleRightLocY = etree.SubElement(frameLocY, 'handle_right', {'X': str(keyframesA['CPY1x']), 'Y': str(keyframesA['CPY1y'])})
            handleLeftLocY = etree.SubElement(frameLocY, 'handle_left', {'X': str(keyframesA['CPY2x']), 'Y': str(keyframesA['CPY2y'])})
            frameLocZ = etree.SubElement(ZA, 'frame', {'id': str(int(keyframesA['Time']*30)), 'value': str(keyframesA['PositionZ']), 'interpolation': InterpolationTypeNameDict[keyframesA['InterpolationTypeZ']]})
            handleRightLocZ = etree.SubElement(frameLocZ, 'handle_right', {'X': str(keyframesA['CPZ1x']), 'Y': str(keyframesA['CPZ1y'])})
            handleLeftLocZ = etree.SubElement(frameLocZ, 'handle_left', {'X': str(keyframesA['CPZ2x']), 'Y': str(keyframesA['CPZ2y'])})

        rotNode = etree.SubElement(aniNode, 'rotation_euler')
        XB = etree.SubElement(rotNode, 'X')
        YB = etree.SubElement(rotNode, 'Y')
        ZB = etree.SubElement(rotNode, 'Z')
        for iib in range(animDesc[i]['NumRotKeys']):
            kfDataB = unpack('fff4s4s4sffffffffffffffffffIffffffI', reader.read(128))
            keyframesB = {}
            for iiib in range(len(keyframesListB)):
                keyframesB[keyframesListB[iiib]] = kfDataB[iiib]
            frameRotX = etree.SubElement(XB, 'frame', {'id': str(int(keyframesB['Time']*30)), 'value': str(keyframesB['RotationX']), 'interpolation': InterpolationTypeNameDict[keyframesB['InterpolationTypeX']]})
            handleRightRotX = etree.SubElement(frameRotX, 'handle_right', {'X': str(keyframesB['CPX1x']), 'Y': str(keyframesB['CPX1y'])})
            handleLeftRotX = etree.SubElement(frameRotX, 'handle_left', {'X': str(keyframesB['CPX2x']), 'Y': str(keyframesB['CPX2y'])})
            frameRotY = etree.SubElement(YB, 'frame', {'id': str(int(keyframesB['Time']*30)), 'value': str(keyframesB['RotationY']), 'interpolation': InterpolationTypeNameDict[keyframesB['InterpolationTypeY']]})
            handleRightRotY = etree.SubElement(frameRotY, 'handle_right', {'X': str(keyframesB['CPY1x']), 'Y': str(keyframesB['CPY1y'])})
            handleLeftRotY = etree.SubElement(frameRotY, 'handle_left', {'X': str(keyframesB['CPY2x']), 'Y': str(keyframesB['CPY2y'])})
            frameRotZ = etree.SubElement(ZB, 'frame', {'id': str(int(keyframesB['Time']*30)), 'value': str(keyframesB['RotationZ']), 'interpolation': InterpolationTypeNameDict[keyframesB['InterpolationTypeZ']]})
            handleRightRotZ = etree.SubElement(frameRotZ, 'handle_right', {'X': str(keyframesB['CPZ1x']), 'Y': str(keyframesB['CPZ1y'])})
            handleLeftRotZ = etree.SubElement(frameRotZ, 'handle_left', {'X': str(keyframesB['CPZ2x']), 'Y': str(keyframesB['CPZ2y'])})

aniXMLFile = (targetPath + 'target_ani.xml')
os.makedirs(os.path.dirname(aniXMLFile), exist_ok=True)
with open(aniXMLFile, "w") as f:
    f.write(prettify(aniXML))
f.close()
