// 
// Demo input file for parameterised geometries with Gmsh
// Author: Rory Spencer
// Date:  Nov-2023

// Geometry Variables
gaugeHeight = 10E-3;
gaugeWidth = 2.5E-3;
gaugeThickness = 1E-3; 

// Parameterisation
//_*
p0 = 1.5E-3;
p1 = 1E-3;
p2 = 1.2E-3;
//**
lc = 1E-4;
filename = "tens_spline_3d.msh";


// Create some points defining the boundary
// Will have vertical symmetry
Point(1) = {0,-gaugeHeight,0,lc}; //Bottom of centreline on specimen
Point(2) = {p0,-5E-3,0,lc}; // Parameterised point 0
Point(3) = {p1,0,0,lc}; // Parameterised point 1
Point(4) = {p2,5E-3,0,lc}; // Parameterised point 2
Point(5) = {gaugeWidth,gaugeHeight,0,lc}; //Top of gauge side line
Point(6) = {0,gaugeHeight,0,lc}; //Top of gauge centreline
Point(7) = {gaugeWidth,-gaugeHeight,0,lc}; // Bottom Edge of gauge

// Connect things up with some lines
Line(1) = {1,7}; // Bottom Hor Line
Spline(2) = {7,2,3,4,5}; //Vertical up side
Line(3) = {5,6}; // Top Hor Line
Line(4) = {6,1}; // Centreline

Curve Loop(1) = {1,2,3,4};
Plane Surface(1) = {1};

// Top & Bottom
Transfinite Curve{1} = 10;
Transfinite Curve{3} = 10;

// Sides
Transfinite Curve{4} = 50;
Transfinite Curve{2} = 50;

Transfinite Surface{1};

Recombine Surface{:};

Extrude {0, 0, gaugeThickness} { Surface{:}; Layers{3}; Recombine;}

Mesh 3;

Physical Volume("Specimen",1) = {1};


delta = 0.005E-3;
topsurf() = Surface In BoundingBox 
{0-delta,gaugeHeight-delta,0-delta,
gaugeWidth+delta, gaugeHeight+delta,gaugeThickness+delta};

btmsurf() = Surface In BoundingBox 
{0-delta,-gaugeHeight-delta,0-delta,
gaugeWidth+delta,-gaugeHeight+delta,gaugeThickness+delta};

bcksurf() = Surface In BoundingBox 
{-1,-gaugeHeight-delta,0-delta,
1,gaugeHeight+delta,0+delta};

midsurf() = Surface In BoundingBox 
{0-delta,-gaugeHeight-delta,0-delta,
0+delta,gaugeHeight+delta,gaugeThickness+delta};

// We now can use these variables to assign physical surfaces.
// Again note the tags! Physical tags start at 1 and tags are shared between all physical entities.
// Physical Volume("Vol",1) and Physical Surface("Sur",1) will cause errors!
// The names given to these surfaces will be used as the BC names in MOOSE.

Physical Surface("Top-BC",2) = {topsurf()};
Physical Surface("Btm-BC",3) = {btmsurf()};
Physical Surface("Bck-BC",4) = {bcksurf()};
Physical Surface("Mid-BC",5) = {midsurf()};


Save Str(filename);
Exit;
