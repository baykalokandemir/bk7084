#version 430 core

uniform mat4 view;
uniform int light_count;
uniform vec4 light_position[10];
uniform vec4 light_color[10];

uniform float ambient_strength = 0.2;
uniform float specular_strength = 0.5;
uniform float diffuse_strength = 1.0;
uniform float shininess = 64.0;
uniform vec2 texture_scale;

in vec3 frag_normal;
in vec4 frag_color;   //diffuse
in vec4 frag_pos;
in vec2 frag_uv;

#ifdef USE_ALBEDO_TEXTURE
uniform sampler2D albedo_texture_sampler;
#endif

out vec4 out_color;

void main()
{
    vec2 scaled_uv = frag_uv * texture_scale;

    vec3 N = normalize(frag_normal);
    vec3 V = normalize(-frag_pos.xyz);
    vec3 base_color = frag_color.rgb;

    // Emissive Hack: Street Light Bulbs
    // If the vertex color is the specific bright yellow we use for bulbs (1.0, 1.0, 0.8),
    // render it as fully unlit/emissive and return.
    if (frag_color.r > 0.95 && frag_color.g > 0.95 && frag_color.b > 0.75) {
        out_color = frag_color;
        return;
    }

#ifdef USE_ALBEDO_TEXTURE
    vec4 tex_color = texture(albedo_texture_sampler, scaled_uv);
    base_color *= tex_color.rgb;
#endif

    vec3 result = base_color * ambient_strength;

    for (int lid = 0; lid < light_count; ++lid) {
        float distance = length(light_position[lid].xyz - frag_pos.xyz);
        vec3 L = normalize(light_position[lid].xyz - frag_pos.xyz);
        vec3 lightCol = light_color[lid].rgb;

        // Default: Sun (lid == 0) -> No attenuation, Omni-directional
        float attenuation = 1.0;
        float spotEffect = 1.0;

        if (lid > 0) {
            // Street Lights: Attenuation + Downward Spotlight
            
            // 1. Attenuation
            attenuation = 1.0 / (1.0 + 0.1 * distance + 0.05 * distance * distance);
            
            // 2. Spotlight (Downwards)
            vec3 spotDir = vec3(0.0, -1.0, 0.0);
            // Vector from light to frag is -L
            float theta = dot(-L, spotDir);
            float cutOff = 0.5; // Cos value (approx 60 degrees)
            float outerCutOff = 0.3; // Soft edge
            
            spotEffect = smoothstep(outerCutOff, cutOff, theta);
        }

        float diff = max(dot(N, L), 0.0);
        vec3 diffuse = diffuse_strength * base_color * diff * lightCol;

        vec3 H = normalize(L + V);
        float spec = pow(max(dot(N, H), 0.0), shininess);
        vec3 specular = specular_strength * spec * lightCol;

        // Apply light modifiers
        diffuse *= attenuation * spotEffect;
        specular *= attenuation * spotEffect;

        result += diffuse + specular;
    }

    out_color = vec4(result, frag_color.a);
}
