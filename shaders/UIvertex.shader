#version 330

in vec2 position;
in vec4 colour;
in vec2 textureCoords;

out vec4 FragColor;
out vec2 TexCoords;

void main()
{
    // Screen Coords are -1 => 1,
    // User Coords are 0 -> 1

    // Z is not 0 so it won't be hidden by the ParticleBlur FBO
    gl_Position = vec4((position*2 * vec2(1, -1) + vec2(-1, 1)), -0.0000001f, 1);

    FragColor = colour;
    TexCoords = textureCoords;
}