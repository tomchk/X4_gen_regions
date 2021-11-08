# X4_gen_regions
This is a WIP Blender addon that handles Blender animation exporting to X4 binary ani files. It also can generate randomized regions.

ANIMATION: 

Most users would follow these steps:

(1) create an animation in Blender; 

(2) select the objects whose animations you want in the generated ANI file (the objects should have the same name as the copmonent parts you want animated); 

(3a) while in Layout tab click on the Generator panel/tab (press N if it's not visible, usually on the right);

(3b) enter your desired target folder in the Generator panel; and 

(4) click the last 2 buttons in order (naturally I can combine these buttons, but it's useful having them separate right now). 

The output anixml and ani files should appear in your target folder. You just need to place and rename them (typically like CLUSTER_100_DATA.ani or whatever the data folder is for the component).

The other buttons are for creating randomized regions from a sectors.xml file (unrelated, just currently part of this addon) and generating orbits for things like planets. Let's get animating!



REGIONS:

Region generation is currently based on a sectors.xml file the user selects, and optionally based on an input file briefly listing what types of fields and resources are desired.



FUTURE PLANS:

Future animation plans may include more animation types than location and rotation, such as scale (assuming these will work) and possibly more automated generation of common antimations, like rotations.

Future region plans may include porting over more of what I created in XSLT, such as field rings around planets, accretion discs, debris fields, etc.
