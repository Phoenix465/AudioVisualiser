#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D image;
uniform vec3 resolution;

void main()
{
     float Pi = 6.28318530718; // Pi*2
    
    // GAUSSIAN BLUR SETTINGS {{{
    float Directions = 16.0; // BLUR DIRECTIONS (Default 16.0 - More is better but slower)
    float Quality = 3.0; // BLUR QUALITY (Default 4.0 - More is better but slower)
    float Size = 8.0; // BLUR SIZE (Radius)
    // GAUSSIAN BLUR SETTINGS }}}
   
    vec2 Radius = Size/resolution.xy;
    
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = TexCoords/resolution.xy;
    // Pixel colour
    vec4 Color = texture(image, TexCoords);
    
    // Blur calculations
    for( float d=0.0; d<Pi; d+=Pi/Directions)
    {
		for(float i=1.0/Quality; i<=1.0; i+=1.0/Quality)
        {
			Color += texture( image, TexCoords+vec2(cos(d),sin(d))*Radius*i);
        }
    }
    
    // Output to screen
    //Color /= Quality * Directions - 15.0;
    FragColor = Color;
}