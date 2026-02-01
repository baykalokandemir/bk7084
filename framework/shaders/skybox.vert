#version 430 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_uv;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec2 frag_uv;
out vec3 local_pos;

void main()
{
    frag_uv = in_uv;
    local_pos = in_position;
    
    mat4 viewRot = mat4(mat3(view)); 
    
    vec4 pos = projection * viewRot * vec4(in_position, 1.0);
    
    gl_Position = pos.xyww;
}
