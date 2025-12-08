#version 430 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

in vec3 position;
in vec3 normal;
in vec2 uv;

out vec3 world_pos;
out vec3 frag_normal;

void main()
{
    vec4 world_pos4 = model * vec4(position, 1.0);
    world_pos = world_pos4.xyz;
    frag_normal = mat3(transpose(inverse(model))) * normal;
    
    gl_Position = projection * view * world_pos4;
}
