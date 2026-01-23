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
    
    // Remove translation from view matrix so skybox acts as infinite background
    mat4 viewRot = mat4(mat3(view)); 
    
    // We ignore model transform usually, but if we want to rotate skybox we might use it.
    // Let's assume model is identity or rotation only.
    
    vec4 pos = projection * viewRot * vec4(in_position, 1.0);
    
    // Set z to w so that after perspective divide (z/w) depth is 1.0 (max depth)
    gl_Position = pos.xyww;
}
