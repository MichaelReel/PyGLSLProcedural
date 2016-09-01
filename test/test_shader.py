import unittest, sys

# Deal with v2 and v3 differences in int types
if sys.version_info < (3,):
    integer_types = (int, long,)
else:
    integer_types = (int,)

# Pull in the shader file for testing
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

class ShaderTestBase(unittest.TestCase):

    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(__class__)

class TestShaderInit(ShaderTestBase):

    def setUp(self):
        self.shader = Shader(vertexCode, fragmentCode)

    def test_handle_created(self):
        self.assertTrue(isinstance(self.shader.handle, integer_types))
        self.assertGreater(self.shader.handle, 0)

    def test_shader_is_linked(self):
        self.assertTrue(self.shader.linked)

class TestShaderLink(ShaderTestBase):

    def test_bad_shaders_link(self):
        shader = Shader("", "")
        shader.link()
        self.assertFalse(shader.linked)

    def test_ok_shaders_link(self):
        shader = Shader(vertexCode, fragmentCode)
        shader.link()
        self.assertTrue(shader.linked)

class TestShaderBind(ShaderTestBase):

    def setUp(self):
        self.shader = Shader(vertexCode, fragmentCode)

    def test_bind(self):
        self.shader.bind()

    def test_unbind(self):
        self.shader.unbind()

class TestShaderUniformFloat(ShaderTestBase):

    def setUp(self):
        self.shader = Shader(vertexCode, fragmentCode)
        self.shader.bind()

    def test_float_1(self):
        testFloat = 0.0
        self.shader.uniformf('', *[testFloat])

    def tearDown(self):
        self.shader.unbind()


if __name__ == '__main__':
    unittest.main()