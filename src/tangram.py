import math

class Block:
    def __init__(self, corners, rotation, color):
        self.corners = corners
        self.rotation = rotation
        self.color = color

    def get_center(self, offset=(0, 0)):
        return (
            (sum([c[0] for c in self.corners]) / len(self.corners) + offset[0]),
            (sum([c[1] for c in self.corners]) / len(self.corners) + offset[1])
        )

    def get_rotated_corners(self, offset=(0, 0), angle=0):
        cx, cy = self.get_center(offset)

        rads = math.radians(angle)
        cos_val = math.cos(rads)
        sin_val = math.sin(rads)

        new_corners = []

        for old_x, old_y in self.corners:
            old_x += offset[0]
            old_y += offset[1]

            old_x -= cx
            old_y -= cy

            new_x = old_x * cos_val - old_y * sin_val
            new_y = old_x * sin_val + old_y * cos_val

            new_corners.append((new_x + cx, new_y + cy))

        return new_corners

BLOCKS = [
    # Große Dreiecke
    Block([(0, 0), (200, 200), (0, 400), (0, 0)], 0, '#f00'),
    Block([(0, 0), (200, 200), (0, 400), (0, 0)], 0, '#0f0'),

    # Mittleres Dreieck
    Block([(0, 0), (200, 0), (0, 200), (0, 0)], 0, '#00f'),

    # Kleine Dreiecke
    Block([(0, 0), (200, 0), (100, 100), (0, 0)], 0, '#ff0'),
    Block([(0, 0), (200, 0), (100, 100), (0, 0)], 0, '#f0f'),

    # Quadrat
    Block([(100, 100), (200, 200), (100, 300), (0, 200), (100, 100)], 0, '#0ff'),

    # Parallelogramm
    Block([(0, 100), (100, 0), (300, 0), (200, 100), (0, 100)], 0, '#555')
]
