import bpy
from bpy_extras import object_utils
from math import (
    sin, cos, pi, radians, sqrt, pow
)
import mathutils.geometry
from mathutils import Matrix, Vector
import mathutils.noise as Noise

import os
from pathlib import Path
import xml.dom

from . gen_orbits import AddOrbitAnim, GenerateAniXML
from . gen_regions import randnum

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


class Gen_Orbits_In_Cluster_Operator(bpy.types.Operator):
    bl_idname = "view3d.gen_orbits_in_cluster"
    bl_label = "Generate Orbits (Animate Cluster)"
    bl_description = "Generate Orbits for Imported Cluster in X4"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mytool = context.scene.my_tool
        source = mytool.source
        target = mytool.target

        source = r'C:\Games\Steam\steamapps\common\X4 Foundations\extensions\planet_builder\assets\environments\cluster\Cluster_pb.xml' #TODO Just for testing
        sourceTree = xml.dom.minidom.parse(source) #etree.parse(source)
        
        sunCoordinatesList = [dm for dm in sourceTree.getElementsByTagName('position') if 'XU Omni' in dm.parentNode.parentNode.getAttribute('name')]
        planetMaterialList = [dm for dm in sourceTree.getElementsByTagName('material') if 'planet' in dm.getAttribute('ref')]
        # planetPositionList = [dm.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.getElementsByTagName('position') for dm in planetMaterialList]
        # sunCoordinatesList = [elm for elm in sourceTree.findall("./component/layers/layer/lights/omni/offset/position") if 'XU Omni' in elm.find("./.../...").attrib['name']]
        # print(sunCoordinatesList[0].getAttribute('x') + ',' + sunCoordinatesList[0].getAttribute('y') + ',' + sunCoordinatesList[0].getAttribute('z'))
        
        bpy.ops.object.select_all(action='DESELECT')
        
        planetIndex = 0
        for obj in bpy.data.objects:
             if obj.name.find('collision') == -1 and obj.name.find('lod') == -1 and not(obj.name.startswith('Cluster')): #TODO Change this, and adjust axes? if obj.name.startswith("part_asteroids"):
                obj.select_set(True) # Add object to selected group
                for child in obj.children: child.select_set(False)

                planetPartName = planetMaterialList[planetIndex].parentNode.parentNode.parentNode.parentNode.getAttribute('name')
                print(planetPartName)
                planetPosition = planetMaterialList[planetIndex].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.getElementsByTagName('position')[0]
                print(planetPosition.getAttribute('x') + ' ' + planetPosition.getAttribute('z'))

                radiusXML = sqrt(pow(float(planetPosition.getAttribute('x')),2) + pow(float(planetPosition.getAttribute('z')),2)) #TODO Use suncoords?
                thisRadius = radiusXML+randnum(1E7,2E7)*planetIndex
                keyframes = 1200+round(randnum(1200,thisRadius/120000))*planetIndex

                AddOrbitAnim(obj,thisRadius,keyframes,60,0,0) #15*planetIndex,15*planetIndex+360 #TODO Make these not rely on adjustments to radius!
                planetIndex += 1

        GenerateAniXML()

        return {'FINISHED'}

