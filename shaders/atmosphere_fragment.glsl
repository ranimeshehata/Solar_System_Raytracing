#version 330 core

in vec3 vPosition;

uniform vec3 cameraPos;
uniform vec3 sunDirection;  // normalized
uniform vec3 planetCenter;  // center of Earth
uniform vec3 scatterColor = vec3(0.5, 0.7, 1.0); // bluish
uniform float intensity = 0.8;

out vec4 FragColor;

void main() {
    vec3 viewDir = normalize(vPosition - cameraPos);
    vec3 lightDir = normalize(sunDirection);

    // Dot product of view and light
    float angle = dot(viewDir, lightDir);

    // Rayleigh-like effect: stronger at 90 degrees to the sun
    float scatter = pow(1.0 - angle, 3.0);

    // Add distance falloff based on altitude
    float height = length(vPosition - planetCenter);
    float falloff = exp(-0.2 * (height - 1.0));

    vec3 color = scatter * scatterColor * intensity * falloff;
    FragColor = vec4(color, scatter * 0.6); // alpha for glow
}
