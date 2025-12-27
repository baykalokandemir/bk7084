import numpy as np
import glfw
import OpenGL.GL as gl

import sys
import os

from .window import *
from .shapes import *
from .shapes import *
from .light  import *
from .materials.shaders import createShader
import ctypes

class GLRenderer ():
    """
    Sets up a renderer with OpenGL
    The Renderer receives a Window and includes the necessary building blocks: camera and shapes array
    and a simple draw function
    """


    def __init__ (self, window, camera):
        """
        Constructor
        Receives a Window 
        The Renderer receives an OpenGLWindow and creates a default camera (Trackball)
        """
        self.glwindow = window
    
        # set the camera for the callbacks
        self.glwindow.camera = camera

        self.objects = []

        # light sources
        self.lights = []
        self.clear_color = [0.0, 0.0, 0.0, 1.0] # Default to black

    def setCamera (self, camera):
        self.glwindow.camera = camera

    def delete (self):
        gl.glDeleteFramebuffers(1, [self.fbo])
        gl.glDeleteTextures([self.texture_color_buffer])
        gl.glDeleteRenderbuffers(1, [self.rbo])
        return
    
    def init_post_process(self, width, height):
        # 1. Framebuffer
        self.fbo = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
        
        # 2. Texture Attachment (Color)
        self.texture_color_buffer = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_color_buffer)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.texture_color_buffer, 0)
        
        # 3. Renderbuffer Attachment (Depth/Stencil)
        self.rbo = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.rbo)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, width, height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT, gl.GL_RENDERBUFFER, self.rbo)
        
        # Check completeness
        if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
            print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!", file=sys.stderr)
            
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        
        # 4. Post-Process Shader
        shader_dir = os.path.join(os.path.dirname(__file__), 'shaders')
        self.post_shader = createShader(
            os.path.join(shader_dir, "post_process.vert"),
            os.path.join(shader_dir, "post_process.frag")
        )
        self.use_post_process = False
        self.aberration_strength = 0.005
        
        # 5. Screen Quad VAO
        self.setup_quad()

    def resize_post_process(self, width, height):
        if hasattr(self, 'texture_color_buffer'):
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_color_buffer)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)
            
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.rbo)
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, width, height)

    def setup_quad(self):
        # Fullscreen quad coordinates
        quad_vertices = np.array([
            # pos        # tex
            -1.0,  1.0,  0.0, 1.0,
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,

            -1.0,  1.0,  0.0, 1.0,
             1.0, -1.0,  1.0, 0.0,
             1.0,  1.0,  1.0, 1.0
        ], dtype=np.float32)
        
        self.quadVAO = gl.glGenVertexArrays(1)
        self.quadVBO = gl.glGenBuffers(1)
        
        gl.glBindVertexArray(self.quadVAO)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.quadVBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, gl.GL_STATIC_DRAW)
        
        # Position
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        # TexCoords
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        
        gl.glBindVertexArray(0)
    
    def addLight (self, light):
        self.lights.append(light)

    def addObject(self, obj):
        if not hasattr(obj, "draw") or not callable(getattr(obj, "draw")):
            print(f"[Renderer] Error: object {obj} has no callable draw() method", file=sys.stderr)
            return
        self.objects.append(obj)

    def render (self):
        # 1. Bind Framebuffer if enabled
        if hasattr(self, 'use_post_process') and self.use_post_process:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
        else:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        gl.glClearColor(*self.clear_color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # 2. Draw Scene
        for o in self.objects:
            o.draw(self.glwindow.camera, self.lights)
            
        # 3. Post-Process Pass
        if hasattr(self, 'use_post_process') and self.use_post_process:
            # Bind Default Framebuffer (Screen)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            gl.glDisable(gl.GL_DEPTH_TEST) # Disable depth test so quad is always drawn
            gl.glClearColor(1.0, 1.0, 1.0, 1.0) 
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            
            gl.glUseProgram(self.post_shader)
            gl.glUniform1i(gl.glGetUniformLocation(self.post_shader, "screenTexture"), 0)
            gl.glUniform1f(gl.glGetUniformLocation(self.post_shader, "aberration_strength"), self.aberration_strength)
            
            gl.glBindVertexArray(self.quadVAO)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_color_buffer)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
            
        # if self.glwindow.camera.draw_camera:
            # print("fixme")
            # self.glwindow.camera.draw()
          
        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # glfw.swap_buffers(self.glwindow.window)
        # glfw.poll_events()

