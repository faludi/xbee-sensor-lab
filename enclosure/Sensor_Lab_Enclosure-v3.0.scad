//-----------------------------------------------------------------------
// Yet Another Parameterized Projectbox generator
//
//  This is a box for Digi XBee Sensor Lab
//  by Robert Faludi rob@faludi.com
//
//-----------------------------------------------------------------------



include <../YAPP_Box/library/YAPPgenerator_v3.scad>

// Note: length/lengte refers to X axis, 
//       width/breedte to Y, 
//       height/hoogte to Z

/*
            padding-back>|<---- pcb length ---->|<padding-front
                                 RIGHT
                   0    X-ax ---> 
               +----------------------------------------+   ---
               |                                        |    ^
               |                                        |   padding-right 
             ^ |                                        |    v
             | |    -5,y +----------------------+       |   ---              
        B    Y |         | 0,y              x,y |       |     ^              F
        A    - |         |                      |       |     |              R
        C    a |         |                      |       |     | pcb width    O
        K    x |         |                      |       |     |              N
               |         | 0,0              x,0 |       |     v              T
               |   -5,0  +----------------------+       |   ---
               |                                        |    padding-left
             0 +----------------------------------------+   ---
               0    X-ax --->
                                 LEFT
*/


//-- which part(s) do you want to print?
printBaseShell        = false;
printLidShell         = true;
printSwitchExtenders  = false;

//-- pcb dimensions -- very important!!!
pcbLength           = 64;
pcbWidth            = 46;
pcbThickness        = 1.3;
                            
//-- padding between pcb and inside wall
paddingFront        = 5;
paddingBack         = 32;
paddingRight        = 59;
paddingLeft         = 47;

//-- Edit these parameters for your own box dimensions
wallThickness       = 2.0;
basePlaneThickness  = 1.0;
lidPlaneThickness   = 1.0;

//-- Total height of box = basePlaneThickness + lidPlaneThickness 
//--                     + baseWallHeight + lidWallHeight
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
baseWallHeight      = 4;
lidWallHeight       = 17;

//-- ridge where base and lid off box can overlap
//-- Make sure this isn't less than lidWallHeight
ridgeHeight         = 3.6;
ridgeSlack          = 0.26;
roundRadius         = 4.0;

//-- How much the PCB needs to be raised from the base
//-- to leave room for solderings and whatnot
standoffHeight      = 8;  //-- only used for showPCB
standoffPinDiameter = 3;
standoffHoleSlack   = 0.4;
standoffDiameter    = 6;


//-- D E B U G -----------------//-> Default ---------
showSideBySide      = true;     //-> true
onLidGap            = 0;
shiftLid            = 1;
hideLidWalls        = false;    //-> false
hideBaseWalls       = false;    //-> false
colorLid            = "silver";
colorBase           = "lightgray";
showOrientation     = true;
showPCB             = false;
showSwitches        = false;
showPCBmarkers      = false;
showShellZero       = true;
showCenterMarkers   = false;
inspectX            = 0;        //-> 0=none (>0 from front, <0 from back)
inspectY            = 0;        //-> 0=none (>0 from left, <0 from right)
inspectLightTubes   = 0;        //-> { -1 | 0 | 1 }
inspectButtons      = 0;        //-> { -1 | 0 | 1 }
//-- D E B U G ---------------------------------------


//-- pcb_standoffs  -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = standoffHeight
// (3) = filletRadius (0 = auto size)
// (n) = { yappBoth | yappLidOnly | yappBaseOnly }
// (n) = { yappHole, YappPin }
// (n) = { yappAllCorners | yappFrontLeft | yappFrontRight | yappBackLeft | yappBackRight }
// (n) = { yappAddFillet }
pcbStands =    [
//                  [2.8, 2.7, 8, 1, yappBaseOnly, yappFrontLeft]
//                , [2.8, 2.7, 8, 1, yappBaseOnly, yappBackRight]
//                , [2.8, 2.7, 8, 1, yappBaseOnly, yappFrontRight]
//                , [2.8, 2.7, 8, 1, yappBaseOnly, yappBackLeft]
               ];

//-- base plane    -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = width
// (3) = length
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsBase =   [
             //       [30, 0, 10, 24, yappRectangle]
             //     , [pcbLength/2, pcbWidth/2, 12, 4, yappCircle]
             //     , [pcbLength-8, 25, 10, 14, yappRectangle, yappCenter]
                ];

//-- Lid plane    -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = width
// (3) = length
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsLid  =   [
             //     [20, 0, 10, 24, 0, yappRectangle]
             //   , [pcbWidth-6, 40, 12, 4, 20, yappCircle]
             //   , [30, 25, 10, 14, 45, yappRectangle, yappCenter]
                ];

