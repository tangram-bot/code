from typing import List


class Polygon:
    vertices: List[List[float]]
    interior_angles: List[float]
    area: float

    def __init__(self, vertices):
        self.vertices = vertices


class Block(Polygon):
    def __init__(self, vertices):
        super().__init__(vertices)


class Shadow(Polygon):
    def __init__(self, vertices):
        super().__init__(vertices)
