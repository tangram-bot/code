import math
import numpy as np

class Polygon:
    def __init__(self, vertices, color):
        self.vertices = vertices
        self.color = color

        self.__calculate_area()
        self.__calculate_interior_angles()
        

    def __calculate_area(self):
        v_len = len(self.vertices)
        s = 0

        for i in range(v_len):
            a = self.vertices[i][0] * self.vertices[(i + 1) % v_len][1]
            b = self.vertices[(i + 1) % v_len][0] * self.vertices[i][1]

            s += a - b

        self.area = abs(s / 2)

    def __calculate_interior_angles(self):
        self.interior_angles = []

        v_len = len(self.vertices)

        for i in range(v_len):
            c0 = self.vertices[(i - 1) % v_len]
            c1 = self.vertices[i]
            c2 = self.vertices[(i + 1) % v_len]
            
            # Vector from c1 to c0
            a = np.array([c0[0]-c1[0], c0[1]-c1[1]])
            # Vector from c1 to c2
            b = np.array([c2[0]-c1[0], c2[1]-c1[1]])

            # Calculate angle
            dot_prod = a.dot(b)
            len_prod = np.linalg.norm(a, ord=2) * np.linalg.norm(b, ord=2)
            rad = math.acos(dot_prod / len_prod)
            deg = math.degrees(rad)
            deg = round(deg, 2)

            # Fix angles greater than 180°
            cross_prod = np.cross(a, b)
            if cross_prod > 0:
                deg = 360 - deg

            self.interior_angles.append(deg)


class Block(Polygon):
    def __init__(self, vertices, color, position=None, rotation=0):
        super().__init__(vertices, color)

        self.position = position
        if position is None:
            self.position = [0, 0]
            
        self.rotation = rotation

    def get_center(self, offset=(0, 0)):
        return (
            (sum([c[0] for c in self.vertices]) / len(self.vertices) + offset[0]),
            (sum([c[1] for c in self.vertices]) / len(self.vertices) + offset[1])
        )

    def get_rotated_vertices(self, rotation_center, angle):
        rads = math.radians(angle)
        cos = math.cos(rads)
        sin = math.sin(rads)

        new_vertices = []

        for old_x, old_y in self.vertices:
            old_x -= rotation_center[0]
            old_y -= rotation_center[1]

            new_x = old_x * cos - old_y * sin
            new_y = old_x * sin + old_y * cos
            
            old_x += rotation_center[0]
            old_y += rotation_center[1]

            new_vertices.append((new_x, new_y))

        return new_vertices



class Shadow(Polygon):
    def __init__(self, vertices):
        super().__init__(vertices, '#000')



BLOCKS = [
    # Große Dreiecke
    Block(((0, 0), (200, 200), (0, 400)), '#f00'),
    Block(((0, 0), (200, 200), (0, 400)), '#0f0'),

    # Mittleres Dreieck
    Block(((0, 0), (200, 0), (0, 200)), '#00f'),

    # Kleine Dreiecke
    Block(((0, 0), (200, 0), (100, 100)), '#ff0'),
    Block(((0, 0), (200, 0), (100, 100)), '#f0f'),

    # Quadrat
    Block(((0, 0), (100, 100), (200, 0), (100, -100)), '#0ff'),

    # Parallelogramm
    Block(((100, 0), (300, 0), (200, 100), (0, 100)), '#555')
]
