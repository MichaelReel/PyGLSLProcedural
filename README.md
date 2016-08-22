# PyGLSLProcedural
Procedurally generated texture using glsl to perform the work. Written in python using pyglet.

This project is for conceptual purposes only. 

This code contains [Ken Perlins Noise Reference Implementation](http://mrl.nyu.edu/~perlin/noise/), ported to GLSL.
Also, contained in this code is a slightly modified pyglet Shader class as written by [Tristam Macdonald](https://swiftcoder.wordpress.com/2008/12/19/simple-glsl-wrapper-for-pyglet/).

Copyrights belong to their respective owners and licences apply accordingly.

Whatever code does not fall under other licences can be assumed to be be MIT licence.

This project requires pyglet to be available, it can be installed using pip:

> pip install pyglet

`run_procedural_shader.py` is the main application. 
Use the mouse to drag around and the mouse wheel to zoom.
E and D control the z coord.
T and G control the number of octives used in sum smoothing.
Y and H control the change in period value between octives.

`shader.py` is a slightly modified copy of Tristam Macdonald's GLSL wrapper.

`proc_shader.v.glsl` is a basic empty vertex shader.

`proc_shader.f.glsl` is a fragment shader that mimics the perlin reference algorithm.
