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
from mathutils import Matrix, Vector
from math import (
    sin, cos, pi
)
import mathutils.noise as Noise


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

import os
import datetime
from pathlib import Path
from xml.dom import minidom


class Gen_Regions_Operator(bpy.types.Operator):
    bl_idname = "view3d.gen_regions"
    bl_label = "Generate Regions"
    bl_description = "Generate Regions for X4"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mytool = context.scene.my_tool
        source = mytool.source
        target = mytool.target
        

        def prettify(elem):
            """Return a pretty-printed XML string for the Element.
            """
            rough_string = etree.tostring(elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")

        # generated_on = str(datetime.datetime.now())

        # targetPath = r'D:/X4_out/testBlend/' # TODO Testing ONLY
        # source = r'C:\Users\Base\Downloads\x4-galaxy-creator-electron-win32-x64\output\swgalaxy\maps\swgalaxy\clusters.xml' # TODO Testing ONLY

        targetPath = target
        sourceTree = etree.parse(source)
        genRIPath = Path(source).parent / "../../gen_regions_input.xml"
        noGenRegionsInput = not(genRIPath.is_file())
        if noGenRegionsInput: # See sample input below
            genRITree = etree.XML('''
<gen_regions_input>
    <sample_cluster_macro noregion="true" randomize="false">
        <fields>
            <volumetricfog></volumetricfog>
            <asteroid_ore_xxl></asteroid_ore_xxl>
            <asteroid_ore_xl></asteroid_ore_xl>
            <fogpattern_v2_macro></fogpattern_v2_macro>
        </fields>
        <resources>
            <ore>high</ore>
            <hydrogen>high</hydrogen>
        </resources>
    </sample_cluster_macro>
</gen_regions_input>
''')
        else:
            genRITree = etree.parse(genRIPath)
        
        thisSeed = 4231
        thisSeedStr = str(thisSeed)
        factorDensity = 1.3

        regionDefXML = etree.Element(
            'regions',
            {
                'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                'xsi:noNamespaceSchemaLocation': "region_definitions.xsd"
            }
        )

        #regionDefXML.append(Comment('Generated XML'))

        i = 0
        #for thisMacro in sourceTree.findall("./macro[@class='cluster']"): 
        for thisMacro in sourceTree.findall("./macro[@class='sector']"):
            thisMacroName = thisMacro.attrib['name']
            randomizeThisRegion = len(genRITree.findall('.//' + thisMacroName + '[@randomize="false"]')) == 0 # Will be false only if the tag includes this attribute as false; default is to randomize
            if len(genRITree.findall('.//' + thisMacroName + '[@noregion="true"]')) == 0:
                region = etree.SubElement(
                    regionDefXML, 'region',
                    {
                        'name': "globalregion_" + thisMacroName.lower(),
                        'density': "1.0",
                        'rotation': "0",
                        'noisescale': "10000",
                        'seed': thisSeedStr,
                        'minnoisevalue': "0",
                        'maxnoisevalue': "1"
                    }
                )

                # Basically, every third item in the for-loop will NOT use a cylinder
                if i % 3 != 0:
                    boundary = etree.SubElement(region, 'boundary', {'class': "cylinder"})
                    boundarySize = etree.SubElement(
                        boundary, 'size', {'r': str(round(randnum(35000,55000,i),0)), 'linear': str(round(randnum(8000,15000,i),0))})

                else:
                    boundary = etree.SubElement(region, 'boundary', {'class': "splinetube"})
                    boundarySize = etree.SubElement(boundary, 'size', {'r': str(round(randnum(12000,22000,i),0))})

                    # START Using Blender Addons
                    context = bpy.context
                    verts = NoiseCurve(2, randnum(2, 7, i), randnum(
                        3, 8, i), 1000000, [1, 1, 1], 1, 0, i)

                    # turn verts into array
                    vertArray = vertsToPoints(verts)
                    # vertArray = [0,0,0,1,0,0,2,0,0]

                    # create object
                    createCurve(context, vertArray)
                    # END Using Blender Addons


                    # START Using Spline Exporter
                    global uscale
                    uscale = bpy.context.scene.unit_settings.scale_length
                    obj = bpy.context.active_object
                    points = obj.data.splines[0].bezier_points
                    pointcount = len(points)

                    for ii in range(0, pointcount):
                        keyvalues = [0, ii+1]
                        tang = (points[ii].handle_right - points[ii].co)
                        tangin = (points[ii].handle_left - points[ii].co).length
                        tangout = (points[ii].handle_right - points[ii].co).length
                        attraction = 1.0
                        if ii == 0 or ii == pointcount-1:
                            attraction = 0.0
                        fieldvalues = [points[ii].co.x*uscale, points[ii].co.z*uscale,
                                    points[ii].co.y*uscale, tang.x, tang.z, tang.y, attraction, tangin, tangout]
                        preNormalizedTangs = Vector((tang.x, tang.z, tang.y))
                        normalizedTangs = preNormalizedTangs.normalized()

                        finalSpline = etree.SubElement(boundary, 'splineposition', {'x': str(fieldvalues[0]), 'y': str(fieldvalues[1]), 'z': str(fieldvalues[2]), 'tx': str(
                            (normalizedTangs[0])), 'ty': str((normalizedTangs[1])), 'tz': str((normalizedTangs[2])), 'inlength': str(tangin), 'outlength': str(tangout)})
                    # END Using Egosoft Spline Exporter


                falloff = etree.SubElement(region, 'falloff')
                lateralFalloff = etree.SubElement(falloff, 'lateral')
                etree.SubElement(lateralFalloff, 'step', {'position': "0.0", 'value': "0.0"})
                etree.SubElement(lateralFalloff, 'step', {'position': "0.05", 'value': "0.1"})
                etree.SubElement(lateralFalloff, 'step', {'position': "0.1", 'value': "0.3"})
                etree.SubElement(lateralFalloff, 'step', {'position': "0.2", 'value': "0.5"})
                etree.SubElement(lateralFalloff, 'step', {'position': "0.5", 'value': "1"})
                etree.SubElement(lateralFalloff, 'step', {'position': "0.8", 'value': "0.5"})
                etree.SubElement(lateralFalloff, 'step', {'position': "0.9", 'value': "0.3"})
                etree.SubElement(lateralFalloff, 'step', {'position': "0.95", 'value': "0.1"})
                etree.SubElement(lateralFalloff, 'step', {'position': "1.0", 'value': "0.0"})
                radialFalloff = etree.SubElement(falloff, 'radial')
                etree.SubElement(radialFalloff, 'step', {'position': "0.0", 'value': "1.0"})
                etree.SubElement(radialFalloff, 'step', {'position': "0.51", 'value': "1.0"})
                etree.SubElement(radialFalloff, 'step', {'position': "0.75", 'value': "0.85"})
                etree.SubElement(radialFalloff, 'step', {'position': "1.0", 'value': "0.0"})

                fields = etree.SubElement(region, 'fields')
                
                fogMediumList = [
                    'fog_asteroidbelt',
                    'fog_asteroidbelt2',
                    'fog_blue',
                    'fog_blue_mist',
                    'fog_bluepink',
                    'fog_blueveins',
                    'fog_brown',
                    'fog_burgundy',
                    'fog_cluster114a',
                    'fog_cluster114b',
                    'fog_cluster_14_basefill',
                    'fog_cluster_14_sector_001',
                    'fog_cluster_33_sector_001',
                    'fog_darkblue',
                    'fog_greenveins',
                    'fog_grey',
                    'fog_grey_emissive',
                    'fog_grey_emissive2',
                    'fog_greybase',
                    'fog_greystructure',
                    'fog_lightbrown',
                    'fog_lightbrown_base',
                    'fog_lightbrown_base_var1',
                    'fog_lightgreen',
                    'fog_orange_directional',
                    'fog_orange_directional_var1',
                    'fog_red',
                    'fog_saturnbelt',
                    'fog_saturnbelt2',
                    'fog_structurefield',
                    'fog_turquoise',
                    'fog_whiteblue',
                    'fog_whiteblue_emissive',
                    'fog_wreckfield',
                    'helium',
                    'hydrogen'
                ]
                fogTextureList = [
                    'assets/textures/environments/fog_maskrnd_03',
                    'assets/textures/environments/fog_maskrnd_06_gui',
                    'assets/textures/environments/fog_maskrnd_07',
                    'assets/textures/environments/fog_patterncloud_01',
                    'assets/textures/environments/fog_patterncloud_02',
                    'assets/textures/environments/fog_patterncloud_03',
                    'assets/textures/environments/fog_patterncloud_04',
                    'assets/textures/environments/fog_patterncloud_06',
                    'assets/textures/environments/fog_patterncloud_07',
                    'assets/textures/environments/fog_patterncloud_08',
                    'assets/textures/environments/fog_smoothclouds_01',
                    'assets/textures/environments/fog_smoothclouds_03',
                    'assets/textures/environments/volumefog/vf_chunky_diff',
                    'assets/textures/environments/volumefog/vf_structured_01_diff'
                ]

                # for element in fogMediumTree.findall(".//medium"): 
                #     fogMediumList.append(element.text)
                # for element in fogTextureTree.findall(".//texture"): 
                #     fogTextureList.append(element.text)

                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/volumetricfog')) > 0: etree.SubElement(fields, 'volumetricfog', {
                    'multiplier': str(round(randnum(0.05,0.2,i),4)), 
                    'medium': fogMediumList[int(randnum(0,len(fogMediumList),i))],
                    'texture': fogTextureList[int(randnum(0,len(fogTextureList),i))], 
                    'lodrule': "nebulafar", 'size': str(round(randnum(15000,45000,i),0)),
                    'sizevariation': "0.4", 'densityfactor': str(round(randnum(0.005,0.2,i),4)), 'rotation': "360", 'rotationvariation': "0.0", 'noisescale': "15000", 
                    'seed': thisSeedStr, 'minnoisevalue': str(round(randnum(0,0.4,i),4)), 'maxnoisevalue': "1.0"})
                
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_ore_xxl')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_ore_xxl",
                        'lodrule': "asteroidxl",
                        'densityfactor': str(round(factorDensity*randnum(0.0005,0.0015,i + 1),4)),
                        'rotation': "0",
                        'rotationvariation': "4",
                        'noisescale': "15000",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.9,0.95,i + 1),4)),
                        'maxnoisevalue': "1"})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_ore_xl')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_ore_xl",
                        'lodrule': "asteroidxl",
                        'densityfactor': str(round(factorDensity*randnum(0.0005,0.0015,i + 2),4)),
                        'rotation': "0",
                        'rotationvariation': "4",
                        'noisescale': "15000",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.7,0.75,i + 2),4)),
                        'maxnoisevalue': str(round(randnum(0.85,0.89,i + 2),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_ore_l')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_ore_l",
                        'densityfactor': str(round(factorDensity*randnum(0.5,1.5,i + 3),2)),
                        'rotation': "0",
                        'rotationvariation': "4",
                        'noisescale': "15000",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.5,0.55,i + 3),4)),
                        'maxnoisevalue': str(round(randnum(0.65,0.69,i + 3),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_ore_m')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_ore_m",
                        'densityfactor': str(round(factorDensity*randnum(1.5,2.5,i + 4),2)),
                        'rotation': "0",
                        'rotationvariation': "8",
                        'noisescale': "15000",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.3,0.35,i + 4),4)),
                        'maxnoisevalue': str(round(randnum(0.45,0.49,i + 4),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_ore_s')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_ore_s",
                        'densityfactor': str(round(factorDensity*randnum(1.5,2.5,i + 5),2)),
                        'rotation': "0",
                        'rotationvariation': "16",
                        'noisescale': "1500",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.1,0.15,i + 5),4)),
                        'maxnoisevalue': str(round(randnum(0.25,0.29,i + 5),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_ore_xs')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_ore_xs",
                        'densityfactor': str(round(factorDensity*randnum(0.1,1.2,i + 6),2)),
                        'rotation': "0",
                        'rotationvariation': "32",
                        'noisescale': "1500",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.0,0.4,i + 6),4)),
                        'maxnoisevalue': str(round(randnum(0.05,0.09,i + 6),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_silicon_s')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_silicon_s",
                        'densityfactor': str(round(factorDensity*randnum(1.5,2.5,i + 7),2)),
                        'rotation': "0",
                        'rotationvariation': "16",
                        'noisescale': "1500",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.1,0.15,i + 5),4)),
                        'maxnoisevalue': str(round(randnum(0.25,0.29,i + 5),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_silicon_xs')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_silicon_xs",
                        'densityfactor': str(round(factorDensity*randnum(0.1,1.2,i + 8),2)),
                        'rotation': "0",
                        'rotationvariation': "32",
                        'noisescale': "1500",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.0,0.4,i + 6),4)),
                        'maxnoisevalue': str(round(randnum(0.05,0.09,i + 6),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_ice_xs')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_ice_xs",
                        'densityfactor': str(round(factorDensity*randnum(0.6,1.0,i + 9),2)),
                        'rotation': "0",
                        'rotationvariation': "16",
                        'noisescale': "5000",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.1,0.15,i + 6),4)),
                        'maxnoisevalue': str(round(randnum(0.25,0.29,i + 6),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/asteroid_nividium_xs')) > 0: etree.SubElement(fields, 'asteroid', {'groupref': "asteroid_nividium_xs",
                        'densityfactor': str(round(factorDensity*randnum(1.5,2.5,i + 10),2)),
                        'rotation': "0",
                        'rotationvariation': "4",
                        'noisescale': "15000",
                        'seed': thisSeedStr,
                        'minnoisevalue': str(round(randnum(0.1,0.15,i + 7),4)),
                        'maxnoisevalue': str(round(randnum(0.25,0.29,i + 7),4))})
                if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/fields/fogpattern_v2_macro')) > 0: etree.SubElement(fields, 'nebula', {'ref': "fogpattern_v2_macro",
                        'localred': "16",
                        'localgreen': "19",
                        'localblue': "22",
                        'localdensity': "0.0",
                        'uniformred': "10",
                        'uniformgreen': "14",
                        'uniformblue': "20",
                        'uniformdensity': "0.3",
                        'backgroundfog': "false",
                        'resources': "hydrogen"})
                resources = etree.SubElement(region, 'resources')
                resourceTypes = ['ore','silicon','ice','nividium','hydrogen','helium','methane'] # TODO add new when ready
                for thisRType in resourceTypes:
                    if randomizeThisRegion or noGenRegionsInput or len(genRITree.findall('.//' + thisMacroName + '/resources/' + thisRType)) > 0: 
                        thisResource = etree.SubElement(resources, 'resource', {'ware':thisRType})
                        if len(genRITree.findall('.//' + thisMacroName + '/resources/' + thisRType)) > 0: thisResource.attrib['yield'] = genRITree.find('.//' + thisMacroName + '/resources/' + thisRType).text
                        else: thisResource.attrib['yield'] = 'low'
                
                i += 1

        regionDefFile = (targetPath + 'libraries/region_definitions.xml')
        os.makedirs(os.path.dirname(regionDefFile), exist_ok=True)
        with open(regionDefFile, "w") as f:
            f.write(prettify(regionDefXML))
        f.close()

        contentXML = etree.Element(
            'content',
            {
                'id': "gen_regions_output",
                'name': "Generated Regions",
                'description': "",
                'author': "metame's Python Generator",
                'date': str(datetime.datetime.now()),
                'version': "1",
                'save': "0"
            }
        )
        etree.SubElement(contentXML, 'dependency', {'id': "ego_dlc_terran", 'version': "100", 'optional': "false"})
        etree.SubElement(contentXML, 'dependency', {'id': "ego_dlc_split", 'version': "100", 'optional': "false"})
        contentFile = (targetPath + 'content.xml')
        os.makedirs(os.path.dirname(contentFile), exist_ok=True)
        with open(contentFile, "w") as f:
            f.write(prettify(contentXML))
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


