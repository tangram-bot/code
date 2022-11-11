import math
import numpy as np
from sympy import Eq, solve, Symbol
from pyniryo import cv2


# Umrechnungsfaktoren zwischen Bildern und unseren Modellen
AREA_FACTOR = 16000
AREA_FACTOR_SHADOW = 14290
LENGTH_FACTOR = 123




class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = int(x)
        self.y = int(y)

    def to_np_array(self):
        return np.array([self.x, self.y])

    def get(self, index: int) -> int:
        return self.x if index == 0 else self.y

    def copy(self):
        return Point(self.x, self.y)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        elif isinstance(other, int):
            return Point(self.x + other, self.y + other)

        raise TypeError('other must be type Point or int')

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        elif isinstance(other, int):
            return Point(self.x - other, self.y - other)

        raise TypeError('other must be type Point or int')

    def __mul__(self, other):
        if isinstance(other, int):
            return Point(self.x * other, self.y * other)

        raise TypeError('other must be type int')

    def __truediv__(self, other):
        if isinstance(other, int):
            return Point(self.x / other, self.y / other)

        raise TypeError('other must be type int')

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

    @staticmethod
    def rotate_around_point(points: list['Point'], center: 'Point', angle: float) -> list['Point']:
        rads = math.radians(angle)
        cos = math.cos(rads)
        sin = math.sin(rads)

        rotated_points: list[Point] = []

        for point in points:
            p = point - center

            x = p.x * cos - p.y * sin + center.x
            y = p.x * sin + p.y * cos + center.y

            rotated_points.append(Point(x, y))

        return rotated_points

    @staticmethod
    def scale_points(points: list['Point'], factor: float) -> list['Point']:
        scaled_points: list[Point] = []

        for p in points:
            scaled_points.append(p * factor)

        return scaled_points

    @staticmethod
    def move_points(points: list['Point'], diff: 'Point') -> list['Point']:
        moved_points: list[Point] = []

        for p in points:
            moved_points.append(p + diff)

        return moved_points

    @staticmethod
    def get_center(points: list['Point']) -> 'Point':
        p_sum = Point(0, 0)

        for p in points:
            p_sum += p

        return p_sum / len(points)

    @staticmethod
    def list_to_np_array(points: list['Point']):
        return np.array([[[p.x, p.y] for p in points]])


class Polygon:
    vertices: list[Point]
    interior_angles: list[float]
    area: float

    def __init__(self, vertices: list[Point], interior_angles: list[float], area: float) -> None:
        self.vertices = vertices
        self.interior_angles = interior_angles
        self.area = area

    def to_np_array(self):
        return [v.to_np_array() for v in self.vertices]

    def get_center(self, offset=Point(0, 0)) -> Point:
        center = offset.copy()

        for v in self.vertices:
            center.x += v.x
            center.y += v.y

        center.x //= len(self.vertices)
        center.y //= len(self.vertices)

        return center

    def get_scaled_vertices(self, offset=Point(0, 0)) -> list[Point]:
        vertices: list[Point] = []

        for v in self.vertices:
            vertices.append(Point(v.x * LENGTH_FACTOR + offset.x, v.y * LENGTH_FACTOR + offset.y))

        return vertices

    def __str__(self) -> str:
        return f'Polygon(vertices={self.vertices}, interior_angles={self.interior_angles}, area={self.area})'

    def __repr__(self) -> str:
        return self.__str__()


class Block(Polygon):
    center: Point
    rotation: float
    
    def __init__(self, vertices: list[Point], interior_angles: list[float], area: float, center: Point, rotation: float) -> None:
        super().__init__(vertices, interior_angles, area)

        self.center = center
        self.rotation = rotation

    def draw(self, img, color, rotation: float, offset: Point = None) -> None:
        if offset is None:
            offset = self.center

        # Block von Modell-Größe auf Pixel-Größe skalieren
        pts = Point.scale_points(self.vertices, LENGTH_FACTOR)

        # Block zu richtiger Position verschieben
        center = offset - Point.get_center(pts)
        pts = Point.move_points(pts, center)

        # Block um Mittelpunkt rotieren
        pts = Point.rotate_around_point(pts, offset, rotation)

        # Block zeichnen
        cv2.fillPoly(img, Point.list_to_np_array(pts), color)

    def __str__(self) -> str:
        return f'Block(vertices={self.vertices}, interior_angles={self.interior_angles}, area={self.area}, position={self.center}, rotation={self.rotation})'

    def __repr__(self) -> str:
        return self.__str__()


class Shadow(Polygon):

    def __init__(self, vertices: list[Point], interior_angles: list[float], area: float) -> None:
        super().__init__(vertices, interior_angles, area)

    def __str__(self) -> str:
        return f'Shadow(vertices={self.vertices}, interior_angles={self.interior_angles}, area={self.area})'

    def __repr__(self) -> str:
        return self.__str__()











class Edge:
    p1: Point
    p2: Point

    def __init__(self, p1: Point, p2: Point) -> None:
        self.p1 = p1
        self.p2 = p2


    def get(self, index: int) -> Point:
        return self.p1 if index == 0 else self.p2

    def intersects_with(self, edge2: 'Edge') -> bool:
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


    def __str__(self) -> str:
        return f"Edge(p1={self.p1}, p2={self.p2})"

    def __repr__(self) -> str:
        return self.__str__() 
    
    def __eq__(self, __o: object) -> bool:
        if(not isinstance(__o, Edge)): 
            return False
        
        return edges_equal_direction_sensitive(self, __o) or edges_equal_direction_sensitive(__o, self)
    
    def __hash__(self) -> int:
        return hash(str(self))


def edges_equal_direction_sensitive(e1: Edge, e2: Edge) -> bool:
    return e1.p1 == e2.p1 and e1.p2 == e2.p2

def angle_between_edges(e1: Edge, e2: Edge) -> float:
    a = e1.p1.to_np_array()
    b = e2.p1.to_np_array()

    a = a - e1.p2.to_np_array()
    b = b - e2.p2.to_np_array()

    dot_prod = np.dot(a, b)
    len_prod = np.linalg.norm(a, 2) * np.linalg.norm(b, 2)

    angle = math.acos(dot_prod / len_prod)
    angle = math.degrees(angle)

def edges_intersect_point(e1: Edge, e2: Edge):
    v1 = e1.p2.to_np_array() - e1.p1.to_np_array()
    v2 = e2.p2.to_np_array() - e2.p1.to_np_array()

    equations = []

    param1 = Symbol("x")
    param2 = Symbol("y")

    for i in range(2):
        equation = Eq((v1[0][i] * param1 + v2[0][i] * param2), (e1.p1.get(i) - e2.p1.get(i)))
        equations.append(equation)
    
    result = solve(equations, (param1, param2))
    return result["x"], result["y"]
