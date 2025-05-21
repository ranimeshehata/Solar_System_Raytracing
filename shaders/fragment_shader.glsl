#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D samplerTex;
uniform bool useSolidColor;     
uniform vec3 solidColor;        

void main() {

    vec4 texColor = texture(samplerTex, TexCoord);
    if (useSolidColor) {
        FragColor = vec4(solidColor, 0.3); // Use alpha for atmosphere
    } else {
        FragColor = texColor;
    }
}