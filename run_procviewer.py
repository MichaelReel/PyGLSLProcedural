from __future__ import print_function
from procviewer import ShaderController
from pyglet.gl import *
from random import Random
import pyglet, os, time

class TextureWindow(pyglet.window.Window):

    def __init__(self, shader_path):
        self.w = 512
        self.h = 512

        self.textureShader = ShaderController(shader_path)
        super(TextureWindow, self).__init__(caption = shader_path, width=self.w, height=self.h)

        self.createKeyHelpLabels()

    def createKeyHelpLabels(self):
        self.helpLabels = []
        y = self.height
        for labelText in self.textureShader.get_html_help():
            self.helpLabels.append(pyglet.text.HTMLLabel(
                    "<font face='Courier New' color='white'>{}</font>".format(labelText),
                    x=0, y=y,
                    anchor_x='left', anchor_y='top'))
            y -= 20
    
    def updateStatusLabels(self):
        self.statusLabels = []
        y = 20
        label = 0
        for labelText in self.textureShader.get_statuses():
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
        self.textureShader.mouse_drag(dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.textureShader.mouse_scroll_y(scroll_y)

    def on_key_release(self, symbol, modifiers):
        self.textureShader.binding_trigger(symbol)

    def saveFromShader(self):
        a = (GLubyte * (4 * self.w * self.h))(0)
        # Save without any GUI elements
        self.drawGenerated()
        glReadPixels(0, 0, self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, a)
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
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1., 1., 1., -1., 0., 1.)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.textureShader.bind()

        self.textureShader.set_uniforms()

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
window = TextureWindow('spike/working_shader')

pyglet.app.run()
