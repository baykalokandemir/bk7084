#version 430 core

uniform mat4 view;
uniform vec3 hologram_color;
uniform float time;

// Refinement Uniforms
uniform float lines_frequency = 100.0;
uniform float lines_thickness = 0.5; // 0.0 to 1.0 (Duty cycle)
uniform vec2 uv_scale = vec2(1.0);
uniform vec2 uv_offset = vec2(0.0);
uniform bool flip_y = false;

uniform sampler2D texture_sampler;
uniform bool use_texture;

in vec3 frag_normal;
in vec4 frag_color;
in vec4 frag_pos;
in vec2 frag_uv;

out vec4 out_color;

void main()
{
    // 1. UV Manipulation
    vec2 uv = frag_uv;
    
    // Interactive Flip
    if (flip_y) {
        uv.y = 1.0 - uv.y;
    }
    
    // Zoom/Pan (Center Origin)
    // uv_scale < 1.0 means ZOOM IN
    uv = (uv - 0.5) * uv_scale + 0.5;
    uv += uv_offset;
    
    // Clip borders cleanly
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        discard;
    }

    vec4 tex_color = texture(texture_sampler, uv);

    // 2. Base Brightness
    float brightness = dot(tex_color.rgb, vec3(0.299, 0.587, 0.114));
    
    // 3. Vertical Strips
    // Map UV.x to sine wave
    float sine_val = sin(frag_uv.x * lines_frequency * 3.14159);
    // Normalize -1..1 to 0..1
    float norm_sine = sine_val * 0.5 + 0.5;
    // Apply duty cycle (thickness)
    // smoothstep for anti-aliased edges
    float thickness_threshold = 1.0 - lines_thickness;
    float strips = smoothstep(thickness_threshold, thickness_threshold + 0.05, norm_sine);

    // 4. Scanline
    float scanline = sin(frag_uv.y * 50.0 - time * 5.0) * 0.1 + 0.9;

    // 5. Combine
    vec3 final_color = hologram_color * brightness;
    
    // Bloom/Glow Boost
    final_color += final_color * brightness * 1.5; 

    float alpha = brightness * strips * scanline;
    alpha = clamp(alpha * 1.5, 0.0, 1.0);

    out_color = vec4(final_color, alpha);
}
