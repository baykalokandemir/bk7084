#version 430 core
out vec4 out_color;

in vec2 frag_uv;
in vec3 local_pos;

uniform vec3 topColor;
uniform vec3 bottomColor;
uniform vec3 sunPosition; 
uniform vec3 moonPosition;

void main()
{
    vec3 dir = normalize(local_pos);

    // Gradient based on Y and Sun position for some dynamic coloring
    // Simple vertical gradient
    float t = dir.y * 0.5 + 0.5;
    t = clamp(t, 0.0, 1.0);
    
    // Use squared interpolation for smoother sky
    t = pow(t, 0.8);

    vec3 skyColor = mix(bottomColor, topColor, t);
    
    // --- Sun ---
    vec3 sunDir = normalize(sunPosition);
    float sunDot = dot(dir, sunDir);
    
    // Sun Disc
    if (sunDot > 0.998) {
        skyColor = mix(skyColor, vec3(1.0, 1.0, 0.9), 1.0); // Sun Core
    } else if (sunDot > 0.990) {
        skyColor = mix(skyColor, vec3(1.0, 0.8, 0.3), 0.5); // Corona
    } else if (sunDot > 0.90) {
        // Bloom/Halo
        skyColor += vec3(1.0, 0.6, 0.1) * pow(sunDot, 64.0) * 0.5; 
    }
    
    // --- Moon ---
    vec3 moonDir = normalize(moonPosition);
    float moonDot = dot(dir, moonDir);
    
    if (moonDot > 0.997) {
        skyColor = mix(skyColor, vec3(0.9, 0.9, 0.95), 1.0); // Moon Disc
    } else if (moonDot > 0.95) {
         skyColor += vec3(0.5, 0.5, 0.8) * pow(moonDot, 32.0) * 0.3; // Glow
    }

    out_color = vec4(skyColor, 1.0);
}
