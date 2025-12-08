#version 430 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

in vec3 position;
in vec3 normal;
in vec2 uv; // x = density

out vec3 frag_pos;
out float dist_to_cam;
out float v_density;

void main()
{
    vec4 world_pos = model * vec4(position, 1.0);
    frag_pos = world_pos.xyz;
    vec4 view_pos = view * world_pos;
    
    gl_Position = projection * view_pos;
    
    dist_to_cam = length(view_pos.xyz);
    v_density = uv.x;
    
    // Attenuation: Size decreases with distance
    // Base size 5.0, adjusted by distance
    gl_PointSize = 10.0 / (dist_to_cam + 0.1); 
    
    // Clamp size
    if (gl_PointSize > 2.0) gl_PointSize = 2.0;
    if (gl_PointSize < 1.0) gl_PointSize = 1.0;
}