//-- cutoutsGrill    -- origin is pcb[0,0,0]
// (0) = xPos
// (1) = yPos
// (2) = grillWidth
// (3) = grillLength
// (4) = gWidth
// (5) = gSpace
// (6) = gAngle
// (7) = plane { "base" | "led" }
// (7) = {polygon points}}
//
//starShape =>>> [  [0,15],[20,15],[30,0],[40,15],[60,15]
//                 ,[50,30],[60,45], [40,45],[30,60]
//                 ,[20,45], [0,45],[10,30]
//               ]
//cutoutsGrill =[
//[-9, -16, 108, 60, 3, 3, 45, "lid"],
//[10, 8, 30, 44, 1.5, 1.5, 45, "base"]
//              ];

//-- front plane  -- origin is pcb[0,0,0]
// (0) = posy
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }

//Parameters:
// (0) = from Back
// (1) = from Left
// (2) = width
// (3) = length
// (4) = radius
// (5) = depth 0=Auto (plane thickness)
// (6) = angle
// (7) = yappRectangle | yappCircle | yappPolygon | yappRoundedRect | yappCircleWithFlats | yappCircleWithKey
// (8) = Polygon : [] if not used.  - Required if yappPolygon specified -
// (9) = Mask : [] if not used.  - Required if yappUseMask specified -
// (n) = { <yappCoordBox> | yappCoordPCB }
// (n) = { <yappOrigin>, yappCenter }
// (n) = { yappUseMask }

cutoutsFront =  [
//[20, 0, 10, 24, 0, yappRectangle]
                   [4, -2.5, 38, 9, 0, yappRectangle]
               //     [4, -2.5, 38, 9, 0, yappRectangle]
              //    , [30, 7.5, 15, 9, 0, yappRectangle, yappCenter]
              //    , [0, 2, 10, 0, 0, yappCircle]
                ];

//-- back plane  -- origin is pcb[0,0,0]
// (0) = posy
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsBack =   [
              //      [10, 0, 10, 18, 0, yappRectangle]
              //    , [30, 0, 10, 8, 0, yappRectangle, yappCenter]
              //    , [pcbWidth, 0, 8, 0, 0, yappCircle]
                ];

//-- left plane   -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsLeft =   [
              //    , [0, 0, 15, 20, 0, yappRectangle]
              //    , [30, 5, 25, 10, 0, yappRectangle, yappCenter]
              //    , [pcbLength-10, 2, 10, 0, 0, yappCircle]
                ];

//-- right plane   -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsRight =  [
              //      [0, 0, 15, 7, 0, yappRectangle]
              //    , [30, 10, 25, 15, 0, yappRectangle, yappCenter]
              //    , [pcbLength-10, 2, 10, 0, 0, yappCircle]
                ];

//===================================================================
//  *** Connectors ***
//  Standoffs with hole through base and socket in lid for screw type connections.
//-------------------------------------------------------------------
//  Default origin = yappCoordBox: box[0,0,0]
//  
//  Parameters:
//   Required:
//    p(0) = posx
//    p(1) = posy
//    p(2) = pcbStandHeight
//    p(3) = screwDiameter
//    p(4) = screwHeadDiameter (don't forget to add extra for the fillet)
//    p(5) = insertDiameter
//    p(6) = outsideDiameter
//   Optional:
//    p(7) = PCB Gap : Default = -1 : Default for yappCoordPCB=pcbThickness, yappCoordBox=0
//    p(8) = filletRadius : Default = 0/Auto(0 = auto size)
//    n(a) = { <yappAllCorners>, yappFrontLeft | yappFrontRight | yappBackLeft | yappBackRight }
//    n(b) = { <yappCoordBox> | yappCoordPCB |  yappCoordBoxInside }
//    n(c) = { yappNoFillet }
//-------------------------------------------------------------------
connectors   =
[
     [2.8, 2.7, 0, 1.85, 1.85, 2.5, 4, 6, 14, yappAllCorners]
//   , [2.8, 2.7, 0, 2.9, 4, 4, 5, 6, 14, yappBackRight]
//   , [2.8, 2.7, 0, 2.9, 4, 4, 5, 6, 14, yappFrontRight]
//   , [2.8, 2.7, 0, 2.9, 4, 4, 5, 6, 14, yappBackLeft]
//   ,[9, 15, 10, 2.5, 6 + 1.25, 4.0, 9, yappNoFillet, yappFrontLeft]
//   ,[34, 15, 10, 2.5, 6+ 1.25, 4.0, 9, yappFrontRight]
//   ,[34, 15, 10, 2.5, 6+ 1.25, 4.0, 9, 0, yappFrontLeft]
];

