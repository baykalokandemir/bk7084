#version 430 core

in vec3 world_pos;
in vec3 frag_normal;

out vec4 out_color;

uniform vec3 color;
uniform float slice_spacing;
uniform float slice_thickness;
uniform vec3 slice_normal; // Direction of slicing
uniform float warp_factor; // Distortion amount
uniform float slice_offset; // Animation offset

void main()
{
    // Calculate slice distance along the normal vector
    float dist = dot(world_pos, normalize(slice_normal));
    
    // Apply non-linear distortion (sine wave)
    dist += sin(world_pos.x * 10.0 + world_pos.z * 10.0) * warp_factor;
    
    // Apply animation offset
    dist += slice_offset;
    
    // Shift dist slightly to avoid z-fighting or artifacts at 0
    float d = dist + 1000.0; 
    
    float d_mod = mod(d, slice_spacing);
    
    if (d_mod > slice_thickness) {
        discard;
    }
    
    // Simple lighting
    vec3 light_dir = normalize(vec3(1.0, 1.0, 1.0));
    float diff = max(dot(normalize(frag_normal), light_dir), 0.2); // Ambient 0.2
    
    // Add a bit of emission/glow look by boosting color
    vec3 final_color = color * diff + color * 0.5;
    
    out_color = vec4(final_color, 1.0);
}
