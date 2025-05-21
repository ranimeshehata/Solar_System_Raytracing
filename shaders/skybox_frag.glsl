#version 330 core
in vec3 TexCoords;
out vec4 FragColor;

uniform sampler2D equirectangularMap;

vec2 sampleSphericalMap(vec3 v)
{
    float theta = atan(v.z, v.x);
    float phi = acos(clamp(v.y, -1.0, 1.0));
    float u = (theta + 3.1415926) / (2.0 * 3.1415926);
    float vTex = phi / 3.1415926;
    return vec2(u, vTex);
}

void main()
{
    vec2 uv = sampleSphericalMap(normalize(TexCoords));
    FragColor = texture(equirectangularMap, uv);
}