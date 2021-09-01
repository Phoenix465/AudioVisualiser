#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D image;

uniform bool horizontal;
//uniform float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
uniform float weight[5] = float[] (0.23127762369253013, 0.19823799227139693, 0.12389871970154837, 0.055066052368555385, 0.016519611965969107);
//uniform float weight[5] = float[] (0.25903093853563375, 0.22202655134396454, 0.13876656606573418, 0.06167397865278202, 0.0185019654018854);

uniform bool shouldBlur;

/*
#include <cmath>
#include <iostream>

int main() {
  double sigma = 1.75;
  int N = 2;

  double total = -((N+.5) / (std::sqrt(2.0) * sigma)) - std::erf((-N-.5) / (std::sqrt(2.0) * sigma));
  for (int i = -N; i <= +N; ++i) {
    std::cout << (std::erf((i+.5) / (std::sqrt(2.0) * sigma)) - std::erf((i-.5) / (std::sqrt(2.0) * sigma))) / total << '\n';
  }
}*/

void main()
{
    if (shouldBlur)
    {
        vec2 tex_offset = 1.0 / textureSize(image, 0); // gets size of single texel
        vec3 result = texture(image, TexCoords).rgb * weight[0]; // current fragment's contribution
        if(horizontal)
        {
            for(int i = 1; i < 5; ++i)
            {
                result += texture(image, TexCoords + vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
                result += texture(image, TexCoords - vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
            }
        }
        else
        {
            for(int i = 1; i < 5; ++i)
            {
                result += texture(image, TexCoords + vec2(0.0, tex_offset.y * i)).rgb * weight[i];
                result += texture(image, TexCoords - vec2(0.0, tex_offset.y * i)).rgb * weight[i];
            }
        }
        FragColor = vec4(result, 1.0);
    }

    else
    {
        vec3 result = texture(image, TexCoords).rgb; // current fragment's contribution
        FragColor = vec4(result, 1.0);
    }
}