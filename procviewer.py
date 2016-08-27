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
        self.bindMostObviousMouseControls()

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
        # build a regex
        s    = r'(?:\s*)'                             # optional white space
        type = r'(?P<type>\w+)'                       # var type
        name = r'(?P<name>\w+)'                       # var name
        defv = r'(?P<default>-?[0-9]+(?:.[0-9]+)?)?'  # optional default value
        diff = r'(?P<diff>-?[0-9]+(?:.[0-9]+)?)?'     # optional diff value

        pattern = re.compile(r'uniform' + s + type + s + name + s + r'=?' + s + defv + s + r';' + r'(?:'+ s + r'(?://)*' + s + r'diff' + s + diff + r')?')
        found = False
        for uniform in re.finditer(pattern, shader):
            self.checkShaderBinding(uniform)
            found = True

        if not found:
            print('No uniforms found in "{}"'.format(shader))

    def checkShaderBinding(self, uniform):
        name = uniform.group('name')
        type = uniform.group('type')
        print ("{} {}".format(type, name))
        # Check for name in the bindings, and create or update where necessary
        if self.bindings.has_key(name):
            # If the type is the same, then leave it unchanged
            if self.bindings[name]['type'] != type:
                # otherwise, clear and redo
                del self.bindings[name]
                self.createBinding(uniform)
        else:
            # Add (makeup) new keybinding
            self.createBinding(uniform)
        
    def createBinding(self, uniform):
        name = uniform.group('name')
        type = uniform.group('type')
        self.bindings[name] = {}
        self.bindings[name]['type'] = type
        {   'int'   : self.setupInt,
            'float' : self.setupFloat,
            'bool'  : self.setupBool,
            'vec2'  : self.setupVec2,
            'vec3'  : self.setupVec3,
            'vec4'  : self.setupVec4,
        }[type](self.bindings[name], uniform)
        print ("Binding added for uniform '{}', check the json file and update defaults.".format(name))
    
    def setupInt(self, bindingDict, uniform):
        '''Insert a default value and keys for incrementing and decrementing'''
        self.getUnboundKey(bindingDict, 'inc_key')
        self.getUnboundKey(bindingDict, 'dec_key')
        bindingDict['default'] = 0
        bindingDict['diff'] = 1
        if uniform.group('default') != None:
            bindingDict['default'] = int(uniform.group('default'))
        if uniform.group('diff') != None:
            bindingDict['diff'] = int(uniform.group('diff'))

    def setupFloat(self, bindingDict, uniform):
        '''Insert a default value and keys for incrementing and decrementing'''
        self.getUnboundKey(bindingDict, 'inc_key')
        self.getUnboundKey(bindingDict, 'dec_key')
        bindingDict['default'] = 0.0
        bindingDict['diff'] = 1.0
        if uniform.group('default') != None:
            bindingDict['default'] = float(uniform.group('default'))
        if uniform.group('diff') != None:
            bindingDict['diff'] = float(uniform.group('diff'))

    def setupBool(self, bindingDict, uniform):
        '''Insert a default value and key for toggling'''
        self.getUnboundKey(bindingDict, 'toggle_key')
        bindingDict['default'] = False
        if uniform.group('default') != None:
            bindingDict['default'] = bool(uniform.group('default'))
    
    def setupVec2(self, bindingDict, uniform):
        '''Insert a default value'''
        # Currently Untested. Need to parse the default values correctly for this
        bindingDict['default'] = (0.0, 0.0)
        
    def setupVec3(self, bindingDict, uniform):
        '''Insert a default value'''
        # Currently Untested. Need to parse the default values correctly for this
        bindingDict['default'] = (0.0, 0.0, 0.0)
        
    def setupVec4(self, bindingDict, uniform):
        '''Insert a default value'''
        # Currently Untested. Need to parse the default values correctly for this
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

    def bindMostObviousMouseControls(self):
        if self.bindings.has_key('x'):
            self.mouseX = self.bindings['x']
        if self.bindings.has_key('y'):
            self.mouseY = self.bindings['y']
        if self.bindings.has_key('zoom'):
            self.mouseScroll = self.bindings['zoom']

    def mouseDrag(self, dx, dy):
        zoom = 1
        if hasattr(self, 'mouseScroll'):
            zoom = self.mouseScroll['default']
        if hasattr(self, 'mouseX'):
            self.mouseX['default'] -= dx * zoom # * self.mouseX['diff']
        if hasattr(self, 'mouseY'):
            self.mouseY['default'] -= dy * zoom # * self.mouseY['diff']

    def mouseScrollY(self, scroll_y):
        if hasattr(self, 'mouseScroll'):
            self.mouseScroll['default'] -= scroll_y * self.mouseScroll['diff']

def preferredKeyOrder():
    '''Not sure how to do this without constantly launching GeneratorExits'''
    # Particular keys prioritised for use
    for letter in ["Q","A","W","S","E","D","R","F","T","G","Y","H","U",
                    "J","I","K","O","L","P","Z","X","C","V","B","N","M",
                    "_1","_2","_3","_4","_5","_6","_7","_8","_9","_0"]:
        yield getattr(key, letter)
    # The rest of the keys in whatever order
    for other in key._key_names:
        yield other
