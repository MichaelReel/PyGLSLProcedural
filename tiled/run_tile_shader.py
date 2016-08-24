from __future__ import print_function
import pyglet, os, time, sys, io, math
from pyglet.gl import *
sys.path.append("..")
from shader import Shader

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class ShaderWindow(pyglet.window.Window):
    def __init__(self, shader_path):
        self.w = 512
        self.h = 512

        # Scaling values
        self.x = -1.345
        self.y = -1.275
        self.z = 0.0
        self.zoom = 0.025
        self.octives = 5
        self.freq = 1.0 / 32.0
        self.tile = 10
        self.bound = True
        self.gui = True

        super(ShaderWindow, self).__init__(caption = 'Shader', width=self.w, height=self.h)

        self.shader = Shader(
          ' '.join(io.open('%s.v.glsl' % shader_path)),
          ' '.join(io.open('%s.f.glsl' % shader_path))
        )

        self.perm = []
        permutation = self.getPermutation()
        for i in range(512):
            self.perm.append(permutation[i % len(permutation)])

        self.label1 = pyglet.text.Label('---',
                        font_name='Courier New',
                        font_size=10,
                        x=0, y=20,
                        anchor_x='left', anchor_y='bottom')

        self.label2 = pyglet.text.Label('---',
                        font_name='Courier New',
                        font_size=10,
                        x=0, y=5,
                        anchor_x='left', anchor_y='bottom')

        self.helpLabel1 = pyglet.text.HTMLLabel(
                        '''
                        <font face="Courier New" color="white">
                        <b>F2</b>:save, 
                        <b>H</b>:toggle-gui, 
                        <b><font size="6">&uarr;</font>/<font size="6">&darr;</font></b>:z-axis
                        </font>
                        ''',
                        x=0, y=self.height + 10,
                        anchor_x='left', anchor_y='top')
        self.helpLabel2 = pyglet.text.HTMLLabel(
                        '''
                        <font face="Courier New" color="white">
                        <b><font size="6">&larr;</font>/<font size="6">&rarr;</font></b>:tile-size,
                        <b>B</b>:toggle-bounds
                        </font>
                        ''',
                        x=0, y=self.height - 10,
                        anchor_x='left', anchor_y='top')
        self.helpLabel3 = pyglet.text.HTMLLabel(
                        '''
                        <font face="Courier New" color="white">
                        <b>Q/A</b>:octives, <b>W/S</b>:frequency
                        </font>
                        ''',
                        x=0, y=self.height - 40,
                        anchor_x='left', anchor_y='top')

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.x -= dx * self.zoom
        self.y -= dy * self.zoom
      
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.zoom -= scroll_y * 0.0025

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.F2:
            self.saveFromShader()
        elif symbol == pyglet.window.key.UP:
            self.z += 0.1
        elif symbol == pyglet.window.key.DOWN:
            self.z -= 0.1
        elif symbol == pyglet.window.key.RIGHT:
            self.tile += 1
        elif symbol == pyglet.window.key.LEFT:
            self.tile -= 1
        elif symbol == pyglet.window.key.Q:
            self.octives += 1
        elif symbol == pyglet.window.key.A:
            self.octives -= 1
        elif symbol == pyglet.window.key.W:
            self.freq += 0.01
        elif symbol == pyglet.window.key.S:
            self.freq -= 0.01
        elif symbol == pyglet.window.key.B:
            self.bound = not self.bound
        elif symbol == pyglet.window.key.H:
            self.gui = not self.gui
      
    def saveFromShader(self):
        a = (GLubyte * (4 * self.w * self.h))(0)
        # Save without the GUI elements
        self.drawGenerated()
        glReadPixels(0, 0, self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, a)
        image = pyglet.image.ImageData(self.w, self.h, 'RGBA', a)
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        filePath = scriptPath + "/TESTSAVE_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
        print ("saved to {}".format(filePath))
        image.save(filePath)

    def getPermutation(self):
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

    def on_draw(self):
        self.drawGenerated()
        if (self.gui):
            self.drawGUI()

    def drawGenerated(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1., 1., 1., -1., 0., 1.)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.shader.bind()
        self.shader.uniformi('perm', *self.perm)
        self.shader.uniformf('x', *[self.x])
        self.shader.uniformf('y', *[self.y])
        self.shader.uniformf('z', *[self.z])
        self.shader.uniformf('zoom', *[self.zoom])
        self.shader.uniformi('octives', *[self.octives])
        self.shader.uniformf('freq', *[self.freq])
        self.shader.uniformi('tile', *[self.tile])
        self.shader.uniformi('bound', *[self.bound])

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

        self.shader.unbind()
    
    def drawGUI(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, -1, 1)

        self.label1.text = "coords: ({},{},{}) zoom: {}\n".format(self.x, self.y, self.z, self.zoom)
        self.label2.text = "tile: {}, octs: {}, freq: {}, bound: {}\n".format(self.tile, self.octives, self.freq, self.bound)

        self.helpLabel1.draw()
        self.helpLabel2.draw()
        self.helpLabel3.draw()

        self.label1.draw()
        self.label2.draw()


if not pyglet.gl.gl_info.have_extension('GL_EXT_gpu_shader4'):
    eprint("GL_EXT_gpu_shader4 is not supported in this environment, but is required by the shader. "
           "Display may be corrupted!")

window = ShaderWindow('tile_shader')
pyglet.app.run()

