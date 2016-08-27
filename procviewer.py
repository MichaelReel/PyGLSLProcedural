from __future__ import print_function
from shader import Shader
import io, os, json, re
from pyglet.window import key

class TextureShader(Shader):
    def __init__(self, shader_path):
    
        vertexShader = ' '.join(io.open('%s.v.glsl' % shader_path))
        fragmentShader = ' '.join(io.open('%s.f.glsl' % shader_path))
        
        # Load and update key bindings
        self.loadKeyBindings("{}.bindings.json".format(shader_path))
        self.checkKeyBindingsFromShaderUniforms(vertexShader)
        self.checkKeyBindingsFromShaderUniforms(fragmentShader)
        self.saveKeyBindings("{}.bindings.json".format(shader_path))

        super(TextureShader, self).__init__(vertexShader, fragmentShader)
    
    def loadKeyBindings(self, keyBindingsFile):
        ''' Load pre-saved key bindings if they exist '''
        if (os.path.isfile(keyBindingsFile)):
            with open(keyBindingsFile, "rb") as jsonFile:
                self.bindings = json.load(jsonFile)
        else:
            self.bindings = {}
        self.setupUsedKeys()

    def saveKeyBindings(self, keyBindingsFiles):
        ''' Save the latest bindings to file '''
        with open(keyBindingsFiles, "wb") as jsonFile:
            json.dump(self.bindings, jsonFile, sort_keys=True, separators=(',\n', ': '))

    def checkKeyBindingsFromShaderUniforms(self, shader):
        ''' Parse the shader and look for unbound uniforms to bind '''
        # Find the single values
        pattern = re.compile(r'\n(?:\s*)uniform(?:\s*)(?P<type>\w+)(?:\s*)(?P<name>\w+)(?:\s*);')
        for uniform in re.finditer(pattern, shader):
            self.checkShaderBinding(uniform.group('name'), uniform.group('type'))

    def checkShaderBinding(self, name, type):
        print ("{} {}".format(type, name))
        # Check for name in the bindings, and create or update where necessary
        if self.bindings.has_key(name):
            # If the type is the same, then leave it unchanged
            if self.bindings[name]['type'] != type:
                # otherwise, clear and redo
                del self.bindings[name]
                self.createBinding(name, type)
        else:
            # Add (makeup) new keybinding
            self.createBinding(name, type)
        
    def createBinding(self, name, type):
        self.bindings[name] = {}
        self.bindings[name]['type'] = type
        {   'int'   : self.setupInt,
            'float' : self.setupFloat,
            'bool'  : self.setupBool,
            'vec2'  : self.setupVec2,
            'vec3'  : self.setupVec3,
            'vec4'  : self.setupVec4,
        }[type](self.bindings[name])
        print ("Binding added for uniform '{}', check the json file and update defaults.".format(name))
    
    def setupInt(self, bindingDict):
        '''Insert a default value and keys for incrementing and decrementing'''
        bindingDict['default'] = 0
        self.getUnboundKey(bindingDict, 'inc_key')
        self.getUnboundKey(bindingDict, 'dec_key')
        bindingDict['diff'] = 1

    def setupFloat(self, bindingDict):
        '''Insert a default value and keys for incrementing and decrementing'''
        bindingDict['default'] = 0.0
        self.getUnboundKey(bindingDict, 'inc_key')
        self.getUnboundKey(bindingDict, 'dec_key')
        bindingDict['diff'] = 1.0

    def setupBool(self, bindingDict):
        '''Insert a default value and key for toggling'''
        bindingDict['default'] = False
        self.getUnboundKey(bindingDict, 'toggle_key')
    
    def setupVec2(self, bindingDict):
        '''Insert a default value'''
        bindingDict['default'] = (0.0, 0.0)
        
    def setupVec3(self, bindingDict):
        '''Insert a default value'''
        bindingDict['default'] = (0.0, 0.0, 0.0)
        
    def setupVec4(self, bindingDict):
        '''Insert a default value'''
        bindingDict['default'] = (0.0, 0.0, 0.0, 0.0)
    
    def setupUsedKeys(self):
        self.usedKeys = {}
        for binding in self.bindings:
            self.checkKeyBinding(self.bindings[binding], 'inc_key')
            self.checkKeyBinding(self.bindings[binding], 'dec_key')
            self.checkKeyBinding(self.bindings[binding], 'toggle_key')

    def checkKeyBinding(self, binding, keyUse):
        if binding.has_key(keyUse):
            self.usedKeys[binding[keyUse]] = binding

    def getUnboundKey(self, binding, keyUse):
        # Find the next key name that isn't already used
        for possibleKey in preferredKeyOrder():
            if not self.usedKeys.has_key(possibleKey):
                binding[keyUse] = possibleKey
                self.usedKeys[possibleKey] = binding
                break

    def bindingTrigger(self, symbol):
        if not self.usedKeys.has_key(symbol):
            return
    
        binding = self.usedKeys[symbol]
        if binding.has_key('toggle_key') and binding['toggle_key'] == symbol:
            binding['default'] = not binding['default']
            return
        if binding.has_key('inc_key') and binding['inc_key'] == symbol:
            binding['default'] += binding['diff']
            return
        if binding.has_key('dec_key') and binding['dec_key'] == symbol:
            binding['default'] -= binding['diff']
            return

    def setUniforms(self):
        for name in self.bindings:
            type = self.bindings[name]['type']
            value = self.bindings[name]['default']
            {
                'int'   : self.uniformi,
                'bool'  : self.uniformi,
                'float' : self.uniformf,
                'vec2'  : self.uniformf,
                'vec3'  : self.uniformf,
                'vec4'  : self.uniformf,
            }[type](name, *[value])

    def getHtmlHelps(self):
        for name in self.bindings:
            binding = self.bindings[name]
            keyCode = None
            if binding.has_key('toggle_key'):
                keyCode = key.symbol_string(binding['toggle_key'])
            if binding.has_key('inc_key'):
                keyCode = key.symbol_string(binding['inc_key']) + "/" + key.symbol_string(binding['dec_key'])
            yield "<b>{}</b>:{}".format(keyCode, name)

def preferredKeyOrder():
    # Particular keys prioritised for use
    for letter in ["Q","A","W","S","E","D","R","F","T","G","Y","H","U",
                   "J","I","K","O","L","P","Z","X","C","V","B","N","M",
                   "_1","_2","_3","_4","_5","_6","_7","_8","_9","_0"]:
        yield getattr(key, letter)
    # The rest of the keys in whatever order
    for other in key._key_names:
        yield other