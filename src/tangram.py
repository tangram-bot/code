import math
import numpy as np
from util import vector_angle

class Polygon:
    vertices: list[list[float]]
    color: str
    area: float
    interior_angles: list[float]

    
    def __init__(self, vertices: list[list[float]], color: str):
        self.vertices = vertices
        self.color = color

        self.__calculate_area()
        self.__calculate_interior_angles()
        


    def get_vertex(self, index: int):
        return self.vertices[index % len(self.vertices)]



    def __calculate_area(self):
        tmp = 0.0

        for i in range(len(self.vertices)):
            a = self.get_vertex(i)
            b = self.get_vertex(i + 1)
            
            tmp += np.cross(a, b)

        self.area = abs(tmp / 2)


    def __calculate_interior_angles(self):
        self.interior_angles = []

        for i in range(len(self.vertices)):
            c0 = self.get_vertex(i - 1)
            c1 = self.get_vertex(i)
            c2 = self.get_vertex(i + 1)
            
            # Vector from c1 to c0
            a = np.subtract(c0, c1)
            # Vector from c1 to c2
            b = np.subtract(c2, c1)

            # Calculate angle
            deg = vector_angle(a, b)

            # Fix angles greater than 180°
            cross_prod = np.cross(a, b)
            if cross_prod > 0:
                deg = 360 - deg

            self.interior_angles.append(deg)





class Block(Polygon):
    name: str
    position: list[int]
    rotation: float


    def __init__(self, name: str, vertices: list[list[float]], color: str):
        super().__init__(vertices, color)

        self.name = name
        self.position = [0, 0]
        self.rotation = 0.0



    def place(self, vertex: int, position: list[float], direction: float):
        # Drehen
        a = self.get_vertex(vertex)
        b = self.get_vertex(vertex - 1)

        vec = np.subtract(b, a)

        deg = vector_angle(vec, direction)

        cross_prod = np.cross(vec, direction)
        cross_prod = cross_prod / abs(cross_prod)
        deg *= cross_prod

        self.rotation = deg



        # self.vertices[vertex] zu position verschieben
        rot_pos = self.get_rotated_vertices(self.get_center(), self.rotation)[vertex]
        pos_diff = np.subtract(position, rot_pos)

        self.position = np.add(self.position, pos_diff)

        print(self.get_rotated_vertices(self.get_center(), self.rotation)[vertex])



    def get_center(self, offset=(0, 0)):
        return (
            (sum([c[0] for c in self.vertices]) / len(self.vertices) + offset[0]),
            (sum([c[1] for c in self.vertices]) / len(self.vertices) + offset[1])
        )



    def get_rotated_vertices(self, rotation_center: list[float], angle: float):
        rads = math.radians(angle)
        cos = math.cos(rads)
        sin = math.sin(rads)

        new_vertices: list[float] = []

        for vertex in self.vertices:
            old_x, old_y = np.subtract(vertex, rotation_center)

            new_x = old_x * cos - old_y * sin + rotation_center[0]
            new_y = old_x * sin + old_y * cos + rotation_center[1]

            new_vertices.append([new_x, new_y])

        return new_vertices





class Shadow(Polygon):
    def __init__(self, vertices: list[list[float]]):
        super().__init__(vertices, '#000')





BLOCKS = [
    Block('Großes Dreieck', ((0, 0), (200, 200), (0, 400)), '#f00'),
    Block('Großes Dreieck', ((0, 0), (200, 200), (0, 400)), '#0f0'),

    Block('Mittleres Dreieck', ((0, 0), (200, 0), (0, 200)), '#00f'),

    Block('Kleines Dreieck', ((0, 0), (200, 0), (100, 100)), '#ff0'),
    Block('Kleines Dreieck', ((0, 0), (200, 0), (100, 100)), '#f0f'),

    Block('Quadrat', ((0, 100), (100, 0), (200, 100), (100, 200)), '#0ff'),

    Block('Parallelogramm', ((100, 0), (300, 0), (200, 100), (0, 100)), '#555')
]
