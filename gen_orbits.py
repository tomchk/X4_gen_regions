# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


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
        
        base_path = r'D:\X4_out\X4_gen_regions\test' #TODO re.sub(r'\.xml$', '', source)

        self.AddOrbitAnim(1E7,108000,60,0,0)
        # self.write_animations(base_path)

        def prettify(elem):
            """Return a pretty-printed XML string for the Element.
            """
            rough_string = etree.tostring(elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")


        aniXML = etree.Element('root')
        dataNode = etree.SubElement(aniXML, 'data')
        
        for obj in bpy.data.objects:
            if obj.name.startswith("part"): #TODO
                frame_start, frame_end = map(int, obj.animation_data.action.frame_range)
                fcurves = obj.animation_data.action.fcurves
                partNode = etree.SubElement(dataNode, 'part', {'name': obj.name})
                catNode = etree.SubElement(partNode, 'category', {'name': "misc"})
                aniNode = etree.SubElement(catNode, 'animation', {'subname': "loop"})
# FC has 6 curves?? locationX,Y,Z show up twice?
                locNode = etree.SubElement(aniNode, 'location')
                rotEulerNode = etree.SubElement(aniNode, 'rotation_euler')
                metadataNode = etree.SubElement(aniXML, 'metadata')
                conNode = etree.SubElement(metadataNode, 'connection', {'name': obj.name})
                aniMetaNode = etree.SubElement(conNode, 'animation', {'subname': "loop"})
                etree.SubElement(aniMetaNode, 'frames', {'start': "0", 'end': "108000"})
                for xyz in range(len(fcurves)):
                    if fcurves[xyz].data_path == 'location':
                        if xyz == 0:
                            X = etree.SubElement(locNode, 'X')
                            for p in fcurves[0].keyframe_points:
                                frameNode = etree.SubElement(X, 'frame', {'id': str(p.co[0]), 'value': str(p.co[1]), 'interpolation': p.interpolation.replace('CONSTANT','STEP')}) #fc[0].evaluate[frame]
                                etree.SubElement(frameNode, 'handle_right', {'X': str(p.handle_right[0]), 'Y': str(p.handle_right[1])})
                                etree.SubElement(frameNode, 'handle_left', {'X': str(p.handle_left[0]), 'Y': str(p.handle_left[1])})

                        if xyz == 1:
                            Y = etree.SubElement(locNode, 'Y')
                            for p in fcurves[1].keyframe_points:
                                frameNode = etree.SubElement(Y, 'frame', {'id': str(p.co[0]), 'value': str(p.co[1]), 'interpolation': p.interpolation.replace('CONSTANT','STEP')}) #fc[0].evaluate[frame]
                                etree.SubElement(frameNode, 'handle_right', {'X': str(p.handle_right[0]), 'Y': str(p.handle_right[1])})
                                etree.SubElement(frameNode, 'handle_left', {'X': str(p.handle_left[0]), 'Y': str(p.handle_left[1])})
                        if xyz == 2:
                            Z = etree.SubElement(locNode, 'Z')
                            for p in fcurves[2].keyframe_points:
                                frameNode = etree.SubElement(Z, 'frame', {'id': str(p.co[0]), 'value': str(p.co[1]), 'interpolation': p.interpolation.replace('CONSTANT','STEP')}) #fc[0].evaluate[frame]
                                etree.SubElement(frameNode, 'handle_right', {'X': str(p.handle_right[0]), 'Y': str(p.handle_right[1])})
                                etree.SubElement(frameNode, 'handle_left', {'X': str(p.handle_left[0]), 'Y': str(p.handle_left[1])})

                    print("%s[%i]" % (fcurves[xyz].data_path, fcurves[xyz].array_index)) # data_path is location, rotation_euler, etc.; array_index is x=0, y=1, z=2

                    # print("    Keyframe Points (x):")
                    # for p in fc.keyframe_points:
                    #     frameNode = etree.SubElement(X, 'frame', {'id': str(p), 'value': str(p.co.x), 'interpolation': "BEZIER"}) #fc[0].evaluate[frame]
                    #     print("    %f" % p.co.x)

                    # print("    Keyframe Points (y):")
                    # for p in fc.keyframe_points:
                    #     frameNode = etree.SubElement(Y, 'frame', {'id': str(p), 'value': str(p.co.y), 'interpolation': "BEZIER"}) #fc[0].evaluate[frame]
                    #     print("    %f" % p.co.y)
                
    

            
        # for xx in range(0,5):
            # frameNode = etree.SubElement(X, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][0]), 'interpolation': "BEZIER"})
            # etree.SubElement(frameNode, 'handle_right', {'X': str(handleRight[xx+1][0]), 'Y': str(handleRight[xx+1][0])}) #str(handleRight[xx][1])
            # etree.SubElement(frameNode, 'handle_left', {'X': str(handleLeft[xx+1][0]), 'Y': str(handleLeft[xx+1][0])}) #str(handleLeft[xx][1])
        # for xx in range(0,5):
            # frameNode = etree.SubElement(Y, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][1]), 'interpolation': "BEZIER"})
            # frameNode = etree.SubElement(Y, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][1]), 'interpolation': "BEZIER"})
            # etree.SubElement(frameNode, 'handle_right', {'X': "0", 'Y': "0"}) #str(handleRight[xx][1])
            # etree.SubElement(frameNode, 'handle_left', {'X': "0", 'Y': "0"}) #str(handleLeft[xx][1])
        # for xx in range(0,5):
            # frameNode = etree.SubElement(Z, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][2]), 'interpolation': "BEZIER"})
            # frameNode = etree.SubElement(Z, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][2]), 'interpolation': "BEZIER"})
            # etree.SubElement(frameNode, 'handle_right', {'X': str(handleRight[xx+1][2]), 'Y': "0"}) #str(handleRight[xx][1])
            # etree.SubElement(frameNode, 'handle_left', {'X': str(handleLeft[xx+1][2]), 'Y': "0"}) #str(handleLeft[xx][1])

        
        targetPath = r'D:/X4_out/X4_gen_regions/' # TODO Testing ONLY
        aniXMLFile = (targetPath + 'testout.anixml')
        os.makedirs(os.path.dirname(aniXMLFile), exist_ok=True)
        with open(aniXMLFile, "w") as f:
            f.write(prettify(aniXML))
        f.close()

        return {'FINISHED'}

    # START Blender Addons
    def randnum(low=0.0, high=1.0, seed=0):
        """
        randnum( low=0.0, high=1.0, seed=0 )

        Create random number
        Parameters:
            low - lower range
                (type=float)
            high - higher range
                (type=float)
            seed - the random seed number, if seed == 0, the current time will be used instead
                (type=int)
        Returns:
            a random number
                (type=float)
        """

        Noise.seed_set(seed)
        rnum = Noise.random()
        rnum = rnum * (high - low)
        rnum = rnum + low
        return rnum
    # END Blender Addons

    # START ORBIT ANIMATION GENERATION
    def AddOrbitAnim(self,radius=1E7,frames=108000,numKeyframes=4,rotationCenterX=0,rotationCenterY=0):
        for obj in bpy.data.objects:
            if obj.name.startswith("part"): #TODO
                angle = radians(0)
                omega = radians(360)/numKeyframes

                obj.location.x = rotationCenterX + radius * cos(angle) # Starting position x
                obj.location.y = rotationCenterY - radius * sin(angle) # Starting position y

                i = 0
                while angle <= radians(360):
                    angle = angle + omega
                    obj.location.x = obj.location.x + radius * omega * cos(angle + pi / 2) # New x
                    obj.location.y = obj.location.y - radius * omega * sin(angle + pi / 2) # New y
                    obj.keyframe_insert(data_path="location",frame=i)
                    i += frames/numKeyframes
                

    # START Converter Addon
    def write_animations(self,base_path):
        anixml_path = base_path + ".anixml"
        tree = etree.parse(anixml_path)
        root = tree.getroot()
        print("Starting animations")
        for part in root[0]:  # we wrote data first
            part_name = part.attrib['name']
            obj = bpy.data.objects[part_name]
            for cat in part:
                self.handle_category(obj,cat,part_name)

        for part in root[1]:
            print(part.attrib['name'])


    def handle_category(self,obj,cat,part_name):
        offset_frames = 0
        for anim in cat:
            offset_frames = offset_frames + self.handle_category_anim(obj,cat,part_name,anim,offset_frames)


    def handle_category_anim(self,obj,cat,part_name,anim,offset_frames):
        anim_name = anim.attrib['subname']
        action_name = part_name + anim_name
        frame_max = 0
        if  obj.animation_data is None:
            obj.animation_data_create()
        for path in anim:
            path_name = path.tag
            for axis in path:
                possible_max=self.read_frames(axis, obj, path_name,offset_frames)
                frame_max=max(frame_max,possible_max)
        return frame_max

    def read_frames(self,axis_data, obj, path_name,offset_frames):
        # TODO test/assert assumption that all anims start at 0, data wise
        groupnames = {"location": "Location", "rotation_euler": "Rotation", "scale": "Scaling"}
        axis_name = axis_data.tag
        axes = ["X", "Y", "Z"]
        axis_idx = axes.index(axis_name)
        # TODO offset instead?

        frame_min = 0
        frame_max = 0
        starting_data={"location": obj.location, "rotation_euler": obj.rotation_euler, "scale": obj.scale}
        for f in axis_data:
            frame = int(f.attrib["id"])
            fake_frame = float(frame+offset_frames)
            obj.keyframe_insert(data_path=path_name,
                                index=axis_idx,
                                frame=fake_frame,
                                group=groupnames[path_name])
            fc = self.get_fcurve(obj,path_name,axis_idx)
            kf = self.get_keyframe(fc,fake_frame)

            # Ugh converting world handedness bullshit
            if path_name == "location" and axis_name =="X":
                kf.co[1]=starting_data[path_name][axis_idx]-float(f.attrib["value"])
            elif path_name == "rotation_euler" and axis_name == "X":
                kf.co[1]=starting_data[path_name][axis_idx]-float(f.attrib["value"])
            elif path_name == "scale":
                # scale multiplies... I'm an idiot sometimes
                kf.co[1]=starting_data[path_name][axis_idx]*float(f.attrib["value"])
            else:
                kf.co[1]=starting_data[path_name][axis_idx]+float(f.attrib["value"])
            interp = f.attrib["interpolation"]
            if (interp == "STEP"):
                kf.interpolation="CONSTANT"
            else:
                kf.interpolation=interp

            handle_l = f.find("handle_left")
            handle_r = f.find("handle_right")
            kf.handle_left=(float(handle_l.attrib["X"]),float(handle_l.attrib["Y"]))
            kf.handle_right=(float(handle_r.attrib["X"]),float(handle_r.attrib["Y"]))
            frame_min = min(frame_min, frame)
            frame_max = max(frame_max,frame)
        if (frame_min <0):
            print("Something has gone horribly wrong, frame_min < 0")
        return frame_max

    def get_fcurve(self,obj,path,idx):
        for fc in obj.animation_data.action.fcurves:
            if fc.data_path==path and fc.array_index == idx:
                return fc
        return None

    def get_keyframe(self,fc,frame):
        for kf in fc.keyframe_points:
            if (abs(frame-kf.co[0])<0.1):
                return kf
        return None

    def read_metadata(self,ctx,root):
        print("Starting metadata")
        for conn in root[1]:  # then we wrote metadta
            tgt_name = conn.attrib["name"]
            for anim in conn:
                anim_name = anim.attrib["subname"]
                #TODO fixme
                scene = ctx.scenes['Scene']
                timeline_markers = scene.timeline_markers

                start = int(anim.attrib["start"])
                end = int(anim.attrib["end"])
                state_name = anim_name.split("_", 1)[1]
                # TODO reverse lookup by time and concatenate?
                if timeline_markers.get(state_name):
                    continue
                elif start == end:
                    timeline_markers.new(state_name, frame=start)
                    continue
                if not timeline_markers.get(state_name + "Start"):
                    # TODO if is there check if same/warn
                    timeline_markers.new(state_name + "Start", frame=start)
                if not timeline_markers.get(state_name + "End"):
                    # TODO if is there check if same/warn
                    timeline_markers.new(state_name + "End", frame=end)

        print("Done with metadata")
    # END Converter Addons



        # vertArrayTest = [1E7,0,0,0,1E7,0,-1E7,0,0,0,-1E7,0,1E7,-100,0,0,1E7,0,-1E7,0,0]
        # uscale = bpy.context.scene.unit_settings.scale_length
        # obj = bpy.context.active_object
        # spline = obj.data.splines[0]
        # pointsOld = obj.data.splines[0].bezier_points
        # numSegments = len(spline.bezier_points)
        # assert(numSegments >= 2)

        # r = spline.resolution_u
        # if spline.use_cyclic_u:
        #     numSegments += 1

        # points = []
        # # handleRight = []
        # # handleLeft = []
        # pointsOnly = []
        # for i in range(numSegments):
        #     nextIdx = (i + 1) % numSegments

        #     knot1 = spline.bezier_points[i].co
        #     handle1 = spline.bezier_points[i].handle_right
        #     handle2 = spline.bezier_points[nextIdx].handle_left
        #     knot2 = spline.bezier_points[nextIdx].co

        #     _points = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, r)
        #     points.extend(_points)

        # assert('3D' == obj.data.dimensions)
        # pointVecs = []
        # for pointVec in points:
        #     pointVecs.append({
        #         'X': pointVec[0],
        #         'Y': pointVec[1],
        #         'Z': pointVec[2]
        #     })
        # print((pointVecs))

        # for ii in range(0, numSegments):
        # #     handleRight.append(points[ii].handle_right)
        # #     handleLeft.append(points[ii].handle_left)
        #     pointsOnly.append([pointsOld[ii].co.x*uscale, pointsOld[ii].co.z*uscale, pointsOld[ii].co.y*uscale])

        # aniXML = etree.Element('root')
        # dataNode = etree.SubElement(aniXML, 'data')
        # partNode = etree.SubElement(dataNode, 'part', {'name': "part_deimos"})
        # catNode = etree.SubElement(partNode, 'category', {'name': "misc"})
        # aniNode = etree.SubElement(catNode, 'animation', {'subname': "loop"})
        # locNode = etree.SubElement(aniNode, 'location')
        # X = etree.SubElement(locNode, 'X')
        # Y = etree.SubElement(locNode, 'Y')
        # Z = etree.SubElement(locNode, 'Z')
        # #for coord in ['X','Y','Z']:
            
        # for xx in range(0,5):
        #     frameNode = etree.SubElement(X, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][0]), 'interpolation': "BEZIER"})
        #     # frameNode = etree.SubElement(X, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][0]), 'interpolation': "BEZIER"})
        #     # etree.SubElement(frameNode, 'handle_right', {'X': str(handleRight[xx+1][0]), 'Y': str(handleRight[xx+1][0])}) #str(handleRight[xx][1])
        #     # etree.SubElement(frameNode, 'handle_left', {'X': str(handleLeft[xx+1][0]), 'Y': str(handleLeft[xx+1][0])}) #str(handleLeft[xx][1])
        # for xx in range(0,5):
        #     frameNode = etree.SubElement(Y, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][1]), 'interpolation': "BEZIER"})
        #     # frameNode = etree.SubElement(Y, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][1]), 'interpolation': "BEZIER"})
        #     # etree.SubElement(frameNode, 'handle_right', {'X': "0", 'Y': "0"}) #str(handleRight[xx][1])
        #     # etree.SubElement(frameNode, 'handle_left', {'X': "0", 'Y': "0"}) #str(handleLeft[xx][1])
        # for xx in range(0,5):
        #     frameNode = etree.SubElement(Z, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][2]), 'interpolation': "BEZIER"})
        #     # frameNode = etree.SubElement(Z, 'frame', {'id': str(xx*27000), 'value': str(pointsOnly[xx+1][2]), 'interpolation': "BEZIER"})
        #     # etree.SubElement(frameNode, 'handle_right', {'X': str(handleRight[xx+1][2]), 'Y': "0"}) #str(handleRight[xx][1])
        #     # etree.SubElement(frameNode, 'handle_left', {'X': str(handleLeft[xx+1][2]), 'Y': "0"}) #str(handleLeft[xx][1])

        # rotEulerNode = etree.SubElement(aniNode, 'rotation_euler')
        # metadataNode = etree.SubElement(aniXML, 'metadata')
        # conNode = etree.SubElement(metadataNode, 'connection', {'name': "part_deimos"})
        # aniMetaNode = etree.SubElement(conNode, 'animation', {'subname': "loop"})
        # etree.SubElement(aniMetaNode, 'frames', {'start': "0", 'end': "108000"})
        
        # targetPath = r'D:/X4_out/testNow/' # TODO Testing ONLY
        # aniXMLFile = (targetPath + 'sample.anixml')
        # os.makedirs(os.path.dirname(aniXMLFile), exist_ok=True)
        # with open(aniXMLFile, "w") as f:
        #     f.write(prettify(aniXML))
        # f.close()
        # END ORBIT TESTING

        
