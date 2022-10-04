import numpy as np
import math

def vector_angle(a, b):
    dot_prod = np.dot(a, b)
    len_prod = np.linalg.norm(a, ord=2) * np.linalg.norm(b, ord=2)

    if len_prod == 0:
        return 0.0

    rad = math.acos(dot_prod / len_prod)
    deg = math.degrees(rad)

    return round(deg, 2)
