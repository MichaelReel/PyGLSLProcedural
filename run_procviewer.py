'''
This is the run file. Run this file to load a shader and attempt to get it to draw.abs
To pick a shader, change the window creation line below to:
`window = TextureWindow('path/file')`
'''

from __future__ import print_function
import os
import time
import io
import pyglet
from pyglet import gl
from pyglet.window import key
from procviewer import ShaderController
from shader import Shader

class TextureWindow(pyglet.window.Window):
    '''
    Concrete draw window. This uses the ShaderController to load and operate the shader at the path
    passed to the constructor.
    '''

    def __init__(self, shader_path):
        '''
        Load and attempt to run the shader at shader_path.
        '''
        self.w = 512
        self.h = 512

        # Load shader code
        vspath = '%s.v.glsl' % shader_path
        fspath = '%s.f.glsl' % shader_path
        with io.open(vspath) as vstrm, io.open(fspath) as fstrm:
            vertexshader = ' '.join(vstrm)
            fragmentshader = ' '.join(fstrm)

        self.shader = Shader(vertexshader, fragmentshader)
        self.shader_controller = ShaderController(self.shader, shader_path)
        super(TextureWindow, self).__init__(caption=shader_path, width=self.w, height=self.h)

        self.create_key_help_labels()

    def create_key_help_labels(self):
        '''
        Create the help labels to display overlaying the drawn shader
        '''
        self.helpLabels = []
        y = self.height
        for labelText in self.shader_controller.get_html_help(key):
            self.helpLabels.append(pyglet.text.HTMLLabel(
                    "<font face='Courier New' color='white'>{}</font>".format(labelText),
                    x=0, y=y,
                    anchor_x='left', anchor_y='top'))
            y -= 20
    
    def updateStatusLabels(self):
        self.statusLabels = []
        y = 20
        label = 0
        for labelText in self.shader_controller.get_statuses():
            # Create a new label if we need one (suddenly)
            if label >= len(self.statusLabels):
                self.statusLabels.append(pyglet.text.HTMLLabel("",
                    x=0, y=y,
                    anchor_x='left', anchor_y='top'))
            # Modify an existing label to give it status text
            self.statusLabels[label].text = "<font face='Courier New' color='white'>{}</font>".format(labelText)
            y += 20
            label += 1

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.shader_controller.mouse_drag(dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.shader_controller.mouse_scroll_y(scroll_y)

    def on_key_release(self, symbol, modifiers):
        self.shader_controller.binding_trigger(symbol)

    def saveFromShader(self):
        a = (gl.GLubyte * (4 * self.w * self.h))(0)
        # Save without any GUI elements
        self.drawGenerated()
        gl.glReadPixels(0, 0, self.w, self.h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, a)
        image = pyglet.image.ImageData(self.w, self.h, 'RGBA', a)
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        filePath = scriptPath + "/TESTSAVE_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
        print ("saved to {}".format(filePath))
        image.save(filePath)

    def on_draw(self):
        self.drawGenerated()
        self.updateStatusLabels()
        self.drawGUI()
        
    def drawGenerated(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-1., 1., 1., -1., 0., 1.)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        self.shader.bind()

        self.shader_controller.set_uniforms()

        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2i(-1, -1)
        gl.glTexCoord2i(-2, -2)
        gl.glVertex2f(1, -1)
        gl.glTexCoord2i(2, -2)
        gl.glVertex2i(1, 1)
        gl.glTexCoord2i(2, 2)
        gl.glVertex2i(-1, 1)
        gl.glTexCoord2i(-2, 2)
        gl.glEnd()

        self.shader.unbind()

    def drawGUI(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.w, 0, self.h, -1, 1)

        for label in self.helpLabels:
            label.draw()
        for label in self.statusLabels:
            label.draw()

if not pyglet.gl.gl_info.have_extension('GL_EXT_gpu_shader4'):
    print("GL_EXT_gpu_shader4 is not supported in this environment, but is required by the shader. "
          "Display may be corrupted!")

# Comment all but one of the following calls to TextureWindow to select a shader:

# window = TextureWindow('perlin_reference/proc_shader')
# window = TextureWindow('tiled/tile_shader')
# window = TextureWindow('scrappy_grid/scrap_grid')
# window = TextureWindow('blobs/blobs_shader')
# window = TextureWindow('spike/working_shader')
window = TextureWindow('julia/julia')

pyglet.app.run()
