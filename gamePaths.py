from os import path


class PathHolder:
    def __init__(self):
        self.resources = path.join(".", "resources")
        self.iconPath = path.join(self.resources, "icon.png")