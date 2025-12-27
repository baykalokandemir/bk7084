#version 430 core

out vec4 FragColor;
in vec2 TexCoords;

uniform sampler2D screenTexture;
uniform float aberration_strength;

void main()
{
    // Direction of shift (can be uniform, but radial is common)
    // Simple radial shift: direction = vector from center to pixel
    vec2 direction = TexCoords - 0.5; 
    
    // RGB split
    // Red Channel: shifted outwards
    float r = texture(screenTexture, TexCoords + direction * aberration_strength).r;
    
    // Green Channel: Clean center
    float g = texture(screenTexture, TexCoords).g;
    
    // Blue Channel: shifted inwards (opposite direction)
    float b = texture(screenTexture, TexCoords - direction * aberration_strength).b;
    
    FragColor = vec4(r, g, b, 1.0);
}
