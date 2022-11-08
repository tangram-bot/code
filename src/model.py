from typing import List, Tuple

import math
import numpy as np
from sympy import Eq, solve, Symbol


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

    def __init__(self, x: int, y: int) -> None:
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

    def get(self, index) -> int:
        return self.x if index == 0 else self.y


class Edge:
    p1: Point
    p2: Point

    def __init__(self, p1: Point, p2: Point) -> None:
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

    def intersects_with(self, edge2) -> bool:
        if(not isinstance(edge2, Edge)): 
            return False

        angle = angle_between_edges(self, edge2)

        if(angle < 0.01):
            return False

        intersect_points = edges_intersect_point(self, edge2)
        results = [False, False]
        for i in range(intersect_points):
            results[i] = not( intersect_points[i] < 0.01 or intersect_points[i] > 0.99)

        return results[0] and results[1]

def edges_equal_direction_sensitive(e1: Edge, e2: Edge) -> bool:
    return e1.p1 == e2.p1 and e1.p2 == e2.p2

def angle_between_edges(e1: Edge, e2: Edge) -> float:
    a = e1.p1.to_cv_array()
    b = e2.p1.to_cv_array()

    a = a - e1.p2.to_cv_array()
    b = b - e2.p2.to_cv_array()

    dot_prod = np.dot(a, b)
    len_prod = np.linalg.norm(a, 2) * np.linalg.norm(b, 2)

    angle = math.acos(dot_prod / len_prod)
    angle = math.degrees(angle)

def edges_intersect_point(e1: Edge, e2: Edge):
    factors = []
    v1 = e1.p2.to_cv_array() - e1.p1.to_cv_array()
    v2 = e2.p2.to_cv_array() - e2.p1.to_cv_array()

    equations = []

    param1 = Symbol("x")
    param2 = Symbol("y")

    for i in range(2):
        equation = Eq((v1[0][i] * param1 + v2[0][i] * param2), (e1.p1.get(i) - e2.p1.get(i)))
        equations.append(equation)
    
    result = solve(equations, (param1, param2))
    return result["x"], result["y"]

class ShadowEdge:
    
    edges: list[Edge]

    def __init__(self, edges: list[Edge]) -> None:
        self.edges = edges


class ShadowPoint:
    
    points: list[Point]

    def __init__(self, points: list[Point]) -> None:
        self.points = points

    def __str__(self) -> str:
        tmp = 'ShadowPoint{ '
        for p in self.points:
            tmp += p.__str__()
            tmp += ' '
        tmp += '}'

        return tmp

    def __repr__(self) -> str:
        return self.__str__()


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
        super().__init__(vertices, interior_angles, area, (0, 0), 0)
