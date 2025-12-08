from pyglm import glm
from .object import *
import OpenGL.GL as gl

class MeshObject(Object):
    def __init__(self, mesh, material, transform=glm.mat4(1.0), draw_mode=gl.GL_TRIANGLES):
        super().__init__(transform)
        self.mesh = mesh
        self.material = material
        self.visible = True
        self.draw_mode = draw_mode

    def draw(self, camera, lights):
        if self.visible == False:
            return
        
        self.material.set_uniforms(False, self, camera, lights)

        if self.mesh.VAO is None:
            self.mesh.createGeometry()
            self.mesh.createBuffers()

        if self.draw_mode == gl.GL_POINTS:
            gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

        gl.glBindVertexArray(self.mesh.VAO)

        if self.mesh.IndexBO is not None and self.draw_mode != gl.GL_POINTS:
             # If we have indices and we are NOT in point mode, use DrawElements.
             # If we are in point mode, we usually want to draw all vertices as points, 
             # but we could also use DrawElements if we wanted points at indices.
             # For Mikoshi style, we likely want every vertex to be a point.
             # However, if the mesh has indices, DrawElements is safer to respect the mesh structure.
             # But usually point clouds ignore connectivity.
             # Let's stick to DrawElements if indices exist, it works for GL_POINTS too.
            gl.glDrawElements(self.draw_mode, len(self.mesh.indices), gl.GL_UNSIGNED_INT, None)
        else:
            gl.glDrawArrays(self.draw_mode, 0, len(self.mesh.vertices))

        gl.glBindVertexArray(0)
        
        if self.draw_mode == gl.GL_POINTS:
            gl.glDisable(gl.GL_PROGRAM_POINT_SIZE)
