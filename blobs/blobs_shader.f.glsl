#version 130

// Perlin reference implementation based on the code at
// http://mrl.nyu.edu/~perlin/noise/

#define p_range 256.0

uniform int p[512];               // permutation 256
uniform float x          = -5.54; // diff 0.1
uniform float y          = -5.54; // diff 0.1
uniform float zmax       = 1.0;   // diff 0.01
uniform float zmin       = 0.0;   // diff 0.01
uniform int levels       = 5; 
uniform float zoom       = 0.0065;// diff 0.0005
uniform int octives      = 9;
uniform float freq       = 0.73;  // diff 0.01
uniform float threshold  = 0.75;  // diff 0.01 

float getSumFreq(float x, float y, float z);
float getHash(float x, float y, float z); 
float fade(float t);
float lerp(float t, float a, float b);
float grad(int hsh, float x, float y, float z);

void main() {


  float fragX = x + gl_FragCoord[0] * zoom;
  float fragY = y + gl_FragCoord[1] * zoom;

  float sumFreq = 0.0;
  float zdiff = 1.0;
  if (levels > 0) zdiff = 1.0 / levels;
  float z = zmax + zdiff;

  do {
    z -= zdiff;
    sumFreq = (getSumFreq(fragX, fragY, z) * (0.5 * zmax)) + (zmin + (0.5 * zmax));
  } while (sumFreq < (threshold * z) && z > zmin);

  gl_FragColor = vec4(z, 0.0, 1.0, 1.0);
  
}

float getSumFreq(float x, float y, float z) {
  float totalHash = 0;
  for (int oct = 0; oct < octives; oct++) {
    totalHash += getHash(x * float(1 << oct), y * float(1 << oct), z  * float(1 << oct)) * pow(freq, float(oct + 1));
  }
  return totalHash;
}

float getHash(float x, float y, float z) {
  int X    = int(floor(x)) & 255;             // FIND UNIT CUBE THAT
  int Y    = int(floor(y)) & 255;             // CONTAINS POINT.
  int Z    = int(floor(z)) & 255;
  x       -= floor(x);                        // FIND RELATIVE X,Y,Z
  y       -= floor(y);                        // OF POINT IN CUBE.
  z       -= floor(z);
  float u  = fade(x);                         // COMPUTE FADE CURVES 
  float v  = fade(y);                         // FOR EACH OF X,Y,Z.
  float w  = fade(z); 
  int A    = p[X  ]+Y;                        // HASH COORDINATES OF
  int AA   = p[A  ]+Z;                        // THE 8 CUBE CORNERS,
  int AB   = p[A+1]+Z;
  int B    = p[X+1]+Y;
  int BA   = p[B]  +Z;
  int BB   = p[B+1]+Z;

  return lerp(w, lerp(v, lerp(u, grad(p[AA  ], x    , y    , z     ),   // AND ADD
                                 grad(p[BA  ], x-1.0, y    , z     )),  // BLENDED
                         lerp(u, grad(p[AB  ], x    , y-1.0, z     ),   // RESULTS
                                 grad(p[BB  ], x-1.0, y-1.0, z     ))), // FROM  8
                 lerp(v, lerp(u, grad(p[AA+1], x    , y    , z-1.0 ),   // CORNERS
                                 grad(p[BA+1], x-1.0, y    , z-1.0 )),  // OF CUBE
                         lerp(u, grad(p[AB+1], x    , y-1.0, z-1.0 ),
                                 grad(p[BB+1], x-1.0, y-1.0, z-1.0 ))));
}

float fade(float t) {
  return t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
}

float lerp(float t, float a, float b) {
  return a + t * (b - a);
}

float grad(int hsh, float x, float y, float z) {
  int   h = hsh & 15;                       // CONVERT LO 4 BITS OF HASH CODE
  float u = (h < 8) ? x : y;                // INTO 12 GRADIENT DIRECTIONS.
  float v = (h < 4) ? y : (h == 12 || h == 14) ? x : z;
  return (((h & 1) == 0) ? u : -u) + (((h & 2) == 0) ? v : -v);
}