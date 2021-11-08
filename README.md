# X4_gen_regions
This is a WIP Blender addon that handles Blender animation exporting to X4 binary ani files. It also can generate randomized regions.

ANIMATION: 

Most users should follow these steps:

(0) If adding animation(s) to a component with existing animations, please use this addon to import the animations for now: https://github.com/Cgettys/X4Converter/blob/master/X4ConverterBlenderAddon.zip (there's a checkbox for import animations).

(1) Create an animation in Blender.

(2) Select the objects whose animations you want in the generated ANI file (the objects should have the same name as the component parts you want animated) (if step 0 applies to you, make sure you select objects with imported animations you want!).

(3a) While in Layout tab, click on the Generator panel/tab (press N if it's not visible, usually on the right).

(3b) Enter your desired target folder in the Generator panel.

(4) Click the last 2 buttons in order (first AniXML, then Ani) (naturally I can combine these buttons, but it's useful having them separate right now). 

The output anixml and ani files should appear in your target folder. You just need to place and rename them (typically like CLUSTER_100_DATA.ani or whatever the data folder is for the component).

The other buttons are for creating randomized regions from a sectors.xml file (unrelated, just currently part of this addon) and generating orbits for things like planets. Let's get animating!



REGIONS:

Region generation is currently based on a sectors.xml file the user selects, and optionally based on an input file briefly listing what types of fields and resources are desired.



FUTURE PLANS:

Future animation plans may include more animation types than location and rotation, such as scale (assuming these will work) and possibly more automated generation of common antimations, like rotations.

Future region plans may include porting over more of what I created in XSLT, such as field rings around planets, accretion discs, debris fields, etc.
