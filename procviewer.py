''' This contains the classes and functions required to parse a shader file
    and generate key bindings to provide some key and mouse controls '''

from __future__ import print_function
import io
import os
import json
import re
from random import Random
from pyglet.window import key
from shader import Shader

class ShaderController(Shader):
    ''' This class provides a control binding wrapper to a GLSL shader'''

    def __init__(self, shader_path):
        # Load shader code
        vspath = '%s.v.glsl' % shader_path
        fspath = '%s.f.glsl' % shader_path
        with io.open(vspath) as vstrm, io.open(fspath) as fstrm:
            vertexshader = ' '.join(vstrm)
            fragmentshader = ' '.join(fstrm)

        # Load and update key bindings
        self.used_keys = {}
        self.load_key_bindings("{}.bindings.json".format(shader_path))
        self.parse_bindings_from_uniforms(vertexshader)
        self.parse_bindings_from_uniforms(fragmentshader)
        self.save_key_bindings("{}.bindings.json".format(shader_path))
        self.bind_mouse_controls()

        # Create the shader
        super(ShaderController, self).__init__(vertexshader, fragmentshader)

    def load_key_bindings(self, file):
        ''' Load pre-saved key bindings if they exist '''
        if os.path.isfile(file):
            with open(file, "r") as json_file:
                self.bindings = json.load(json_file)
        else:
            self.bindings = {}
        self.setup_used_keys()

    def save_key_bindings(self, key_bindings_files):
        ''' Save the latest bindings to file '''
        with open(key_bindings_files, "w") as json_file:
            json.dump(self.bindings, json_file)

    def parse_bindings_from_uniforms(self, shader):
        ''' Parse the shader and look for unbound uniforms to bind '''
        found = False

        found = found | self.parse_numeric_bindings(shader)
        found = found | self.parse_boolean_bindings(shader)
        found = found | self.parse_array_bindings(shader)

        return found

    def parse_numeric_bindings(self, shader):
        '''Parse the shader and for each scalar uniform found, try to create a keybinding'''
        found = False

        # build a regex for finding int and float lines:
        ows = r'(?:\s*)'                              # optional white space
        mws = r'(?:\s+)'                              # manditory white space
        typ = r'(?P<type>(?:int|float))'              # var type
        name = r'(?P<name>\w+)'                       # var name
        defv = r'(?P<default>-?[0-9]+(?:.[0-9]+)?)?'  # optional default value
        diff = r'(?P<diff>-?[0-9]+(?:.[0-9]+)?)?'     # optional diff value

        pattern = re.compile(r'uniform' + mws + typ + mws + name + ows + r'=?' +\
                             ows + defv + ows + r';' +\
                             r'(?:'+ ows + r'(?://)*' + ows + r'diff' + mws + diff + r')?')
        for uniform in re.finditer(pattern, shader):
            self.update_binding(uniform)
            found = True

        return found

    def parse_boolean_bindings(self, shader):
        '''Parse the shader and for each boolean uniform found, try to create a keybinding'''
        found = False

        # build a regex for finding int and float lines:
        ows = r'(?:\s*)'                              # optional white space
        mws = r'(?:\s+)'                              # manditory white space
        typ = r'(?P<type>bool)'                       # var type
        name = r'(?P<name>\w+)'                       # var name
        defv = r'(?P<default>\w+)?'                   # optional default value

        pattern = re.compile(r'uniform' + mws + typ + mws + name + ows + r'=?' +\
                             ows + defv + ows + r';')
        for uniform in re.finditer(pattern, shader):
            self.update_binding(uniform)
            found = True

        return found

    def parse_array_bindings(self, shader):
        '''Parse the shader and for each array uniform found, try to create a keybinding'''
        found = False

        # build a regex for finding int and float lines:
        ows = r'(?:\s*)'                                              # optional white space
        mws = r'(?:\s+)'                                              # manditory white space
        com = r'(?://+)' + ows                                        # comment
        typ = r'uniform' + mws + r'(?P<type>(?:int|float))' + mws     # var type
        name = r'(?P<name>\w+)' + ows                                 # var name
        size = r'\[(?P<size>[0-9]+)\]' + ows                          # array size
        seed = r'(?:seed' + ows + r'(?P<seed>\w+)' + ows + r')?'      # optional string seed value
        perm_size = r'permutation' + ows + r'(?P<perm>[0-9]+)' + ows  # optional permutation size
        line_size = com + r'linear' + ows + r'(?P<line>[0-9]+)' + ows # optional linear size value

        regex = typ + name + size + r';' + ows +\
                r'(?:'+ com + perm_size + seed + r')?' + r'(?:' + line_size + r')?'
        pattern = re.compile(regex)

        for uniform in re.finditer(pattern, shader):
            self.update_binding(uniform)
            found = True

        return found

    def update_binding(self, uniform):
        '''Update existing bindings or create new bindings for unknown uniforms'''
        var_name = uniform.group('name')
        var_type = uniform.group('type')

        # Check for name in the bindings, and create or update where necessary
        if var_name in self.bindings:
            # If the type is the same, then leave it unchanged
            if self.bindings[var_name]['type'] != var_type:
                # otherwise, clear and redo
                del self.bindings[var_name]
                self.create_binding(uniform)
        else:
            # Add (makeup) new keybinding
            self.create_binding(uniform)

    def create_binding(self, uniform):
        '''Create a key binding for the given uniform'''

        # if size is a group, this is from an array check
        if 'size' in uniform.groupdict().keys():
            self.create_array_binding(uniform)
            return

        # if size isn't set, it's a primitive
        var_name = uniform.group('name')
        var_type = uniform.group('type')
        self.bindings[var_name] = {}
        self.bindings[var_name]['type'] = var_type
        {'int'   : self.init_int_binding,
         'float' : self.init_float_binding,
         'bool'  : self.init_bool_binding,
         'vec2'  : self.init_vec2_binding,
         'vec3'  : self.init_vec3_binding,
         'vec4'  : self.init_vec4_binding,
        }[var_type](self.bindings[var_name], uniform)
        print("Binding added for uniform '{}', check the json file and update defaults."
              .format(var_name))

    def create_array_binding(self, uniform):
        '''Create new binding for modifying arrays'''
        var_name = uniform.group('name')
        var_type = uniform.group('type')

        self.bindings[var_name] = {}
        self.bindings[var_name]['type'] = var_type
        {'int'   : self.init_int_array_binding,
         'float' : self.init_float_array_binding,
         'bool'  : self.init_bool_array_binding,
         'vec2'  : self.init_vec2_array_binding,
         'vec3'  : self.init_vec3_array_binding,
         'vec4'  : self.init_vec4_array_binding,
        }[var_type](self.bindings[var_name], uniform)
        print("Binding added for uniform '{}', check the json file and update defaults."
              .format(var_name))

    def init_int_binding(self, binding_dict, uniform):
        '''Insert a default value and keys for incrementing and decrementing'''
        self.get_unbound_key(binding_dict, 'inc_key')
        self.get_unbound_key(binding_dict, 'dec_key')
        binding_dict['default'] = 0
        binding_dict['diff'] = 1
        if uniform.group('default') != None:
            binding_dict['default'] = int(uniform.group('default'))
        if uniform.group('diff') != None:
            binding_dict['diff'] = int(uniform.group('diff'))

    def init_float_binding(self, binding_dict, uniform):
        '''Insert a default value and keys for incrementing and decrementing'''
        self.get_unbound_key(binding_dict, 'inc_key')
        self.get_unbound_key(binding_dict, 'dec_key')
        binding_dict['default'] = 0.0
        binding_dict['diff'] = 1.0
        if uniform.group('default') != None:
            binding_dict['default'] = float(uniform.group('default'))
        if uniform.group('diff') != None:
            binding_dict['diff'] = float(uniform.group('diff'))

    def init_bool_binding(self, binding_dict, uniform):
        '''Insert a default value and key for toggling'''
        self.get_unbound_key(binding_dict, 'toggle_key')
        binding_dict['default'] = False
        if uniform.group('default') != None:
            binding_dict['default'] = bool(uniform.group('default'))

    def init_vec2_binding(self, binding_dict, uniform):
        '''Insert a default value'''
        # Currently Untested. Need to parse the default values correctly for this
        binding_dict['default'] = (0.0, 0.0)

    def init_vec3_binding(self, binding_dict, uniform):
        '''Insert a default value'''
        # Currently Untested. Need to parse the default values correctly for this
        binding_dict['default'] = (0.0, 0.0, 0.0)

    def init_vec4_binding(self, binding_dict, uniform):
        '''Insert a default value'''
        # Currently Untested. Need to parse the default values correctly for this
        binding_dict['default'] = (0.0, 0.0, 0.0, 0.0)

    def init_int_array_binding(self, binding_dict, uniform):
        '''Insert a default array and key for shuffling'''
        self.get_unbound_key(binding_dict, 'shuffle_key')
        size = int(uniform.group('size'))

        binding_dict['default'] = [x for x in range(size)]

        if uniform.group('line') != None:
            line_size = int(uniform.group('line'))
            binding_dict['loop'] = line_size
            binding_dict['default'] = []
            for i in range(size):
                binding_dict['default'].append(i % line_size)
        elif uniform.group('perm') != None:
            perm_size = int(uniform.group('perm'))
            binding_dict['loop'] = perm_size
            seed = 1
            if uniform.group('seed') != None:
                seed = int(uniform.group('seed'))
            binding_dict['seed'] = seed
            update_permutation(binding_dict)

    def init_float_array_binding(self, binding_dict, uniform):
        '''Insert a default float array (To Be Implemented)'''
        raise NotImplementedError

    def init_bool_array_binding(self, binding_dict, uniform):
        '''Insert a default boolean array (To Be Implemented)'''
        raise NotImplementedError

    def init_vec2_array_binding(self, binding_dict, uniform):
        '''Insert a default vec2 array (To Be Implemented)'''
        raise NotImplementedError

    def init_vec3_array_binding(self, binding_dict, uniform):
        '''Insert a default vec3 (To Be Implemented)'''
        raise NotImplementedError

    def init_vec4_array_binding(self, binding_dict, uniform):
        '''Insert a default vec4 array (To Be Implemented)'''
        raise NotImplementedError

    def setup_used_keys(self):
        '''Use existing bindings to setup key mappings'''
        for binding in self.bindings:
            self.check_key_binding(self.bindings[binding], 'inc_key')
            self.check_key_binding(self.bindings[binding], 'dec_key')
            self.check_key_binding(self.bindings[binding], 'toggle_key')

    def check_key_binding(self, binding, key_use):
        '''Set the key to perform bound operation'''
        if key_use in binding:
            self.used_keys[binding[key_use]] = binding

    def get_unbound_key(self, binding, key_use):
        ''' Find the next preferred key that isn't already used'''
        for possible_key in preferred_key_order():
            if possible_key not in self.used_keys:
                binding[key_use] = possible_key
                self.used_keys[possible_key] = binding
                break

    def binding_trigger(self, symbol):
        '''
        Return True if trigger succeeded,
        False if not bound,
        ValueError if key is used but not bound
        '''
        if symbol not in self.used_keys:
            return False
        binding = self.used_keys[symbol]
        if 'toggle_key' in binding and binding['toggle_key'] == symbol:
            binding['default'] = not binding['default']
            return True
        if 'inc_key' in binding and binding['inc_key'] == symbol:
            binding['default'] += binding['diff']
            return True
        if 'dec_key'in binding and binding['dec_key'] == symbol:
            binding['default'] -= binding['diff']
            return True
        if 'shuffle_key' in binding and binding['shuffle_key'] == symbol:
            update_permutation(binding)
            return True
        # Key was bound, but not to any action
        raise ValueError("symbol {} used but not bound to an action".format(symbol))

    def set_uniforms(self):
        '''Define the uniforms we're going to use in the shader'''
        for name in self.bindings:
            var_type = self.bindings[name]['type']
            var_default = self.bindings[name]['default']
            if not isinstance(var_default, list):
                # Wrap scalars
                var_default = [var_default]
            # Switch on type
            {
                'int'   : self.uniformi,
                'bool'  : self.uniformi,
                'float' : self.uniformf,
                'vec2'  : self.uniformf,
                'vec3'  : self.uniformf,
                'vec4'  : self.uniformf,
                'ivec2' : self.uniformi,
                'ivec3' : self.uniformi,
                'ivec4' : self.uniformi,
            }[var_type](name, *var_default)

    def get_html_help(self):
        '''Return html description of key bindings'''
        for name in self.bindings:
            binding = self.bindings[name]
            key_code = None
            if 'toggle_key' in binding:
                key_code = key.symbol_string(binding['toggle_key'])
            if 'inc_key' in binding:
                key_code = key.symbol_string(binding['inc_key']) +\
                           "/" + key.symbol_string(binding['dec_key'])
            if 'shuffle_key' in binding:
                key_code = key.symbol_string(binding['shuffle_key'])
            yield "<b>{}</b>:{}".format(key_code, name)

    def get_statuses(self):
        '''Return a html description of the current editable values'''
        for name in self.bindings:
            binding = self.bindings[name]
            status = None
            if 'default' in binding:
                status = binding['default']
            if isinstance(status, list):
                status = "[{},{},{},...,{}]".format(status[0], status[1], status[2], status[-1])
            yield "<b>{}</b>={}".format(name, status)

    def bind_mouse_controls(self):
        '''Bind any x, y and zoom uniforms to the mouse'''
        if 'x' in self.bindings:
            self.mouse_x = self.bindings['x']
        if 'y' in self.bindings:
            self.mouse_y = self.bindings['y']
        if 'zoom' in self.bindings:
            self.mouse_scroll = self.bindings['zoom']

    def mouse_drag(self, diff_x, diff_y):
        '''Perform mouse drag action and update uniforms appropriately'''
        zoom = 1
        if getattr(self, 'mouse_scroll', None):
            zoom = self.mouse_scroll['default']
        if getattr(self, 'mouse_x', None):
            self.mouse_x['default'] -= diff_x * zoom
        if getattr(self, 'mouse_y', None):
            self.mouse_y['default'] -= diff_y * zoom

    def mouse_scroll_y(self, scroll_y):
        '''Perform mouse wheel action and update uniforms appropriately'''
        if getattr(self, 'mouse_scroll', None):
            self.mouse_scroll['default'] -= scroll_y * self.mouse_scroll['diff']

