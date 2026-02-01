#version 430 core

in float dist_to_cam;
in float v_density;
flat in vec2 v_scale_ratios;

out vec4 out_color;

uniform bool enable_glow;
uniform bool is_point_mode;
uniform int shape_type;
uniform vec3 base_color;

// Mikoshi Palette
// Deep Blue: #000b1e -> (0.0, 0.04, 0.12)
// Cyan: #00f0ff -> (0.0, 0.94, 1.0)
// Magenta: #ff003c -> (1.0, 0.0, 0.23)

void main()
{
    // Circular point shape (only for points)
    if (is_point_mode) {
        vec2 center_coord = gl_PointCoord - 0.5;
        
        // shape_type: 0 = Circle, 1 = Square
        if (shape_type == 0) {
            // Ellipse logic: normalize coord by scale ratios
            vec2 adjusted = center_coord / v_scale_ratios;
            // Check radius (0.5 is edge)
            if (length(adjusted) > 0.5) {
                discard;
            }
        } else {
            // Rectangle logic
            // Check if outside bounds defined by scale ratios
            if (abs(center_coord.x) > 0.5 * v_scale_ratios.x || abs(center_coord.y) > 0.5 * v_scale_ratios.y) {
                discard;
            }
        }
    }

    // Color based on distance
    vec3 deep_blue = base_color * 0.2; // Darker version of base color
    vec3 cyan = base_color;
    vec3 hot_white = mix(base_color, vec3(1.0), 0.5);
    
    // Mix based on distance (closer = cyan, further = blue)
    float mix_factor = 1.0 / (dist_to_cam * 0.05 + 0.1);
    mix_factor = clamp(mix_factor, 0.0, 1.0);
    
    vec3 color = mix(deep_blue, cyan, mix_factor);
    
    if (enable_glow) {
        // Boost brightness based on density
        // High density areas get pushed towards white/magenta
        float glow = v_density * 2.0; // Amplify density
        color += vec3(0.2, 0.0, 0.1) * glow; // Add magenta tint
        color += hot_white * max(glow - 0.8, 0.0); // Hot core for very dense areas
    }
    
    out_color = vec4(color, 1.0);
}
