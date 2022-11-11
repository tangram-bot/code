from typing import List, Tuple
from model import Point
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

