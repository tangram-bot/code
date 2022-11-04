from typing import List, Tuple

import numpy as np


AREA_FACTOR = 16000
LENGTH_FACTOR = 123


class Shape:
    vertices: List[Tuple[float, float]]
    interior_angles: List[float]
    area: float

    def __init__(self, vertices: List[Tuple[float, float]], interior_angles: List[float], area: float) -> None:
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

class Point:
    x: int
    y: int

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    
    def __str__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"

    def __repr__(self) -> str:
        return self.__str__() 

    def __eq__(self, __o: object) -> bool:
        if(not isinstance(__o, Point)): 
            return False
        return self.x == __o.x and self.y == __o.y

    def __hash__(self) -> int:
        return hash(str(self))

    def to_cv_array(self) -> list:
        return np.array([self.x, self.y])


def edges_equal_direction_sensitive(e1, e2) -> bool:
    return e1.p1 == e2.p1 and e1.p2 == e2.p2

class Edge:
    p1: Point
    p2: Point

    def __init__(self, p1, p2) -> None:
        self.p1 = p1
        self.p2 = p2

    def __str__(self) -> str:
        return f"Edge(p1={self.p1}, p2={self.p2})"

    def __repr__(self) -> str:
        return self.__str__() 
    
    def get(self, index: int) -> Point:
        return self.p1 if index == 0 else self.p2

    def __eq__(self, __o: object) -> bool:
        if(not isinstance(__o, Edge)): 
            return False
        
        return edges_equal_direction_sensitive(self, __o) or edges_equal_direction_sensitive(__o, self)
    
    def __hash__(self) -> int:
        return hash(str(self))

class ShadowEdge:
    
    edges: list[Edge]

    def __init__(self, edges: list[Edge]) -> None:
        self.edges = edges


class ShadowPoint:
    
    points: list[Point]

    def __init__(self, points: list[Point]) -> None:
        self.points = points


class Polygon:
    vertices: List[Tuple[float, float]]
    interior_angles: List[float]
    area: float

    position: Tuple[float, float]
    rotation: float

    def __init__(self, vertices: List[Tuple[float, float]], interior_angles: List[float], area: float, position: Tuple[float, float], rotation: float) -> None:
        self.vertices = vertices
        self.interior_angles = interior_angles
        self.area = area

        self.position = position
        self.rotation = rotation

    def __str__(self) -> str:
        return 'Polygon(vertices=%s, interior_angles=%s, area=%f, position=%s, rotation=%f)' % (self.vertices, self.interior_angles, self.area, self.position, self.rotation)

    def __repr__(self) -> str:
        return self.__str__()


class Block(Polygon):
    def __init__(self, shape: Shape, position: Tuple[float, float], rotation: float) -> None:
        super().__init__(shape.vertices, shape.interior_angles, shape.area, position, rotation)

    def get_rotated_vertices(self):
        pass


class Shadow(Polygon):
    def __init__(self, vertices, interior_angles, area) -> None:
        super().__init__(vertices, interior_angles, area)
