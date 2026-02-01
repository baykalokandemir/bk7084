#version 430 core

uniform mat4 model;
uniform float point_size;
uniform float time;
uniform bool anim_x;
uniform bool anim_y;
uniform mat4 view;
uniform mat4 projection;

in vec3 position;
in vec3 normal;
in vec2 uv; // x = density

out vec3 frag_pos;
out float dist_to_cam;
out float v_density;
flat out vec2 v_scale_ratios;

void main()
{
    vec4 world_pos = model * vec4(position, 1.0);
    frag_pos = world_pos.xyz;
    vec4 view_pos = view * world_pos;
    
    gl_Position = projection * view_pos;
    
    dist_to_cam = length(view_pos.xyz);
    v_density = uv.x;
    
    // Pulse Animation Logic
    // Random offset based on position to desynchronize points
    float random_offset = sin(dot(position, vec3(12.9898, 78.233, 45.164))) * 43758.5453;
    float pulse = 1.0 + 0.5 * sin(time * 2.0 + random_offset); // varies 0.5 to 1.5
    
    // Determine scaling for each axis
    float scale_x = anim_x ? pulse : 1.0;
    float scale_y = anim_y ? pulse : 1.0;
    
    float max_scale = max(scale_x, scale_y);
    
    // Attenuation
    gl_PointSize = (point_size * max_scale) / (dist_to_cam + 0.1); 
    
    // Clamp size (minimum visible)
    if (gl_PointSize < 1.0) gl_PointSize = 1.0;
    
    // Calculate ratio of actual dimensions to the drawn square point
    v_scale_ratios = vec2(scale_x, scale_y) / max_scale;
}
