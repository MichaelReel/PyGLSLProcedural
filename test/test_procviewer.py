import unittest, sys

# Deal with v2 and v3 differences in int types
if sys.version_info < (3,):
    integer_types = (int, long,)
else:
    integer_types = (int,)

# Pull in the procviewer file for testing
sys.path.append("..")
from procviewer import *

class BaseCase(unittest.TestCase):

    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(__class__)

class TestTextureShaderInitBlank(BaseCase):

    def setUp(self):
        # Ensure there's no json for blank
        self.tearDown()
        self.shader = TextureShader("blank/blank_shader")

    def test_handle_created(self):
        self.assertTrue(isinstance(self.shader.handle, integer_types))
        self.assertGreater(self.shader.handle, 0)

    def test_shader_is_linked(self):
        self.assertTrue(self.shader.linked)

    def test_empty_bindings_file_created(self):
        keyBindingsFile = "blank/blank_shader.bindings.json"
        self.assertTrue(os.path.isfile(keyBindingsFile))
        with open(keyBindingsFile, "r") as jsonFile:
            self.assertEqual(jsonFile.readlines(), ["{}"])

    def test_no_key_bindings_loaded_or_created(self):
        # Check bindings is a dictionary
        self.assertIs(type(self.shader.bindings), dict)
        # Check the dictionary is empty
        self.assertFalse(self.shader.bindings)

    def tearDown(self):
        # Remove any json for blank
        try:
            os.remove("blank/blank_shader.bindings.json")
        except OSError:
            pass

class TestLoadKeyBindings(BaseCase):

    def setUp(self):
        # Start with the blank shader
        self.shader = TextureShader("blank/blank_shader")
        # Load a different json file
        self.shader.loadKeyBindings("bindings/loadkey.json")
    

class TestStaticFunctions(BaseCase):

    from pyglet.window import key

    def test_preferredKeyOrder(self):
        for x in preferredKeyOrder():
            self.assertTrue(x in key._key_names)

    def test_updatePermutation(self):
        binding = {}
        binding['loop'] = 5
        binding['seed'] = 1
        # The values after 'loop' will get overwritten
        binding['default'] = [0, 1, 2, 3, 4, 9, 9, 9, 9, 9]
        updatePermutation(binding)
        # Other values should not have been changed
        self.assertEquals(binding['loop'], 5)
        self.assertEquals(binding['seed'], 1)
        # Default should have changed, random reorder of
        # the first 5 values, duplicated
        self.assertEquals(binding['default'], [1, 4, 2, 3, 0, 1, 4, 2, 3, 0])
        # Note, the seed makes this predictable

if __name__ == '__main__':
    unittest.main()