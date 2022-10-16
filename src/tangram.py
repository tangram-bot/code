from typing import List, Tuple


AREA_FACTOR = 6000
LENGTH_FACTOR = 80


class Shape:
    vertices: List[Tuple[float, float]]
    interior_angles: List[float]
    area: float

    def __init__(self, vertices: List[Tuple[float, float]], interior_angles: List[float], area: float):
        self.vertices = vertices
        self.interior_angles = interior_angles
        self.area = area


SHAPES: dict[str, Shape] = {
    # Square
    'SQ': Shape([(0, 0), (1, 0), (1, 1), (0, 1)], [90, 90, 90, 90], 1),
    # Small Triangle
    'ST': Shape([(0, 0), (1, 0), (0, 1)], [90, 45, 45], 0.5),
    # Medium Triangle
    'MT': Shape([(0, 0), (2, 0), (1, 1)], [45, 45, 90], 1),
    # Large Triangle
    'LT': Shape([(0, 0), (2, 0), (0, 2)], [90, 45, 45], 2),
    # Paralleogram
    'PA': Shape([(0, 0), (1, 1), (1, 2), (0, 1)], [45, 135, 45, 135], 1),
}


class Polygon:
    vertices: List[Tuple[float, float]]
    interior_angles: List[float]
    area: float

    position: Tuple[float, float]
    rotation: float

    def __init__(self, vertices: List[Tuple[float, float]], interior_angles: List[float], area: float, position: Tuple[float, float], rotation: float):
        self.vertices = vertices
        self.interior_angles = interior_angles
        self.area = area

        self.position = position
        self.rotation = rotation

    def __str__(self):
        return 'Polygon(vertices=%s, interior_angles=%s, area=%f, position=%s, rotation=%f)' % (self.vertices, self.interior_angles, self.area, self.position, self.rotation)

    def __repr__(self):
        return self.__str__()


class Block(Polygon):
    def __init__(self, shape: Shape, position: Tuple[float, float], rotation: float):
        super().__init__(shape.vertices, shape.interior_angles, shape.area, position, rotation)


class Shadow(Polygon):
    def __init__(self, vertices):
        super().__init__(vertices)


# BLOCKS = [
#     Block([()])
# ]
