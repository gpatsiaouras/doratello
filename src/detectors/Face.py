class Face:
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.center_x = x + self.width//2
        self.center_y = y + self.height//2
        self.area = self.width * self.height
