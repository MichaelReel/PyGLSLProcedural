import unittest, sys, re
try:
    from unittest.mock import create_autospec
except ImportError:
    from mock import create_autospec

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

loadfile = "bindings/loadkey.json"
savefile = "bindings/savekey.json"

class TestLoadKeyBindings(BaseCase):

    def setUp(self):
        # Start with the blank shader
        self.shader = TextureShader("blank/blank_shader")
        # Load a different json file
        self.shader.loadKeyBindings(loadfile)

    def test_binding_load(self):
        # Check bindings have been loaded
        # {"zoom": {"default": 0.02, "dec_key": 102, "type": "float", "inc_key": 114, "diff": 0.0005}}
        self.assertIn("zoom", self.shader.bindings)
        binding = self.shader.bindings["zoom"]
        self.assertIn("dec_key", binding)
        self.assertEqual(binding["dec_key"], 102)

class TestSaveKeyBindings(BaseCase):

    def setUp(self):
        # Clear any file that exists
        self.tearDown()
        # Start with the blank shader
        self.shader = TextureShader("blank/blank_shader")
        # Load a different json file
        self.shader.loadKeyBindings(loadfile)
        # Save key binds to a new file
        self.shader.saveKeyBindings(savefile)

    def test_binding_save(self):
        # do a byte compare (should work :-/)
        with open (loadfile, "r") as lf, open (savefile, "r") as sf:
            loadBindings = json.load(lf)
            saveBindings = json.load(sf)
            self.assertEqual(loadBindings, saveBindings)

    def tearDown(self):
        try:
            os.remove(savefile)
        except OSError:
            pass

class TestCheckKeyBindingsFromShaderUniforms(BaseCase):

    def setUp(self):
        self.shader = TextureShader("blank/blank_shader")
        self.shader.checkNumericKeyBindingsFromShader = create_autospec(self.shader.checkNumericKeyBindingsFromShader, return_value = False)
        self.shader.checkBooleanKeyBindingsFromShader = create_autospec(self.shader.checkBooleanKeyBindingsFromShader, return_value = False)
        self.shader.checkArrayKeyBindingsFromShader   = create_autospec(self.shader.checkArrayKeyBindingsFromShader,   return_value = False)

    def assertBindingChecksCalled(self, shaderCode):
        # All subtasks are called once each 
        # Whether binding found or not
        self.shader.checkNumericKeyBindingsFromShader.assert_called_once_with(shaderCode)
        self.shader.checkBooleanKeyBindingsFromShader.assert_called_once_with(shaderCode)
        self.shader.checkArrayKeyBindingsFromShader.assert_called_once_with(shaderCode)

    def testFoundNoUniforms(self):
        shaderCode = ""
        self.assertFalse(self.shader.checkKeyBindingsFromShaderUniforms(shaderCode, "test"))
        self.assertBindingChecksCalled(shaderCode)

    def testFoundNumericUniforms(self):
        shaderCode = ""
        self.shader.checkNumericKeyBindingsFromShader.return_value = True
        self.assertTrue(self.shader.checkKeyBindingsFromShaderUniforms(shaderCode, "test"))
        self.assertBindingChecksCalled(shaderCode)

    def testFoundBooleanUniforms(self):
        shaderCode = ""
        self.shader.checkBooleanKeyBindingsFromShader.return_value = True
        self.assertTrue(self.shader.checkKeyBindingsFromShaderUniforms(shaderCode, "test"))
        self.assertBindingChecksCalled(shaderCode)

    def testFoundArrayUniforms(self):
        shaderCode = ""
        self.shader.checkArrayKeyBindingsFromShader.return_value = True
        self.assertTrue(self.shader.checkKeyBindingsFromShaderUniforms(shaderCode, "test"))
        self.assertBindingChecksCalled(shaderCode)

class TestCheckNumericKeyBindingsFromShader(BaseCase):

    def setUp(self):
        self.shader = TextureShader("blank/blank_shader")
        self.shader.checkShaderBinding = create_autospec(self.shader.checkShaderBinding)

    def test_no_uniforms_found(self):
        self.assertFalse(self.shader.checkNumericKeyBindingsFromShader(""))
        self.assertFalse(self.shader.checkShaderBinding.called)

    def test_bools_arrays_not_found(self):
        self.assertFalse(self.shader.checkNumericKeyBindingsFromShader(
            "uniform bool boolname; uniform float arrayname[1];"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 0)
    
    def test_ints_floats_found(self):
        self.assertTrue(self.shader.checkNumericKeyBindingsFromShader(
            "uniform bool boolname; uniform float arrayname[1];"
            "uniform int intname; uniform float floatname;"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 2)
        
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
        self.assertEqual(binding['loop'], 5)
        self.assertEqual(binding['seed'], 1)
        # Default should have changed, random reorder of
        # the first 5 values
        self.assertEqual(sorted(binding['default'][:5]), list(range(0, 5)))
        # The second half of the list should be the same as the first
        self.assertEqual(binding['default'][:5], binding['default'][5:])
        # Note, the seed is meant to make this predictable:
        print(binding['default'])

if __name__ == '__main__':
    unittest.main()