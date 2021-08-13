#version 330
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;

in vec3 vertexPosition;
in vec3 worldPosition;
in vec4 color;

in vec4 lookAtMatrix0;
in vec4 lookAtMatrix1;
in vec4 lookAtMatrix2;
in vec4 lookAtMatrix3;

out vec4 newColor;

void main()
{
    mat4 lookAtMatrix = mat4(lookAtMatrix0, lookAtMatrix1, lookAtMatrix2, lookAtMatrix3);

    gl_Position = uniform_Projection * uniform_View * uniform_Model * (vec4(worldPosition, 1) + (lookAtMatrix * vec4(vertexPosition,1)));
    newColor = color;
}