#version 450 core

in PARTICLEOUT {
    vec4 color;
    int valid;
} particlein;

layout (location = 0) out vec4 outColor;

void main()
{
    if (particlein.valid == 0){
        discard;
    }

    outColor = particlein.color;
}