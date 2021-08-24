#version 450 core

in PARTICLEOUT {
    vec4 color;
    float brightness;
    int valid;
} particlein;

layout (location = 0) out vec4 outColor;
layout (location = 1) out vec4 brightColor;

void main()
{
    if (particlein.valid == 0){
        discard;
    }

    outColor = particlein.color;

    if (particlein.brightness > 0) {
        brightColor = vec4(outColor.rgb, 1);
    }
    else {
        brightColor = vec4(0, 0, 0, 1);
    }
}