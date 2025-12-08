import numpy as np
import os
import base64
from pygltflib import GLTF2
from .shapes.shape import Shape
from .objects.mesh_object import MeshObject
from pyglm import glm

def load_gltf(filepath, material=None):
    """
    Loads a glTF/GLB file and returns a list of MeshObjects.
    """
    gltf = GLTF2().load(filepath)
    objects = []
    
    # Helper to get data from accessor
    def get_data(accessor_index):
        accessor = gltf.accessors[accessor_index]
        buffer_view = gltf.bufferViews[accessor.bufferView]
        buffer = gltf.buffers[buffer_view.buffer]
        
        data = None
        
        # Handle buffer data source
        if buffer.uri:
            if buffer.uri.startswith("data:"):
                # Data URI
                header, encoded = buffer.uri.split(",", 1)
                data = base64.b64decode(encoded)
            else:
                # External file
                bin_path = os.path.join(os.path.dirname(filepath), buffer.uri)
                with open(bin_path, "rb") as f:
                    data = f.read()
        else:
            # GLB binary blob
            data = gltf.binary_blob()
            
        if data is None:
            return None
            
        # Calculate offset and length
        offset = (buffer_view.byteOffset or 0) + (accessor.byteOffset or 0)
        length = buffer_view.byteLength
        
        # Determine dtype and shape
        dtype = np.float32
        if accessor.componentType == 5120: dtype = np.int8
        elif accessor.componentType == 5121: dtype = np.uint8
        elif accessor.componentType == 5122: dtype = np.int16
        elif accessor.componentType == 5123: dtype = np.uint16
        elif accessor.componentType == 5125: dtype = np.uint32
        elif accessor.componentType == 5126: dtype = np.float32
        
        num_components = 1
        if accessor.type == "SCALAR": num_components = 1
        elif accessor.type == "VEC2": num_components = 2
        elif accessor.type == "VEC3": num_components = 3
        elif accessor.type == "VEC4": num_components = 4
        elif accessor.type == "MAT4": num_components = 16
        
        # Extract data
        # Note: This is a simplified extraction and might not handle all strides/interleaving perfectly
        count = accessor.count
        item_size = np.dtype(dtype).itemsize
        total_bytes = count * num_components * item_size
        
        # Slice the data
        chunk = data[offset:offset+total_bytes]
        array = np.frombuffer(chunk, dtype=dtype).reshape(count, num_components)
        
        return array

    # Iterate through nodes to find meshes
    # (Simplified: ignoring hierarchy transforms for now, just grabbing meshes)
    for node in gltf.nodes:
        if node.mesh is not None:
            mesh = gltf.meshes[node.mesh]
            
            for primitive in mesh.primitives:
                # Create a generic Shape
                shape = Shape()
                
                # Positions
                if primitive.attributes.POSITION is not None:
                    pos_data = get_data(primitive.attributes.POSITION)
                    # Convert to vec4 (x, y, z, 1.0)
                    ones = np.ones((pos_data.shape[0], 1), dtype=np.float32)
                    shape.vertices = np.hstack([pos_data, ones]).astype(np.float32)
                
                # Normals
                if primitive.attributes.NORMAL is not None:
                    shape.normals = get_data(primitive.attributes.NORMAL).astype(np.float32)
                
                # UVs
                if primitive.attributes.TEXCOORD_0 is not None:
                    shape.uvs = get_data(primitive.attributes.TEXCOORD_0).astype(np.float32)
                
                # Indices
                if primitive.indices is not None:
                    shape.indices = get_data(primitive.indices).flatten().astype(np.uint32)
                
                # Create MeshObject
                # Apply node transform if present (simplified)
                transform = glm.mat4(1.0)
                if node.matrix:
                    transform = glm.mat4(*node.matrix)
                elif node.translation or node.rotation or node.scale:
                    t = glm.translate(glm.mat4(1.0), glm.vec3(*(node.translation or [0,0,0])))
                    r = glm.mat4(1.0) # Rotation quaternion handling needed if robust
                    if node.rotation:
                        # glTF quaternion is x, y, z, w
                        q = glm.quat(node.rotation[3], node.rotation[0], node.rotation[1], node.rotation[2])
                        r = glm.mat4_cast(q)
                    s = glm.scale(glm.mat4(1.0), glm.vec3(*(node.scale or [1,1,1])))
                    transform = t * r * s
                
                obj = MeshObject(shape, material, transform=transform)
                objects.append(obj)
                
    return objects
