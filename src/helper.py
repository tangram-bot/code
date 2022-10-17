from typing import List, Tuple
import numpy as np
import math


#===============#
# GENERAL MATHS #
#===============#

def vector_angle(a, b) -> float:
    dot_prod = np.dot(a, b)
    len_prod = abs(np.linalg.norm(a)) * abs(np.linalg.norm(b))

    angle = math.acos( dot_prod / len_prod )
    angle = math.degrees(angle)

    return angle


def rotate_around_center(vertices: List[Tuple[float, float]], center: Tuple[float, float], angle: float) -> List[Tuple[float, float]]:
    rads = math.radians(angle)
    cos = math.cos(rads)
    sin = math.sin(rads)

    new_vertices: list[float] = []

    for vertex in vertices:
        old_x, old_y = np.subtract(vertex, center)

        new_x = old_x * cos - old_y * sin + center[0]
        new_y = old_x * sin + old_y * cos + center[1]

        new_vertices.append([new_x, new_y])

    return new_vertices