def vTurbNoise(x, y, z, iScale=0.25, Size=1.0, Depth=6, Hard=False, Basis=0, Seed=0):
    """
    vTurbNoise((x,y,z), iScale=0.25, Size=1.0,
            Depth=6, Hard=0, Basis=0, Seed=0 )

    Create randomised vTurbulence noise

    Parameters:
        xyz - (x,y,z) float values.
            (type=3-float tuple)
        iScale - noise intensity scale
            (type=float)
        Size - noise size
            (type=float)
        Depth - number of noise values added.
            (type=int)
        Hard - noise hardness: True - soft noise; False - hard noise
            (type=int)
        basis - type of noise used for turbulence
            (type=int)
        Seed - the random seed number, if seed == 0, the current time will be used instead
            (type=int)
    Returns:
        the generated turbulence vector.
            (type=3-float list)
    """
    rand = randnum(-100, 100, Seed)
    if Basis == 9:
        Basis = 14
    vec = Vector((x / Size + rand, y / Size + rand, z / Size + rand))
    vTurb = Noise.turbulence_vector(vec, Depth, Hard)
    # mathutils.noise.turbulence_vector(position, octaves, hard, noise_basis='PERLIN_ORIGINAL', amplitude_scale=0.5, frequency_scale=2.0)
    tx = vTurb[0] * iScale
    ty = vTurb[1] * iScale
    tz = vTurb[2] * iScale
    return tx, ty, tz


