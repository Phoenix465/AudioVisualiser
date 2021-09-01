#version 330 core
out vec4 outputColor;

in vec4 FragColor;
in vec2 TexCoords;

void main()
{
    vec3 result = texture(image, TexCoords).rgb;
    outputColor = vec4(result, 1.0) * FragColor;
}