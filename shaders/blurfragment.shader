#version 460
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D image;

uniform bool horizontal;
uniform float weight[26];
uniform int blurRange;

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
    if (blurRange != 0)
    {
        vec2 tex_offset = 1.0 / textureSize(image, 0); // gets size of single texel
        vec3 result = texture(image, TexCoords).rgb * weight[0]; // current fragment's contribution
        if(horizontal)
        {
            for(int i = 1; i < blurRange; ++i)
            {
                result += texture(image, TexCoords + vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
                result += texture(image, TexCoords - vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
            }
        }
        else
        {
            for(int i = 1; i < blurRange; ++i)
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