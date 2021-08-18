#version 450 core

in PARTICLEOUT {
    vec4 color;
    float brightness;
} particlein;

out vec4 outColor;

void main()
{
    if (brightness < 0.0) {
        discard;
    }
    outColor = particlein.color;
}