def preferred_key_order():
    '''
    Return a list of keys in the the preconfigured 'best' order
    for use as key bindings
    '''
    # Remove the particular keys prioritised for use
    priority_keys = ["Q", "A", "W", "S", "E", "D", "R", "F", "T", "G", "Y", "H", "U",
                     "J", "I", "K", "O", "L", "P", "Z", "X", "C", "V", "B", "N", "M",
                     "_1", "_2", "_3", "_4", "_5", "_6", "_7", "_8", "_9", "_0"]

    # clone the full set of key codes, removing the priority keys
    # from the key list and placing them at the front
    non_priority_keys = list(get_all_key_names() - set(priority_keys))
    return [getattr(key, letter) for letter in priority_keys] + non_priority_keys


def get_all_key_names():
    '''Return the set of all key names'''
    # pylint: disable=I0011,W0212
    return set(key._key_names)

def update_permutation(binding):
    '''
    This takes an list of values in binding['default'] and shuffles them.
    The value in binding['loop'] will cause the reshuffle to only take the
    first 'loop' values in the list, shuffle them, then reproduce the same
    shuffled values (in the same order) over the rest of the list.
    The value in binding['seed'] will determine the random seed used for shuffling.
    '''
    perm_size = binding['loop']
    seed = binding['seed']
    size = len(binding['default'])
    rand = Random(seed)
    perm = binding['default'][:perm_size]
    rand.shuffle(perm)
    binding['default'] = []
    for i in range(size):
        binding['default'].append(perm[i % perm_size])
