import unittest, sys
sys.path.append("..")
from shader import Shader

vertexCode = """
//vertex
#version 110
void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
"""

fragmentCode = """
//fragment
"""

class TestShaderInit(unittest.TestCase):

    def setUp(self):
        
        self.shader = Shader(vertexCode, fragmentCode)

    def test_handle_created(self):
        shader = self.shader
        self.assertTrue(isinstance(shader.handle, long))
        self.assertGreater(shader.handle, 0)

    def test_shader_is_linked(self):
        shader = self.shader
        self.assertTrue(shader.linked)

    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestShaderInit)

if __name__ == '__main__':
    unittest.main()