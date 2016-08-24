#version 130

// Perlin reference implementation based on the code at
// http://mrl.nyu.edu/~perlin/noise/

#define pi 3.1415926535897932384626433832795
#define perm_size 512

uniform int perm[perm_size];
uniform float x;
uniform float y;
uniform float z;
uniform float zoom;
uniform int octives;
uniform float freq;
uniform int tile;
uniform bool bound;

float fBm(float x, float y, float z, int per, int octs);
float noise(float x, float y, float z, int per);
float surflet(float x, float y, float z, float gridX, float gridY, float gridZ, int per);

void main() {

  if (bound) {
    // draw bounds
    if (gl_FragCoord[0] * zoom + x < 0.0 ||
        gl_FragCoord[1] * zoom + y < 0.0 ||
        gl_FragCoord[0] * zoom + x > tile ||
        gl_FragCoord[1] * zoom + y > tile )
    {
      gl_FragColor = vec4(0.0, 0.75, 0.0, 1.0);
      return;
    }
  }

  // getHash is not normalised to 0.0 <-> 1.0
  // it's really somewhere between -1.0 and +1.0
  float fb = fBm(
      x + gl_FragCoord[0] * zoom, 
      y + gl_FragCoord[1] * zoom, 
      z,
      tile,
      octives
    ) * 0.5 + 0.5;

  gl_FragColor = vec4(fb, fb, fb, 1.0);
}

float fBm(float x, float y, float z, int per, int octs) {
  float val = 0;
  for (int oct = 0; oct < octs; oct++) {
    val += noise(
      x * float(1 << oct), 
      y * float(1 << oct), 
      z * float(1 << oct), 
      per * (1 << oct)
    ) * pow(0.5, float(oct));
  }
  return val;
}

float noise(float x, float y, float z, int per) {
  float intX = floor(x);
  float intY = floor(y);
  float intZ = floor(z); // Would this better be floor?
  return (
    surflet(x, y, z, intX + 0.0, intY + 0.0, intZ + 0.0, per) +
    surflet(x, y, z, intX + 1.0, intY + 0.0, intZ + 0.0, per) +
    surflet(x, y, z, intX + 0.0, intY + 1.0, intZ + 0.0, per) +
    surflet(x, y, z, intX + 1.0, intY + 1.0, intZ + 0.0, per) +
    surflet(x, y, z, intX + 0.0, intY + 0.0, intZ + 1.0, per) +
    surflet(x, y, z, intX + 1.0, intY + 0.0, intZ + 1.0, per) +
    surflet(x, y, z, intX + 0.0, intY + 1.0, intZ + 1.0, per) +
    surflet(x, y, z, intX + 1.0, intY + 1.0, intZ + 1.0, per) 
  );
}

float surflet(float x, float y, float z, float gridX, float gridY, float gridZ, int per) {
  float distX = abs(x - gridX);
  float distY = abs(y - gridY);
  float distZ = abs(z - gridZ);
  float polyX = 1.0 - 6.0 * pow(distX, 5.0) + 15.0 * pow(distX, 4.0) - 10.0 * pow(distX, 3.0);
  float polyY = 1.0 - 6.0 * pow(distY, 5.0) + 15.0 * pow(distY, 4.0) - 10.0 * pow(distY, 3.0);
  float polyZ = 1.0 - 6.0 * pow(distZ, 5.0) + 15.0 * pow(distZ, 4.0) - 10.0 * pow(distZ, 3.0);
  float hashd = float(perm[perm[perm[int(gridX) % per] + int(gridY) % per] + int(gridZ) % per]);
  float grad  = (x - gridX) * (cos(hashd * 2.0 * pi / 256.0)) + 
                (y - gridY) * (sin(hashd * 2.0 * pi / 256.0));
  return polyX * polyY * polyZ * grad;
}



// TODO: clearly many could be replaced by vectors
//       certainly surflet should be taking 2 vectors
//       it might be possible to pass dirs in as vectors (or some other pre-calc)