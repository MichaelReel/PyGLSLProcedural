import unittest, sys, io

# Deal with v2 and v3 differences in int types
if sys.version_info < (3,):
    integer_types = (int, long,)
else:
    integer_types = (int,)

# Pull in the shader file for testing
sys.path.append("..")
from shader import Shader

vertexCode = ' '.join(io.open('blank/blank_shader.v.glsl'))
fragmentCode = ' '.join(io.open('blank/blank_shader.f.glsl'))

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
        self.shader.uniformf('', *[0.0])

    def test_float_2(self):
        self.shader.uniformf('', *[0.0, 0.1])
        
    def test_float_3(self):
        self.shader.uniformf('', *[0.0, 0.1, 0.2])
        
    def test_float_4(self):
        self.shader.uniformf('', *[0.0, 0.1, 0.2, 0.3])
        
    def test_float_5(self):
        self.shader.uniformf('', *[0.0, 0.1, 0.2, 0.3, 0.4])

    def tearDown(self):
        self.shader.unbind()

class TestShaderUniformInt(ShaderTestBase):

    def setUp(self):
        self.shader = Shader(vertexCode, fragmentCode)
        self.shader.bind()

    def test_int_1(self):
        self.shader.uniformf('', *[0])

    def test_int_2(self):
        self.shader.uniformf('', *[0, 1])
        
    def test_int_3(self):
        self.shader.uniformf('', *[0, 1, 2])
        
    def test_int_4(self):
        self.shader.uniformf('', *[0, 1, 2, 3])
        
    def test_int_5(self):
        self.shader.uniformf('', *[0, 1, 2, 3, 4])

    def tearDown(self):
        self.shader.unbind()

class TestShaderUniformMatrix(ShaderTestBase):

    def setUp(self):
        self.shader = Shader(vertexCode, fragmentCode)
        self.shader.bind()

    def test_matrix(self):
        # Why not the identity matrix? ;-)
        # Needs to be a flat list, of course
        matrix = [(1.0 if x == y else 0.0) for x in range(4) for y in range(4)]
        self.shader.uniform_matrixf('', matrix)

    def tearDown(self):
        self.shader.unbind()

if __name__ == '__main__':
    unittest.main()