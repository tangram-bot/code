import math
import numpy as np
from model import Point, AREA_FACTOR


class BlockFeature:
    vertices: list[tuple[float, float]]
    center: Point
    area: float


    def __init__(self, vertices: list[tuple[float, float]], center: Point, area: float) -> None:
        self.vertices = vertices
        self.center = center
        self.area = area


    def get_vertex_count(self) -> int:
        return len(self.vertices)


    def get_scaled_area(self) -> float:
        TOLERANCE = 0.2

        area = self.area / AREA_FACTOR
        area = round(area, 1)

        if abs(0.5 - area) <= TOLERANCE:
            area = 0.5
        elif abs(1.0 - area) <= TOLERANCE:
            area = 1.0
        elif abs(2.0 - area) <= TOLERANCE:
            area = 2.0

        return area


    def get_interior_angles(self) -> list[float]:
        TOLERANCE = 20.0

        angles: list[float] = []

        for i in range(len(self.vertices)):
            v = self.vertices[i].ravel()
            a = self.vertices[(i+1)%len(self.vertices)].ravel()
            b = self.vertices[(i-1)%len(self.vertices)].ravel()

            a = a - v
            b = b - v

            angle = math.acos( np.dot(a, b) / ( abs(np.linalg.norm(a)) * abs(np.linalg.norm(b)) ) )
            angle = math.degrees(angle)

            if abs(45.0 - angle) <= TOLERANCE:
                angle = 45.0
            elif abs(90.0 - angle) <= TOLERANCE:
                angle = 90.0
            elif abs(135.0 - angle) <= TOLERANCE:
                angle = 135.0

            angles.append(angle)

        return angles


    def __str__(self) -> str:
        return f'BlockFeature(vertices={self.vertices}, center={self.center}, area={self.area})'


    def __repr__(self) -> str:
        return self.__str__()




class ShadowFeature:
    
    points: list[Point]

    def __init__(self, points: list[Point]) -> None:
        self.points = points

    def __str__(self) -> str:
        return f'ShadowFeature(points={self.points})'

    def __repr__(self) -> str:
        return self.__str__()
