import math
import numpy as np
from pyniryo import cv2
from enum import Enum


# Umrechnungsfaktoren zwischen Bildern und unseren Modellen
AREA_FACTOR = 16000
AREA_FACTOR_SHADOW = 14290
LENGTH_FACTOR = 125




class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def to_np_int_array(self):
        return np.array([int(self.x), int(self.y)])

    def to_np_array(self):
        return np.array([self.x, self.y])

    def get(self, index: int) -> float:
        return self.x if index == 0 else self.y

    def copy(self) -> 'Point':
        return Point(self.x, self.y)

    def __add__(self, other) -> 'Point':
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        elif isinstance(other, int) or isinstance(other, float):
            return Point(self.x + other, self.y + other)

        raise TypeError('other must be type Point, int or float')

    def __sub__(self, other) -> 'Point':
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        elif isinstance(other, int) or isinstance(other, float):
            return Point(self.x - other, self.y - other)

        raise TypeError('other must be type Point, int or float')

    def __mul__(self, other) -> 'Point':
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x * other, self.y * other)

        raise TypeError('other must be type int or float')

    def __truediv__(self, other) -> 'Point':
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x / other, self.y / other)

        raise TypeError('other must be type int or float')

    def __str__(self) -> str:
        return f"Point(x={round(self.x, 2)}, y={round(self.y, 2)})"

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
        return np.array([[[int(p.x), int(p.y)] for p in points]])

    @staticmethod
    def angle(a: 'Point', b: 'Point', fix_reflex_angles=False) -> float:
        a = a.to_np_array()
        b = b.to_np_array()
        
        dot_prod = np.dot(a, b)
        len_prod = abs(np.linalg.norm(a)) * abs(np.linalg.norm(b))

        quot = dot_prod / len_prod
        quot = min(quot, 1)
        quot = max(quot, -1)

        angle = math.acos(quot)
        angle = math.degrees(angle)

        if fix_reflex_angles:
            cross = np.cross(a, b)
            if cross > 0:
                angle = 360 - angle

        return angle


class Polygon:
    vertices: list[Point]
    interior_angles: list[float]
    area: float

    def __init__(self, vertices: list[Point], interior_angles: list[float], area: float) -> None:
        self.vertices = vertices
        self.interior_angles = interior_angles
        self.area = area

    def to_np_array(self):
        return [v.to_np_int_array() for v in self.vertices]

    def get_center(self, offset=Point(0, 0)) -> Point:
        center = offset.copy()

        for v in self.vertices:
            center.x += v.x
            center.y += v.y

        center.x /= len(self.vertices)
        center.y /= len(self.vertices)

        return center

    def get_scaled_vertices(self, offset=Point(0, 0)) -> list[Point]:
        vertices: list[Point] = []

        for v in self.vertices:
            vertices.append(Point(v.x * LENGTH_FACTOR + offset.x, v.y * LENGTH_FACTOR + offset.y))

        return vertices

    def get_vertex(self, index: int) -> Point:
        index = index % len(self.vertices)
        return self.vertices[index]

    def __str__(self) -> str:
        return f'Polygon(vertices={self.vertices}, interior_angles={self.interior_angles}, area={self.area})'

    def __repr__(self) -> str:
        return self.__str__()


class BlockType(Enum):
    SQUARE = 1
    PARALLELOGRAM = 2
    SMALL_TRIANGLE = 3
    MEDIUM_TRIANGLE = 4
    LARGE_TRIANGLE = 5

class Block(Polygon):
    btype: BlockType
    center: Point
    rotation: float
    
    def __init__(self, btype: BlockType, vertices: list[Point], interior_angles: list[float], area: float, center: Point, rotation: float) -> None:
        super().__init__(vertices, interior_angles, area)

        self.btype = btype
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

    def intersects_with(self, other: 'Edge') -> bool:
        if(not isinstance(other, Edge)): 
            return False

        angle = angle_between_edges(self, other)
        if(angle < 1):
            return False

        s, t = intersection_parameters(self, other)
        eps = 0.09 # TODO: vielleicht nochmal anpassen :)
        return (eps < s < 1-eps) and (eps < t < 1-eps)




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
    a = e1.p1.to_np_int_array()
    b = e2.p1.to_np_int_array()

    a = a - e1.p2.to_np_int_array()
    b = b - e2.p2.to_np_int_array()

    dot_prod = np.dot(a, b)
    len_prod = np.linalg.norm(a, 2) * np.linalg.norm(b, 2)

    div = dot_prod / len_prod
    div = max(-1, div)
    div = min(div, 1)

    angle = math.acos(div)
    angle = math.degrees(angle)

    return angle

def intersection_parameters(e1: Edge, e2: Edge) -> tuple[float, float]:
    b1 = e1.p1
    b11 = b1.x
    b12 = b1.y

    r1 = e1.p2 - e1.p1
    r11 = r1.x
    r12 = r1.y

    b2 = e2.p1
    b21 = b2.x
    b22 = b2.y

    r2 = e2.p2 - e2.p1
    r21 = r2.x
    r22 = r2.y

    s = (r22 * (b11 - b21) - r21 * (b12 - b22)) / (r12 * r21 - r11 * r22)
    if(r21 != 0):
        t = (b11 - b21 + s * r11) / r21
    else:
        t = (b12 - b22 + s * r12) / r22

    return s, t
