import cv2
import os

path = "cyk-cyk/"
files = os.listdir(path)
fac = 0.955

dimensions = (3508, 2480)
scaled_dimensions = (int(dimensions[0] * fac), int(dimensions[1] * fac))

width, height = scaled_dimensions
x, y = int((dimensions[0] - scaled_dimensions[0]) / 2), int((dimensions[1] - scaled_dimensions[1]) / 2)

for file in files:
    print(file)
    img = cv2.imread(path + file, 1)

    # Crop image to specified area using slicing
    crop_img = img[y:y+height, x:x+width]
    cv2.imwrite(path + file + "-new.png", crop_img)