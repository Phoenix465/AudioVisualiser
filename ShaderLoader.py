from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER


def loadShader(shader_file):
    with open(shader_file) as f:
        shader_source = f.read()
    f.close()
    return str.encode(shader_source)


def compileShaders(vs, fs):
    vert_shader = loadShader(vs)
    frag_shader = loadShader(fs)

    shader = compileProgram(compileShader(vert_shader, GL_VERTEX_SHADER),
                            compileShader(frag_shader, GL_FRAGMENT_SHADER))

    return shader
