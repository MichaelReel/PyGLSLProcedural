import unittest, sys
from test_base import *

# Pull in the procviewer file for testing
from procviewer import *

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
        super(TestSaveKeyBindings, self).tearDown()
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

    def test_bools_arrays_not_found(self):
        self.assertFalse(self.shader.checkNumericKeyBindingsFromShader(
            "uniform bool boolname; uniform float arrayname[1];"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 0)
    
    def test_ints_floats_found(self):
        self.assertTrue(self.shader.checkNumericKeyBindingsFromShader(
            "uniform bool boolname; uniform float arrayname[1];"
            "uniform int intname; uniform float floatname;"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 2)

class TestCheckBooleanKeyBindingsFromShader(BaseCase):

    def setUp(self):
        self.shader = TextureShader("blank/blank_shader")
        self.shader.checkShaderBinding = create_autospec(self.shader.checkShaderBinding)

    def test_floats_ints_arrays_not_found(self):
        self.assertFalse(self.shader.checkBooleanKeyBindingsFromShader(
            "uniform float arrayname[1];"
            "uniform int intname; uniform float floatname;"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 0)
    
    def test_bools_found(self):
        self.assertTrue(self.shader.checkBooleanKeyBindingsFromShader(
            "uniform bool boolname; uniform float arrayname[1];"
            "uniform int intname; uniform float floatname;"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 1)

class TestCheckArrayKeyBindingsFromShader(BaseCase):

    def setUp(self):
        self.shader = TextureShader("blank/blank_shader")
        self.shader.checkShaderBinding = create_autospec(self.shader.checkShaderBinding)

    def test_floats_ints_bools_not_found(self):
        self.assertFalse(self.shader.checkArrayKeyBindingsFromShader(
            "uniform bool boolname;"
            "uniform int intname; uniform float floatname;"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 0)
    
    def test_bools_found(self):
        self.assertTrue(self.shader.checkArrayKeyBindingsFromShader(
            "uniform bool boolname; uniform float arrayname[1];"
            "uniform int intname; uniform float floatname;"))
        self.assertEqual(self.shader.checkShaderBinding.call_count, 1)

class TestCheckShaderBinding(BaseCase):

    class mockUniform(object):
        def group(self, key):
            return key

    def setUp(self):
        self.shader = TextureShader("blank/blank_shader")
        self.shader.createBinding = create_autospec(self.shader.createBinding)
        self.uniform = TestCheckShaderBinding.mockUniform()

    def test_name_not_in_bindings(self):
        self.shader.checkShaderBinding(self.uniform)
        self.shader.createBinding.assert_called_once_with(self.uniform)
    
    def test_name_in_bindings_already_same_type(self):
        self.shader.bindings['name'] = {}
        self.shader.bindings['name']['type'] = 'type'
        self.shader.checkShaderBinding(self.uniform)
        self.assertEqual(self.shader.createBinding.call_count, 0)

    def test_name_in_bindings_new_type(self):
        self.shader.bindings['name'] = {}
        self.shader.bindings['name']['type'] = 'oldtype'
        self.shader.checkShaderBinding(self.uniform)
        self.shader.createBinding.assert_called_once_with(self.uniform)

class TestCreateBinding(BaseCase):

    class mockUniform(object):
        def __init__(self):
            self.gdict = {}

        def group(self, key):
            return self.gdict[key]

        def groupdict(self):
            return self.gdict

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.viewer.createArrayBinding = create_autospec(self.viewer.createArrayBinding)
        self.viewer.setupInt   = create_autospec(self.viewer.setupInt)
        self.viewer.setupFloat = create_autospec(self.viewer.setupFloat)
        self.viewer.setupBool  = create_autospec(self.viewer.setupBool)
        self.viewer.setupVec2  = create_autospec(self.viewer.setupVec2)
        self.viewer.setupVec3  = create_autospec(self.viewer.setupVec3)
        self.viewer.setupVec4  = create_autospec(self.viewer.setupVec4)

        self.uniform = TestCreateBinding.mockUniform()

    def test_size_is_set(self):
        self.uniform.gdict['size'] = '1'
        self.viewer.createBinding(self.uniform)
        self.viewer.createArrayBinding.assert_called_once_with(self.uniform)
        self.assertEqual(self.viewer.setupInt  .call_count, 0)
        self.assertEqual(self.viewer.setupFloat.call_count, 0)
        self.assertEqual(self.viewer.setupBool .call_count, 0)
        self.assertEqual(self.viewer.setupVec2 .call_count, 0)
        self.assertEqual(self.viewer.setupVec3 .call_count, 0)
        self.assertEqual(self.viewer.setupVec4 .call_count, 0)

    def test_type_is_int(self):
        self.uniform.gdict['name'] = 'an_int'
        self.uniform.gdict['type'] = 'int'
        self.viewer.createBinding(self.uniform)
        self.assertEqual(self.viewer.createArrayBinding.call_count, 0)
        self.viewer.setupInt.assert_called_once_with(self.viewer.bindings['an_int'], self.uniform)
        self.assertEqual(self.viewer.setupFloat.call_count, 0)
        self.assertEqual(self.viewer.setupBool .call_count, 0)
        self.assertEqual(self.viewer.setupVec2 .call_count, 0)
        self.assertEqual(self.viewer.setupVec3 .call_count, 0)
        self.assertEqual(self.viewer.setupVec4 .call_count, 0)
        self.assertEqual(self.viewer.bindings['an_int']['type'], 'int')
        
    def test_type_is_float(self):
        self.uniform.gdict['name'] = 'a_float'
        self.uniform.gdict['type'] = 'float'
        self.viewer.createBinding(self.uniform)
        self.assertEqual(self.viewer.createArrayBinding.call_count, 0)
        self.assertEqual(self.viewer.setupInt  .call_count, 0)
        self.viewer.setupFloat.assert_called_once_with(self.viewer.bindings['a_float'], self.uniform)
        self.assertEqual(self.viewer.setupBool .call_count, 0)
        self.assertEqual(self.viewer.setupVec2 .call_count, 0)
        self.assertEqual(self.viewer.setupVec3 .call_count, 0)
        self.assertEqual(self.viewer.setupVec4 .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_float']['type'], 'float')
        
    def test_type_is_bool(self):
        self.uniform.gdict['name'] = 'a_bool'
        self.uniform.gdict['type'] = 'bool'
        self.viewer.createBinding(self.uniform)
        self.assertEqual(self.viewer.createArrayBinding.call_count, 0)
        self.assertEqual(self.viewer.setupInt  .call_count, 0)
        self.assertEqual(self.viewer.setupFloat.call_count, 0)
        self.viewer.setupBool.assert_called_once_with(self.viewer.bindings['a_bool'], self.uniform)
        self.assertEqual(self.viewer.setupVec2 .call_count, 0)
        self.assertEqual(self.viewer.setupVec3 .call_count, 0)
        self.assertEqual(self.viewer.setupVec4 .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_bool']['type'], 'bool')
        
    def test_type_is_vec2(self):
        self.uniform.gdict['name'] = 'a_vec'
        self.uniform.gdict['type'] = 'vec2'
        self.viewer.createBinding(self.uniform)
        self.assertEqual(self.viewer.createArrayBinding.call_count, 0)
        self.assertEqual(self.viewer.setupInt  .call_count, 0)
        self.assertEqual(self.viewer.setupFloat.call_count, 0)
        self.assertEqual(self.viewer.setupBool .call_count, 0)
        self.viewer.setupVec2.assert_called_once_with(self.viewer.bindings['a_vec'], self.uniform)
        self.assertEqual(self.viewer.setupVec3 .call_count, 0)
        self.assertEqual(self.viewer.setupVec4 .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_vec']['type'], 'vec2')
        
    def test_type_is_vec3(self):
        self.uniform.gdict['name'] = 'a_vec'
        self.uniform.gdict['type'] = 'vec3'
        self.viewer.createBinding(self.uniform)
        self.assertEqual(self.viewer.createArrayBinding.call_count, 0)
        self.assertEqual(self.viewer.setupInt  .call_count, 0)
        self.assertEqual(self.viewer.setupFloat.call_count, 0)
        self.assertEqual(self.viewer.setupBool .call_count, 0)
        self.assertEqual(self.viewer.setupVec2 .call_count, 0)
        self.viewer.setupVec3.assert_called_once_with(self.viewer.bindings['a_vec'], self.uniform)
        self.assertEqual(self.viewer.setupVec4 .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_vec']['type'], 'vec3')
        
    def test_type_is_vec4(self):
        self.uniform.gdict['name'] = 'a_vec'
        self.uniform.gdict['type'] = 'vec4'
        self.viewer.createBinding(self.uniform)
        self.assertEqual(self.viewer.createArrayBinding.call_count, 0)
        self.assertEqual(self.viewer.setupInt  .call_count, 0)
        self.assertEqual(self.viewer.setupFloat.call_count, 0)
        self.assertEqual(self.viewer.setupBool .call_count, 0)
        self.assertEqual(self.viewer.setupVec2 .call_count, 0)
        self.assertEqual(self.viewer.setupVec3 .call_count, 0)
        self.viewer.setupVec4.assert_called_once_with(self.viewer.bindings['a_vec'], self.uniform)
        self.assertEqual(self.viewer.bindings['a_vec']['type'], 'vec4')

class TestCreateArrayBinding(BaseCase):

    class mockUniform(object):
        def __init__(self):
            self.gdict = {}

        def group(self, key):
            return self.gdict[key]

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.viewer.setupIntArray   = create_autospec(self.viewer.setupIntArray)
        self.viewer.setupFloatArray = create_autospec(self.viewer.setupFloatArray)
        self.viewer.setupBoolArray  = create_autospec(self.viewer.setupBoolArray)
        self.viewer.setupVec2Array  = create_autospec(self.viewer.setupVec2Array)
        self.viewer.setupVec3Array  = create_autospec(self.viewer.setupVec3Array)
        self.viewer.setupVec4Array  = create_autospec(self.viewer.setupVec4Array)

        self.uniform = TestCreateArrayBinding.mockUniform()

    def test_type_is_int(self):
        self.uniform.gdict['name'] = 'an_int'
        self.uniform.gdict['type'] = 'int'
        self.viewer.createArrayBinding(self.uniform)
        self.viewer.setupIntArray.assert_called_once_with(self.viewer.bindings['an_int'], self.uniform)
        self.assertEqual(self.viewer.setupFloatArray.call_count, 0)
        self.assertEqual(self.viewer.setupBoolArray .call_count, 0)
        self.assertEqual(self.viewer.setupVec2Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec3Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec4Array .call_count, 0)
        self.assertEqual(self.viewer.bindings['an_int']['type'], 'int')
        
    def test_type_is_float(self):
        self.uniform.gdict['name'] = 'a_float'
        self.uniform.gdict['type'] = 'float'
        self.viewer.createArrayBinding(self.uniform)
        self.assertEqual(self.viewer.setupIntArray  .call_count, 0)
        self.viewer.setupFloatArray.assert_called_once_with(self.viewer.bindings['a_float'], self.uniform)
        self.assertEqual(self.viewer.setupBoolArray .call_count, 0)
        self.assertEqual(self.viewer.setupVec2Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec3Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec4Array .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_float']['type'], 'float')
        
    def test_type_is_bool(self):
        self.uniform.gdict['name'] = 'a_bool'
        self.uniform.gdict['type'] = 'bool'
        self.viewer.createArrayBinding(self.uniform)
        self.assertEqual(self.viewer.setupIntArray  .call_count, 0)
        self.assertEqual(self.viewer.setupFloatArray.call_count, 0)
        self.viewer.setupBoolArray.assert_called_once_with(self.viewer.bindings['a_bool'], self.uniform)
        self.assertEqual(self.viewer.setupVec2Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec3Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec4Array .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_bool']['type'], 'bool')
        
    def test_type_is_vec2(self):
        self.uniform.gdict['name'] = 'a_vec'
        self.uniform.gdict['type'] = 'vec2'
        self.viewer.createArrayBinding(self.uniform)
        self.assertEqual(self.viewer.setupIntArray  .call_count, 0)
        self.assertEqual(self.viewer.setupFloatArray.call_count, 0)
        self.assertEqual(self.viewer.setupBoolArray .call_count, 0)
        self.viewer.setupVec2Array.assert_called_once_with(self.viewer.bindings['a_vec'], self.uniform)
        self.assertEqual(self.viewer.setupVec3Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec4Array .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_vec']['type'], 'vec2')
        
    def test_type_is_vec3(self):
        self.uniform.gdict['name'] = 'a_vec'
        self.uniform.gdict['type'] = 'vec3'
        self.viewer.createArrayBinding(self.uniform)
        self.assertEqual(self.viewer.setupIntArray  .call_count, 0)
        self.assertEqual(self.viewer.setupFloatArray.call_count, 0)
        self.assertEqual(self.viewer.setupBoolArray .call_count, 0)
        self.assertEqual(self.viewer.setupVec2Array .call_count, 0)
        self.viewer.setupVec3Array.assert_called_once_with(self.viewer.bindings['a_vec'], self.uniform)
        self.assertEqual(self.viewer.setupVec4Array .call_count, 0)
        self.assertEqual(self.viewer.bindings['a_vec']['type'], 'vec3')
        
    def test_type_is_vec4(self):
        self.uniform.gdict['name'] = 'a_vec'
        self.uniform.gdict['type'] = 'vec4'
        self.viewer.createArrayBinding(self.uniform)
        self.assertEqual(self.viewer.setupIntArray  .call_count, 0)
        self.assertEqual(self.viewer.setupFloatArray.call_count, 0)
        self.assertEqual(self.viewer.setupBoolArray .call_count, 0)
        self.assertEqual(self.viewer.setupVec2Array .call_count, 0)
        self.assertEqual(self.viewer.setupVec3Array .call_count, 0)
        self.viewer.setupVec4Array.assert_called_once_with(self.viewer.bindings['a_vec'], self.uniform)
        self.assertEqual(self.viewer.bindings['a_vec']['type'], 'vec4')

class TestSetupInt(BaseCase):

    class mockUniform(object):
        def __init__(self):
            self.gdict = {}

        def group(self, key):
            if key in self.gdict:
                return self.gdict[key]
            else:
                return None

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.uniform = TestSetupInt.mockUniform()
        self.binding = {}

    def test_no_default_no_diff(self):
        self.viewer.setupInt(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], 0)
        self.assertEqual(self.binding['diff'], 1)
        # Keys should be bound to the first 2 off the list
        self.assertEqual(self.binding['inc_key'], 113) # Q
        self.assertEqual(self.binding['dec_key'], 97)  # A

    def test_with_default_and_diff(self):
        self.uniform.gdict['default'] = 100
        self.uniform.gdict['diff'] = 20
        self.viewer.setupInt(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], 100)
        self.assertEqual(self.binding['diff'], 20)

class TestSetupFloat(BaseCase):

    class mockUniform(object):
        def __init__(self):
            self.gdict = {}

        def group(self, key):
            if key in self.gdict:
                return self.gdict[key]
            else:
                return None

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.uniform = TestSetupFloat.mockUniform()
        self.binding = {}

    def test_no_default_no_diff(self):
        self.viewer.setupFloat(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], 0)
        self.assertEqual(self.binding['diff'], 1)
        # Keys should be bound to the first 2 off the list
        self.assertEqual(self.binding['inc_key'], 113) # Q
        self.assertEqual(self.binding['dec_key'], 97)  # A

    def test_with_default_and_diff(self):
        self.uniform.gdict['default'] = 100
        self.uniform.gdict['diff'] = 20
        self.viewer.setupFloat(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], 100)
        self.assertEqual(self.binding['diff'], 20)

class TestSetupBool(BaseCase):

    class mockUniform(object):
        def __init__(self):
            self.gdict = {}

        def group(self, key):
            if key in self.gdict:
                return self.gdict[key]
            else:
                return None

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.uniform = TestSetupBool.mockUniform()
        self.binding = {}

    def test_no_default(self):
        self.viewer.setupBool(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], False)
        # Key should be bound to the first off the list
        self.assertEqual(self.binding['toggle_key'], 113) # Q

    def test_with_default(self):
        self.uniform.gdict['default'] = True
        self.viewer.setupBool(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], True)

class TestSetupVec(BaseCase):

    class mockUniform(object):
        def __init__(self):
            self.gdict = {}

        def group(self, key):
            if key in self.gdict:
                return self.gdict[key]
            else:
                return None

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.uniform = TestSetupVec.mockUniform()
        self.binding = {}

    def test_vec2(self):
        # Parsing not done yet, will update here when implementing
        self.viewer.setupVec2(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], (0.0, 0.0))

    def test_vec3(self):
        # Parsing not done yet, will update here when implementing
        self.viewer.setupVec3(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], (0.0, 0.0, 0.0))

    def test_vec4(self):
        # Parsing not done yet, will update here when implementing
        self.viewer.setupVec4(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], (0.0, 0.0, 0.0, 0.0))

class TestSetupIntArray(BaseCase):

    class mockUniform(object):
        def __init__(self):
            self.gdict = {}

        def group(self, key):
            if key in self.gdict:
                return self.gdict[key]
            else:
                return None

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.uniform = TestSetupIntArray.mockUniform()
        self.binding = {}

    def test_no_linesize_no_permutation(self):
        self.uniform.gdict['size'] = 5
        self.viewer.setupIntArray(self.binding, self.uniform)
        self.assertEqual(self.binding['default'], [0, 1, 2, 3, 4])
        self.assertEqual(self.binding['shuffle_key'], 113) # Q

    def test_with_linesize(self):
        self.uniform.gdict['size'] = 10
        self.uniform.gdict['line'] = 5
        self.viewer.setupIntArray(self.binding, self.uniform)
        self.assertEqual(self.binding['loop'], 5)
        self.assertEqual(self.binding['default'], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4])
        self.assertEqual(self.binding['shuffle_key'], 113) # Q

    def test_with_permutation_size_unseeded(self):
        self.uniform.gdict['size'] = 10
        self.uniform.gdict['perm'] = 5
        self.viewer.setupIntArray(self.binding, self.uniform)
        self.assertEqual(self.binding['loop'], 5)
        self.assertEqual(self.binding['seed'], 1)
        self.assertEqual(sorted(self.binding['default'][:5]), list(range(0, 5)))
        self.assertEqual(self.binding['default'][:5], self.binding['default'][5:])
        self.assertEqual(self.binding['shuffle_key'], 113) # Q

    def test_with_permutation_size_seeded(self):
        self.uniform.gdict['size'] = 10
        self.uniform.gdict['perm'] = 5
        self.uniform.gdict['seed'] = 50
        self.viewer.setupIntArray(self.binding, self.uniform)
        self.assertEqual(self.binding['loop'], 5)
        self.assertEqual(self.binding['seed'], 50)
        self.assertEqual(sorted(self.binding['default'][:5]), list(range(0, 5)))
        self.assertEqual(self.binding['default'][:5], self.binding['default'][5:])
        self.assertEqual(self.binding['shuffle_key'], 113) # Q

class TestUnimplementedSetupArrayMethods(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.uniform = TestSetupIntArray.mockUniform()
        self.binding = {}

    def test_float_array(self):
        self.assertRaises(NotImplementedError, self.viewer.setupFloatArray, self.binding, self.uniform)
        
    def test_bool_array(self):
        self.assertRaises(NotImplementedError, self.viewer.setupBoolArray, self.binding, self.uniform)
        
    def test_vec2_array(self):
        self.assertRaises(NotImplementedError, self.viewer.setupVec2Array, self.binding, self.uniform) 
        
    def test_vec3_array(self):
        self.assertRaises(NotImplementedError, self.viewer.setupVec3Array, self.binding, self.uniform) 
        
    def test_vec4_array(self):
        self.assertRaises(NotImplementedError, self.viewer.setupVec4Array, self.binding, self.uniform)

class TestBindingTrigger(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")

    def test_symbol_not_bound(self):
        self.assertFalse(self.viewer.bindingTrigger(key.Q))

    def test_toggle_key_bound(self):
        # Key bindings are normally prepared in the viewer.bindings and linked in usedkeys
        # Here we're just throwing them into usedkeys directly and ignoring the bindings table
        self.viewer.usedKeys[key.Q] = {}
        self.viewer.usedKeys[key.Q]['toggle_key'] = key.Q
        self.viewer.usedKeys[key.Q]['default'] = False
        # Check the bound key caused an action
        self.assertTrue(self.viewer.bindingTrigger(key.Q))
        # Check the default value was toggled
        self.assertTrue(self.viewer.usedKeys[key.Q]['default'])

    def test_inc_key_bound(self):
        self.viewer.usedKeys[key.Q] = {}
        self.viewer.usedKeys[key.Q]['inc_key'] = key.Q
        self.viewer.usedKeys[key.Q]['default'] = 10
        self.viewer.usedKeys[key.Q]['diff'] = 5
        # Check the bound key caused an action
        self.assertTrue(self.viewer.bindingTrigger(key.Q))
        # Check the default value was incremented
        self.assertEqual(self.viewer.usedKeys[key.Q]['default'], 15)

    def test_dec_key_bound(self):
        self.viewer.usedKeys[key.Q] = {}
        self.viewer.usedKeys[key.Q]['dec_key'] = key.Q
        self.viewer.usedKeys[key.Q]['default'] = 10
        self.viewer.usedKeys[key.Q]['diff'] = 5
        # Check the bound key caused an action
        self.assertTrue(self.viewer.bindingTrigger(key.Q))
        # Check the default value was decremented
        self.assertEqual(self.viewer.usedKeys[key.Q]['default'], 5)

    def test_shuffle_key_bound(self):
        self.viewer.usedKeys[key.Q] = {}
        self.viewer.usedKeys[key.Q]['shuffle_key'] = key.Q
        self.viewer.usedKeys[key.Q]['default'] = [0, 1, 2, 3, 4]
        self.viewer.usedKeys[key.Q]['loop'] = len(self.viewer.usedKeys[key.Q]['default'])
        self.viewer.usedKeys[key.Q]['seed'] = 1
        # Check the bound key caused an action
        self.assertTrue(self.viewer.bindingTrigger(key.Q))
        # Check the shuffle was triggered, i.e.: list is reordered
        self.assertNotEqual(self.viewer.usedKeys[key.Q]['default'], [0, 1, 2, 3, 4])
        # but still the same values
        self.assertEqual(sorted(self.viewer.usedKeys[key.Q]['default']), [0, 1, 2, 3, 4])

    def test_key_used_but_not_bound(self):
        self.viewer.usedKeys[key.Q] = {}
        # Check the bound key caused an exception
        self.assertRaises(ValueError, self.viewer.bindingTrigger, key.Q)

class TestSetUniforms(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")
        self.viewer.uniformi = create_autospec(self.viewer.uniformi)
        self.viewer.uniformf = create_autospec(self.viewer.uniformf)

    def test_no_uniforms(self):
        self.viewer.setUniforms()
        self.assertEqual(self.viewer.uniformi.call_count, 0)
        self.assertEqual(self.viewer.uniformf.call_count, 0)

    def test_int_uniform(self):
        self.viewer.bindings['an_int'] = {}
        self.viewer.bindings['an_int']['type'] = "int"
        self.viewer.bindings['an_int']['default'] = 1
        self.viewer.setUniforms()
        self.viewer.uniformi.assert_called_once_with('an_int', 1)
        self.assertEqual(self.viewer.uniformf.call_count, 0)
        
    def test_int_array_uniform(self):
        self.viewer.bindings['an_int_array'] = {}
        self.viewer.bindings['an_int_array']['type'] = "int"
        self.viewer.bindings['an_int_array']['default'] = [1, 2, 3, 4, 5]
        self.viewer.setUniforms()
        self.viewer.uniformi.assert_called_once_with('an_int_array', 1, 2, 3, 4, 5)
        self.assertEqual(self.viewer.uniformf.call_count, 0)

    def test_ivec2_uniform(self):
        self.viewer.bindings['an_ivec2'] = {}
        self.viewer.bindings['an_ivec2']['type'] = "ivec2"
        self.viewer.bindings['an_ivec2']['default'] = [1, 2]
        self.viewer.setUniforms()
        self.viewer.uniformi.assert_called_once_with('an_ivec2', 1, 2)
        self.assertEqual(self.viewer.uniformf.call_count, 0)

    def test_ivec3_uniform(self):
        self.viewer.bindings['an_ivec3'] = {}
        self.viewer.bindings['an_ivec3']['type'] = "ivec3"
        self.viewer.bindings['an_ivec3']['default'] = [1, 2, 3]
        self.viewer.setUniforms()
        self.viewer.uniformi.assert_called_once_with('an_ivec3', 1, 2, 3)
        self.assertEqual(self.viewer.uniformf.call_count, 0)

    def test_ivec4_uniform(self):
        self.viewer.bindings['an_ivec4'] = {}
        self.viewer.bindings['an_ivec4']['type'] = "ivec4"
        self.viewer.bindings['an_ivec4']['default'] = [1, 2, 3, 4]
        self.viewer.setUniforms()
        self.viewer.uniformi.assert_called_once_with('an_ivec4', 1, 2, 3, 4)
        self.assertEqual(self.viewer.uniformf.call_count, 0)

    def test_bool_uniform(self):
        self.viewer.bindings['a_bool'] = {}
        self.viewer.bindings['a_bool']['type'] = "bool"
        self.viewer.bindings['a_bool']['default'] = True
        self.viewer.setUniforms()
        self.viewer.uniformi.assert_called_once_with('a_bool', True)
        self.assertEqual(self.viewer.uniformf.call_count, 0)

    def test_float_uniform(self):
        self.viewer.bindings['a_float'] = {}
        self.viewer.bindings['a_float']['type'] = "float"
        self.viewer.bindings['a_float']['default'] = 1.0
        self.viewer.setUniforms()
        self.assertEqual(self.viewer.uniformi.call_count, 0)
        self.viewer.uniformf.assert_called_once_with('a_float', 1.0)

    def test_float_array_uniform(self):
        self.viewer.bindings['a_float_array'] = {}
        self.viewer.bindings['a_float_array']['type'] = "float"
        self.viewer.bindings['a_float_array']['default'] = [1.0, 1.1, 1.2, 1.3, 1.4]
        self.viewer.setUniforms()
        self.assertEqual(self.viewer.uniformi.call_count, 0)
        self.viewer.uniformf.assert_called_once_with('a_float_array', 1.0, 1.1, 1.2, 1.3, 1.4)

    def test_vec2_uniform(self):
        self.viewer.bindings['a_vec2'] = {}
        self.viewer.bindings['a_vec2']['type'] = "vec2"
        self.viewer.bindings['a_vec2']['default'] = [1.0, 1.1]
        self.viewer.setUniforms()
        self.assertEqual(self.viewer.uniformi.call_count, 0)
        self.viewer.uniformf.assert_called_once_with('a_vec2', 1.0, 1.1)

    def test_vec3_uniform(self):
        self.viewer.bindings['a_vec3'] = {}
        self.viewer.bindings['a_vec3']['type'] = "vec3"
        self.viewer.bindings['a_vec3']['default'] = [1.0, 1.1, 1.2]
        self.viewer.setUniforms()
        self.assertEqual(self.viewer.uniformi.call_count, 0)
        self.viewer.uniformf.assert_called_once_with('a_vec3', 1.0, 1.1, 1.2)

    def test_vec4_uniform(self):
        self.viewer.bindings['a_vec4'] = {}
        self.viewer.bindings['a_vec4']['type'] = "vec4"
        self.viewer.bindings['a_vec4']['default'] = [1.0, 1.1, 1.2, 1.3]
        self.viewer.setUniforms()
        self.assertEqual(self.viewer.uniformi.call_count, 0)
        self.viewer.uniformf.assert_called_once_with('a_vec4', 1.0, 1.1, 1.2, 1.3)

class TestGetHtmlHelps(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")

    def test_no_bindings(self):
        results = list(self.viewer.getHtmlHelps())
        self.assertEqual(len(results), 0)

    def test_keys_bound(self):
        self.viewer.bindings['Bool'] = {}
        self.viewer.bindings['Bool']['toggle_key'] = key.W
        self.viewer.bindings['Scalar'] = {}
        self.viewer.bindings['Scalar']['inc_key'] = key.Q
        self.viewer.bindings['Scalar']['dec_key'] = key.A
        self.viewer.bindings['List'] = {}
        self.viewer.bindings['List']['shuffle_key'] = key.S        
        results = sorted(self.viewer.getHtmlHelps())
        self.assertEqual(results, ['<b>Q/A</b>:Scalar', '<b>S</b>:List', '<b>W</b>:Bool'])

class TestGetStatuses(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")

    def test_no_bindings(self):
        results = list(self.viewer.getStatuses())
        self.assertEqual(len(results), 0)

    def test_statuses_bound(self):
        self.viewer.bindings['Bool'] = {}
        self.viewer.bindings['Bool']['default'] = False
        self.viewer.bindings['Scalar'] = {}
        self.viewer.bindings['Scalar']['default'] = 10
        self.viewer.bindings['List'] = {}
        self.viewer.bindings['List']['default'] = [x for x in range(10)] 
        self.viewer.bindings['Nothing'] = {}
        results = sorted(self.viewer.getStatuses())
        self.assertEqual(results, ['<b>Bool</b>=False', '<b>List</b>=[0,1,2,...,9]', '<b>Nothing</b>=None', '<b>Scalar</b>=10'])

class TestBindMostObviousMouseControls(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")

    def test_no_controls_to_bind(self):
        self.viewer.bindMostObviousMouseControls()
        self.assertFalse(getattr(self.viewer, 'mouseX', None))
        self.assertFalse(getattr(self.viewer, 'mouseY', None))
        self.assertFalse(getattr(self.viewer, 'mouseScroll', None))

    def test_controls_bound(self):
        self.viewer.bindings['x'] = "mock_x"
        self.viewer.bindings['y'] = "mock_y"
        self.viewer.bindings['zoom'] = "mock_zoom"
        self.viewer.bindMostObviousMouseControls()
        self.assertEqual(getattr(self.viewer, 'mouseX'), "mock_x")
        self.assertEqual(getattr(self.viewer, 'mouseY'), "mock_y")
        self.assertEqual(getattr(self.viewer, 'mouseScroll'), "mock_zoom")

class TestMouseDrag(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")

    def test_no_zoom_bound(self):
        self.viewer.mouseX = {}
        self.viewer.mouseX['default'] = -10
        self.viewer.mouseY = {}
        self.viewer.mouseY['default'] = 0
        self.viewer.mouseDrag(10, -20)
        self.assertEqual(self.viewer.mouseX['default'], -20)
        self.assertEqual(self.viewer.mouseY['default'], 20)

    def test_zoom_bound(self):
        self.viewer.mouseScroll = {}
        self.viewer.mouseScroll['default'] = 10
        self.viewer.mouseX = {}
        self.viewer.mouseX['default'] = -10
        self.viewer.mouseY = {}
        self.viewer.mouseY['default'] = 0
        self.viewer.mouseDrag(1, -2)
        self.assertEqual(self.viewer.mouseX['default'], -20)
        self.assertEqual(self.viewer.mouseY['default'], 20)
    
class TestMouseScrollY(BaseCase):

    def setUp(self):
        self.viewer = TextureShader("blank/blank_shader")

    def test_no_zoom_bound(self):
        self.viewer.mouseScrollY(2)
        self.assertFalse(getattr(self.viewer, 'mouseScroll', None))

    def test_zoom_bound(self):
        self.viewer.mouseScroll = {}
        self.viewer.mouseScroll['default'] = 10
        self.viewer.mouseScroll['diff'] = 5
        self.viewer.mouseScrollY(-2)
        self.assertEqual(self.viewer.mouseScroll['default'], 20)

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
        # print(binding['default'])

if __name__ == '__main__':
    unittest.main()