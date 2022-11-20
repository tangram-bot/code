from model import Point, AREA_FACTOR


class BlockFeature:
    vertices: list[Point]
    center: Point
    area: float


    def __init__(self, vertices: list[Point], center: Point, area: float) -> None:
        self.vertices = vertices
        self.center = center
        self.area = area


    def get_vertex_count(self) -> int:
        return len(self.vertices)


    def get_scaled_area(self) -> float:
        TOLERANCE = 0.25

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
        TOLERANCE = 45 / 2

        angles: list[float] = []

        for i, v in enumerate(self.vertices):
            a = self.vertices[(i+1) % len(self.vertices)] - v
            b = self.vertices[(i-1) % len(self.vertices)] - v

            angle = Point.angle(a, b)

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