def NoiseCurve(type=2, number=14, length=8.0, size=10,
            scale=[0.5, 0.5, 0.5], octaves=2, basis=0, seed=0):
    """
    Create noise curve

    Parameters:
        number - number of points
            (type=int)
        length - curve length
            (type=float)
        size - noise size
            (type=float)
        scale - noise intensity scale x,y,z
            (type=list)
        basis - noise basis
            (type=int)
        seed - noise random seed
            (type=int)
        type - noise curve type
            (type=int)
    Returns:
        a list with lists of x,y,z coordinates for curve points, [[x,y,z],[x,y,z],...n]
        (type=list)
    """

    newpoints = []
    step = (length / number)
    i = 0
    if type == 1:
        # noise circle
        while i < number:
            t = i * step
            v = vTurbNoise(t, t, t, 1.0, size, octaves, False, basis, seed)
            x = sin(t * pi) + (v[0] * scale[0])
            y = cos(t * pi) + (v[1] * scale[1])
            z = v[2] * scale[2]
            newpoints.append([x, y, z])
            i += 1
    elif type == 2:
        # noise knot / ball
        while i < number:
            t = i * step
            v = vTurbNoise(t, t, t, 1.0, 1.0, octaves, False, basis, seed)
            x = v[0] * scale[0] * size
            y = v[1] * scale[1] * size
            z = v[2] * scale[2] * size
            newpoints.append([x, y, z])
            i += 1
    else:
        # noise linear
        while i < number:
            t = i * step
            v = vTurbNoise(t, t, t, 1.0, size, octaves, False, basis, seed)
            x = t + v[0] * scale[0]
            y = v[1] * scale[1]
            z = v[2] * scale[2]
            newpoints.append([x, y, z])
            i += 1
    return newpoints


