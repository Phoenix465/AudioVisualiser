#version 450 core
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;
uniform mat4 lookAtMatrix;

in vec3 vertexPosition;
in vec3 worldPosition;
in vec4 color;
in float scale;
in int draw;

out PARTICLEOUT {
    vec4 color;
    int valid;
} particleout;

void main()
{
    gl_Position = uniform_Projection * uniform_View * uniform_Model * (vec4(worldPosition, 1) + (lookAtMatrix * vec4(vertexPosition * scale,1)));

    particleout.color = color;
    particleout.valid = draw;
}