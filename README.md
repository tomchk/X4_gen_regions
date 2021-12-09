# X4_gen_regions
This is a WIP Blender addon that handles Blender animation exporting to X4 binary ani files. It also can generate randomized regions.

ANIMATION: 

Most users should follow these steps:

(0) If adding animation(s) to a component with existing animations, please use this addon to import the animations for now: https://github.com/Cgettys/X4Converter/blob/master/X4ConverterBlenderAddon.zip (there's a checkbox for import animations).

(1) Create an animation in Blender.

(2) Select the objects whose animations you want in the generated ANI file (the objects should have the same name as the component parts you want animated) (if step 0 applies to you, make sure you select objects with imported animations you want!).

(3a) While in Layout tab, click on the Generator panel/tab (press N if it's not visible, usually on the right).

(3b) Enter your desired target folder in the Generator panel.

(3c) Click the "Export to AniXML" button.

(4a) If you are making a simple loop animation, like a looping rotation or orbit, just click the "AniXML to Ani" button and proceed to step 5. HOWEVER, for complex (e.g., SHIP) animations that are broken into different activiation steps, like dockingbay_closing and dockingbay_opening, go to 4b instead.

(4b) Follow the example AniXML that Cgetty's above addon generates when it imports the ship. You will need to do the following:
(i) Replace the name in ```<category name="misc">``` with the part of the activation before the _, so in this example "dockingbay". 
(ii) Separate the ```<animation subname="loop">``` into the different activation steps, following the example mentioned. 
(iii) SAVE and BACKUP your edited AniXML.
(iv) THEN click the "AniXML to Ani" button.


(5) The output anixml and ani files should appear in your target folder. You just need to place and rename them (typically like CLUSTER_100_DATA.ani or whatever the data folder is for the component).

(6) You should follow the vanilla pattern for adding the animations to your component XML--the information for that is in the metadata node of the anixml file. I have not tested what exactly can be omitted, but I suspect at least that you need to add "animation" to the "tag".

The other buttons are for creating randomized regions from a sectors.xml file (unrelated, just currently part of this addon) and generating orbits for things like planets. Let's get animating!



REGIONS:

Region generation is currently based on a sectors.xml file the user selects, and optionally based on an input file gen_regions_input.xml in the extension root folder, which briefly lists sector macros you want to customize (e.g., no region, non-random region, size of region, and types of fields and resources).

Steps:
(0) OPTIONAL: Provide your gen_regions_input.xml in the extension root folder, based on the sample in gen_regions.py.
(1) Select any mesh in Blender.
(2) While in Layout tab, click on the Generator panel/tab (press N if it's not visible, usually on the right).
(3a) Enter your desired sectors.xml file in the Generator panel.
(3b) Enter your desired target folder in the Generator panel.
(4) Click "Generate Regions" button.



FUTURE PLANS:

Future animation plans may include more animation types than location and rotation, such as scale (assuming these will work) and possibly more automated generation of common animations, like rotations.

Future region plans may include porting over more of what I created in XSLT, such as field rings around planets, accretion discs, debris fields, etc.
