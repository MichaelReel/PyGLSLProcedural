# PyGLSLProcedural
Procedurally generated texture using glsl to perform the work.
Written in python using pyglet.

This project is for conceptual purposes only. 

This code contains [Ken Perlins Noise Reference Implementation]
(http://mrl.nyu.edu/~perlin/noise/), ported to GLSL. Also, contained in this code 
is a slightly modified pyglet Shader class as written by [Tristam Macdonald]
(https://swiftcoder.wordpress.com/2008/12/19/simple-glsl-wrapper-for-pyglet/).

Copyrights belong to their respective owners and licences apply accordingly.

Whatever code does not fall under other licences can be assumed to be be MIT licence.

This project requires pyglet to be available, it can be installed using pip:

> pip install pyglet

`run_procviewer.py` is the main application.

## Executing a shader

Currently, the shader being loaded by the `run_procviewer` script is selected by 
the call to TextureWindow near the bottom of the python file. Uncommenting one 
of the alternative lines and commenting out the current one will change the 
GLSL script being loaded.

## Run time behaviour

When `run_procviewer` is executed, the TextureWindow call loads a GLSL script and
attempts to parse it for uses of the uniform keyword. For `uniform` it finds it will
attempt to apply key bindings. If the script contains x and y uniforms, then they 
will also be bound to the mouse. If the script contains a zoom uniform, then that
will be bound to the mouse wheel. All other keys bound will be displayed listed
from the top left corner of the draw window with the keys mapped for incrementing
and decrementing the uniform value.

## Saved keybindings

The keybindings, once created, will be saved to a json file in the same location
as the shader script. Editing this file will allow the user to set default values
as well as the incrementing and decrementing differences the key bindings cause.
To recreate the keybindings file, just delete it and call `run_procviewer` to 
generate a new one.