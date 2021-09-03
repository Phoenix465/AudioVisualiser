#version 330 core
out vec4 outputColor;

in vec4 FragColor;
in vec2 TexCoords;

uniform sampler2D image;

void main()
{
    vec4 result = texture(image, TexCoords);

    outputColor = FragColor * result;
}