from pyniryo import cv2
from main import show_trackbars


def create_window(window_name: str) -> None:
    if not show_trackbars():
        return
        
    cv2.namedWindow(window_name)


def create_trackbar(window_name: str, trackbar_name: str, val_name: str, max_value: int) -> None:
    if not show_trackbars():
        return

    cv2.createTrackbar(trackbar_name, window_name, VALUES.__getattribute__(val_name), max_value, lambda new_value: update_value(val_name, new_value))


def update_value(val_name: str, new_value: int) -> None:
    VALUES.__setattr__(val_name, new_value)



# Window Names
NW_BLOCKS = 'CV: Blocks'
NW_SHADOW = 'CV: Shadow'

class Values:
    B_BLUR_KERNEL = 1
    B_MASK_LOWER_H = 0
    B_MASK_LOWER_S = 0
    B_MASK_LOWER_V = 30
    B_MASK_UPPER_H = 115
    B_MASK_UPPER_S = 255
    B_MASK_UPPER_V = 255
    B_CANNY_1 = 0
    B_CANNY_2 = 0
    B_DILATE_K_SIZE = 1
    B_MIN_CONTOUR_AREA = 200
    B_CORNER_ACCURACY = 5

    S_CANNY_1 = 280
    S_CANNY_2 = 800
    S_MIN_CONTOUR_AREA = 120
    S_CORNER_ACCURACY = 20

VALUES = Values()




create_window(NW_BLOCKS)
create_trackbar(NW_BLOCKS, 'Blur Kernel',       'B_BLUR_KERNEL',        10)
create_trackbar(NW_BLOCKS, 'Mask Lower H',      'B_MASK_LOWER_H',       255)
create_trackbar(NW_BLOCKS, 'Mask Lower S',      'B_MASK_LOWER_S',       255)
create_trackbar(NW_BLOCKS, 'Mask Lower V',      'B_MASK_LOWER_V',       255)
create_trackbar(NW_BLOCKS, 'Mask Upper H',      'B_MASK_UPPER_H',       255)
create_trackbar(NW_BLOCKS, 'Mask Upper S',      'B_MASK_UPPER_S',       255)
create_trackbar(NW_BLOCKS, 'Mask Upper V',      'B_MASK_UPPER_V',       255)
create_trackbar(NW_BLOCKS, 'Canny 1',           'B_CANNY_1',            255)
create_trackbar(NW_BLOCKS, 'Canny 2',           'B_CANNY_2',            255)
create_trackbar(NW_BLOCKS, 'Dilate Kernel',     'B_DILATE_K_SIZE',      10)
create_trackbar(NW_BLOCKS, 'Min Contour Area',  'B_MIN_CONTOUR_AREA',   500)
create_trackbar(NW_BLOCKS, 'Corner Accuracy',   'B_CORNER_ACCURACY',    1000)

create_window(NW_SHADOW)
create_trackbar(NW_SHADOW, 'Canny 1',           'S_CANNY_1',            1000)
create_trackbar(NW_SHADOW, 'Canny 2',           'S_CANNY_2',            1000)
create_trackbar(NW_SHADOW, 'Min Contour Area',  'S_MIN_CONTOUR_AREA',   500)
create_trackbar(NW_SHADOW, 'Corner Accuracy',   'S_CORNER_ACCURACY',    100)
