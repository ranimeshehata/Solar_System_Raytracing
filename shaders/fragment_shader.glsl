#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D samplerTex;
uniform bool useSolidColor;     
uniform vec3 solidColor;        

void main() {
    if (useSolidColor) {
        FragColor = vec4(solidColor, 1.0);
    } else {
        FragColor = texture(samplerTex, TexCoord); 
}
}