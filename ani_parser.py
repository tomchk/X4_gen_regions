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

targetPath = './'
targetFile = (targetPath + 'ani_parsed.txt')
sourceFile = (r'D:\Games\Steam\steamapps\common\X4 Foundations\X4_extracted\extensions\ego_dlc_terran\assets\environments\cluster\CLUSTER_101_DATA.ANI')

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

    for i in range(header['NumAnims']):
        animData = unpack('64s64sIIIIIfII', reader.read(160))
        animDesc = {
            'Name': animData[0].decode().split('\x00')[0],
            'Subname': animData[1].decode().split('\x00')[0],
            'NumPosKeys': animData[2],
            'NumRotKeys': animData[3],
            'NumScaleKeys': animData[4],
            'NumPreScaleKeys': animData[5],
            'NumPostScaleKeys': animData[6],
            'Duration': animData[7]
        }
        print(animDesc)

    for i in range(header['NumAnims']):
        for ii in range(animDesc['NumPosKeys']):
            kfData = unpack('fff4s4s4sffffffffffffffffffI3f3fI', reader.read(128))
            keyframesList = ['PositionX','PositionY','PositionZ','InterpolationTypesX','InterpolationTypesY','InterpolationTypesZ','Time','CPX1x','CPX1y','CPX2x','CPX2y','CPY1x','CPY1y','CPY2x','CPY2y','CPZ1x','CPZ1y','CPZ2x','CPZ2y','Tension','Continuity','Bias','EaseIn','EaseOut','DerivIn','DerivOut','AngleKey']
            keyframes = {}
            for iii in range(len(keyframesList)):
                keyframes[keyframesList[iii]] = kfData[iii]
            print(keyframes)
        for ii in range(animDesc['NumRotKeys']):
            kfData = unpack('fff4s4s4sffffffffffffffffffI3f3fI', reader.read(128))
            keyframesList = ['RotationX','RotationY','RotationZ','InterpolationTypesX','InterpolationTypesY','InterpolationTypesZ','Time','CPX1x','CPX1y','CPX2x','CPX2y','CPY1x','CPY1y','CPY2x','CPY2y','CPZ1x','CPZ1y','CPZ2x','CPZ2y','Tension','Continuity','Bias','EaseIn','EaseOut','DerivIn','DerivOut','AngleKey']
            keyframes = {}
            for iii in range(len(keyframesList)):
                keyframes[keyframesList[iii]] = kfData[iii]
            print(keyframes)

os.makedirs(os.path.dirname(targetFile), exist_ok=True)
with open(targetFile, "w") as f:
    f.write(input)
f.close()
