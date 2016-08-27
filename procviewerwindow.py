from __future__ import print_function
from procviewer import TextureShader
from pyglet.gl import *
from random import Random
import pyglet

class TextureWindow(pyglet.window.Window):

    def __init__(self, shader_path):
        self.w = 512
        self.h = 512

        self.textureShader = TextureShader(shader_path)
        super(TextureWindow, self).__init__(caption = shader_path, width=self.w, height=self.h)

        self.p = []
        permutation = getPermutation()
        for i in range(512):
            self.p.append(permutation[i % len(permutation)])

        self.helpLabels = []
        y = self.height
        for labelText in self.textureShader.getHtmlHelps():
            self.helpLabels.append(pyglet.text.HTMLLabel(
                    "<font face='Courier New' color='white'>{}</font>".format(labelText),
                    x=0, y=y,
                    anchor_x='left', anchor_y='top'))
            y -= 20

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.textureShader.mouseDrag(dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.textureShader.mouseScrollY(scroll_y)

    def on_key_release(self, symbol, modifiers):
        self.textureShader.bindingTrigger(symbol)

    def saveFromShader(self):
        a = (GLubyte * (4 * self.w * self.h))(0)

        glReadPixels(0, 0, self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, a)
        image = pyglet.image.ImageData(self.w, self.h, 'RGBA', a)
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        filePath = scriptPath + "/TESTSAVE_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
        print ("saved to {}".format(filePath))
        image.save(filePath)

    def on_draw(self):
        self.drawGenerated()
        self.drawGUI()
        
    def drawGenerated(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1., 1., 1., -1., 0., 1.)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.textureShader.bind()
        self.textureShader.uniformi('p', *self.p)

        self.textureShader.setUniforms()

        glBegin(GL_QUADS)
        glVertex2i(-1, -1)
        glTexCoord2i(-2, -2)
        glVertex2f(1, -1)
        glTexCoord2i(2, -2)
        glVertex2i(1, 1)
        glTexCoord2i(2, 2)
        glVertex2i(-1, 1)
        glTexCoord2i(-2, 2)
        glEnd()

        self.textureShader.unbind()

    def drawGUI(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, -1, 1)

        for label in self.helpLabels:
            label.draw()

def getPermutation():
    '''
    Although a shuffled array should do the same job, the Array
    provided by Ken Perlin seems to create the fewest artifacts
    near the origin.
    '''
    return [
        151,160,137, 91, 90, 15,131, 13,201, 95, 96, 53,194,233,  7,225,
        140, 36,103, 30, 69,142,  8, 99, 37,240, 21, 10, 23,190,  6,148,
        247,120,234, 75,  0, 26,197, 62, 94,252,219,203,117, 35, 11, 32,
         57,177, 33, 88,237,149, 56, 87,174, 20,125,136,171,168, 68,175,
         74,165, 71,134,139, 48, 27,166, 77,146,158,231, 83,111,229,122,
         60,211,133,230,220,105, 92, 41, 55, 46,245, 40,244,102,143, 54,
         65, 25, 63,161,  1,216, 80, 73,209, 76,132,187,208, 89, 18,169,
        200,196,135,130,116,188,159, 86,164,100,109,198,173,186,  3, 64,
         52,217,226,250,124,123,  5,202, 38,147,118,126,255, 82, 85,212,
        207,206, 59,227, 47, 16, 58, 17,182,189, 28, 42,223,183,170,213,
        119,248,152,  2, 44,154,163, 70,221,153,101,155,167, 43,172,  9,
        129, 22, 39,253, 19, 98,108,110, 79,113,224,232,178,185,112,104,
        218,246, 97,228,251, 34,242,193,238,210,144, 12,191,179,162,241,
         81, 51,145,235,249, 14,239,107, 49,192,214, 31,181,199,106,157,
        184, 84,204,176,115,121, 50, 45,127,  4,150,254,138,236,205, 93,
        222,114, 67, 29, 24, 72,243,141,128,195, 78, 66,215, 61,156,180,
    ]

if not pyglet.gl.gl_info.have_extension('GL_EXT_gpu_shader4'):
  eprint("GL_EXT_gpu_shader4 is not supported in this environment, but is required by the shader. "
         "Display may be corrupted!")

window = TextureWindow('perlin_reference/proc_shader')
pyglet.app.run()