def vertsToPoints(Verts):
    # main vars
    vertArray = []
    for v in Verts:
        vertArray += v
    return vertArray


def createCurve(context, vertArray):
    splineType = 'BEZIER'

    name = 'TestCurve'

    if bpy.context.mode == 'EDIT_CURVE':
        Curve = context.active_object
        newSpline = Curve.data.splines.new(type=splineType)          # spline
    else:
        # create curve
        dataCurve = bpy.data.curves.new(name, type='CURVE')  # curve data block
        newSpline = dataCurve.splines.new(type=splineType)          # spline

        # create object with newCurve
        Curve = object_utils.object_data_add(
            context, dataCurve)  # place in active scene

    # set newSpline Options
    newSpline.use_cyclic_u = False
    newSpline.use_endpoint_u = False
    newSpline.order_u = False

    # set curve Options
    Curve.data.dimensions = '3D'
    Curve.data.use_path = True
    Curve.data.fill_mode = 'FULL'

    for spline in Curve.data.splines:
        for point in spline.bezier_points:
            point.select_control_point = False
            point.select_left_handle = False
            point.select_right_handle = False

    # create spline from vertarray
    newSpline.bezier_points.add(int(len(vertArray) * 0.33))
    newSpline.bezier_points.foreach_set('co', vertArray)
    for point in newSpline.bezier_points:
        # Setting these types to 'FREE' makes an explosion-like noise! 'AUTO' creates smooth curves.
        point.handle_right_type = 'AUTO'
        point.handle_left_type = 'AUTO'
        point.select_control_point = True
        point.select_left_handle = True
        point.select_right_handle = True

    return
# END Blender Addons
