from os import path


class PathHolder:
    def __init__(self):
        self.resources = path.join(".", "resources")
        self.iconPath = path.join(self.resources, "icon.png")
        self.songPath = path.join(self.resources, "LetTheWindTellYou.wav")

        self.imagesPath = path.join(self.resources, "images")
        self.scorePath = path.join(self.imagesPath, "score")
        self.scoreBasePath = path.join(self.scorePath, "score@2x.png")

        self.shaderPath = path.join(".", "shaders")

        self.vertexPath = path.join(self.shaderPath, "vertex.shader")
        self.fragmentPath = path.join(self.shaderPath, "fragment.shader")
        self.defaultShaderPaths = (self.vertexPath, self.fragmentPath)

        self.blurVertexPath = path.join(self.shaderPath, "blurvertex.shader")
        self.blurFragmentPath = path.join(self.shaderPath, "blurfragment.shader")
        self.blurShaderPaths = (self.blurVertexPath, self.blurFragmentPath)

        self.uiVertexPath = path.join(self.shaderPath, "UIvertex.shader")
        self.uiFragmentPath = path.join(self.shaderPath, "UIfragment.shader")
        self.uiShaderPaths = (self.uiVertexPath, self.uiFragmentPath)
