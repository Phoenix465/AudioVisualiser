# version 450 core
in vec2 position;
in vec2 texCoords;
in vec4 colour;

out vec4 FragColor;
out vec2 TexCoords;

void main()
{
    gl_Position = vec4(position.x, position.y, 0.0f, 1.0f);

    FragColor = colour;
    TexCoords = texCoords;
}