//-- base mounts -- origen = box[x0,y0]
// (0) = posx | posy
// (1) = screwDiameter
// (2) = width
// (3) = height
// (n) = yappLeft / yappRight / yappFront / yappBack (one or more)
// (n) = { yappCenter }
// (n) = { yappAddFillet }
baseMounts   =  [
              //      [-5, 3.3, 10, 3, yappLeft, yappRight, yappCenter]
              //    , [40, 3, 8, 3, yappBack, yappFront]
              //    , [4, 3, 34, 3, yappFront]
              //    , [25, 3, 3, 3, yappBack]
                ];

//-- snap Joins -- origen = box[x0,y0]
// (0) = posx | posy
// (1) = width
// (2..5) = yappLeft / yappRight / yappFront / yappBack (one or more)
// (n) = { yappSymmetric }
snapJoins   =   [
                  [(shellWidth/2), 1, yappBack, yappFront]
                , [(shellLength/2), 1, yappLeft, yappRight]

              //    [2,               5, yappLeft, yappRight, yappSymmetric]
              //    [5,              10, yappLeft]
              //  , [shellLength-2,  10, yappLeft]
              //  , [20,             10, yappFront, yappBack]
              //  , [2.5,             5, yappBack,  yappFront, yappSymmetric]
                ];
               
//-- lightTubes  -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = tubeLength
// (3) = tubeWidth
// (4) = tubeWall
// (5) = abovePcb
// (6) = filletRadius (0 = auto size)
// (n) = througLid {yappThroughLid}
// (n) = tubeType  {yappCircle|yappRectangle}
// (n) = { yappAddFillet }
lightTubes = [
              //--- 0,  1, 2,   3, 4, 5, 6/7
              //    [15, 20, 1.5, 5, 1, 2, yappRectangle]
              // ,  [15, 30, 1.5, 5, 1, 2, yappRectangle, yappThroughLid]
              ];     

//-- pushButtons  -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = capLength
// (3) = capWidth
// (4) = capAboveLid
// (5) = switchHeight
// (6) = switchTrafel
// (7) = poleDiameter
// (n) = buttonType  {yappCircle|yappRectangle}
pushButtons = [
              //-- 0,  1, 2, 3, 4, 5,   6, 7,   8
          //       [15, 30, 8, 8, 0, 1,   1, 3.5, yappCircle]
          //       [15, 10, 8, 6, 2, 3.5, 1, 3.5, yappRectangle]
              ];     
             
//-- origin of labels is box [0,0,0]
// (0) = posx
// (1) = posy/z
// (2) = orientation
// (3) = depth
// (4) = plane {lid | base | left | right | front | back }
// (5) = font
// (6) = size
// (7) = "label text"
labelsPlane =   [
                   //  [25, 18, 90, 0.5, "lid", "Source Sans Pro:style=bold", 8, "Digi XBee Sensor Lab" ]
                ];


//========= MAIN CALL's ===========================================================
  
//===========================================================
module lidHookInside()
{
  //echo("lidHookInside(original) ..");
 
  
} // lidHookInside(dummy)
  
//===========================================================
module lidHookOutside()
{
  //echo("lidHookOutside(original) ..");
  
} // lidHookOutside(dummy)

//===========================================================
module hookBaseInside()
{

// LABEL OUTLINE       
//L_W = 21; // Box Width
//L_L = 123;// Box Length
//L_H = 0.2; // Box Height
//
//L_CORNER_RADIUS = 3; // Radius of corners
//L_WALL_THICKNESS = 0.3;// Wall Thickness
//
//translate([7.5,25.5,0])
//linear_extrude( L_H )
//    difference(){
//        offset(r=L_CORNER_RADIUS) 
//            square( [L_W, L_L]);
//        
//        offset( r= L_CORNER_RADIUS - L_WALL_THICKNESS )
//            square( [L_W, L_L] );
//    }
    
// BATTERY ENCLOSURE
B_W = 47.5; // Box Width
B_L = 65;// Box Length
B_H = 5.75; // Box Height

B_CORNER_RADIUS = 3; // Radius of corners
B_WALL_THICKNESS = 1.3;// Wall Thickness

translate([40.2,28,0])
linear_extrude( B_H )
    difference(){
        offset(r=B_CORNER_RADIUS) 
            square( [B_W, B_L]);
        
        offset( r= B_CORNER_RADIUS - B_WALL_THICKNESS )
            square( [B_W, B_L] );
    }

// SENSOR SHELF
S_W = 60.5; // Box Width
S_L = 47;// Box Length
S_H = .8; // Box Height

S_CORNER_RADIUS = 3; // Radius of corners
S_WALL_THICKNESS = 0.4;// Wall Thickness

translate([36,101,0])
linear_extrude( S_H )
   difference(){
        offset(r=S_CORNER_RADIUS) 
            square( [S_W, S_L]);
        
    }

  
} // hookBaseInside(dummy)

//===========================================================
module hookBaseOutside()
{
  //echo("baseHookOutside(original) ..");
  
} // hookBaseOutside(dummy)




//---- This is where the magic happens ----
YAPPgenerate();
