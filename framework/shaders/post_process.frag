#version 430 core

out vec4 FragColor;
in vec2 TexCoords;

uniform sampler2D screenTexture;
uniform float aberration_strength;
uniform float blur_strength;

vec3 getAberrationColor(vec2 uv) {
    vec2 direction = uv - 0.5; 
    float r = texture(screenTexture, uv + direction * aberration_strength).r;
    float g = texture(screenTexture, uv).g;
    float b = texture(screenTexture, uv - direction * aberration_strength).b;
    return vec3(r, g, b);
}

void main()
{
    vec3 color = vec3(0.0);
    
    if (blur_strength > 0.0) {
        // Simple Box Blur / Average
        // We take 9 samples around the center
        float total = 0.0;
        for (int x = -1; x <= 1; x++) {
            for (int y = -1; y <= 1; y++) {
                vec2 offset = vec2(float(x), float(y)) * blur_strength;
                color += getAberrationColor(TexCoords + offset);
                total += 1.0;
            }
        }
        color /= total;
    } else {
        color = getAberrationColor(TexCoords);
    }
    
    FragColor = vec4(color, 1.0);
}
