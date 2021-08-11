#version 330
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;

in vec3 position;
in vec4 color;

out vec4 newColor;

void main()
{
    gl_Position = uniform_Projection * uniform_View * uniform_Model * vec4(position,1);
    newColor = color;
}