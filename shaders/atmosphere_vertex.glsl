#version 330 core

layout(location = 0) in vec3 position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 vPosition;  // for scattering calc

void main() {
    vec4 worldPos = model * vec4(position, 1.0);
    vPosition = worldPos.xyz;
    gl_Position = projection * view * worldPos;
}
