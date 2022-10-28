import cv2 as cv
import numpy as np
import math

factor = 50
x_off = 100
y_off = 100
vertices = np.array([
    [1*factor+x_off, 0*factor+y_off],
    [3*factor+x_off, 2*factor+y_off],
    [5*factor+x_off, 1*factor+y_off],
    [6*factor+x_off, 5*factor+y_off],
    [3*factor+x_off, 4*factor+y_off]
])

img = 255 * np.ones(shape=[10*factor, 10*factor, 3], dtype=np.uint8)
cv.fillPoly(img, pts=[vertices], color=(0, 0, 0))
cv.imshow("White Blank", img)

print('Vertices', vertices)


int_angle_sum = 0
out_angle_sum = 0

for i in range(len(vertices)):
    print()

    v = vertices[i]
    a = vertices[(i+1)%len(vertices)]
    b = vertices[(i-1)%len(vertices)]

    a = a - v
    b = b - v

    dot_prod = np.dot(a, b)
    len_prod = np.linalg.norm(a, 2) * np.linalg.norm(b, 2)
    angle = math.acos(dot_prod / len_prod)
    angle = math.degrees(angle)

    cross_prod = np.cross(a, b)
    if cross_prod < 0:
        angle = 360 - angle

    int_angle_sum += angle
    out_angle_sum += 360 - angle

    print('a', a)
    print('b', b)
    print('angle', angle)

print()
print('Inner Angle Sum', round(int_angle_sum, 2))
print('Outer Angle Sum', round(out_angle_sum, 2))


while True:
    cv.waitKey(5)
