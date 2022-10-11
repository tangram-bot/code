import logging
import numpy as np
from typing import List, Tuple
from pyniryo import cv2
from tangram import Block, Shadow


L = logging.getLogger('CV')


def create_trackbar_uis():
    cv2.namedWindow('CV: General')
    cv2.createTrackbar('Blur Kernel',       'CV: General', 0,   10, lambda x: x)

    cv2.namedWindow('CV: Blocks')
    cv2.createTrackbar('Mask Lower H',      'CV: Blocks', 0,    255, lambda x: x)
    cv2.createTrackbar('Mask Lower S',      'CV: Blocks', 0,    255, lambda x: x)
    cv2.createTrackbar('Mask Lower V',      'CV: Blocks', 47,   255, lambda x: x)
    cv2.createTrackbar('Mask Upper H',      'CV: Blocks', 57,   255, lambda x: x)
    cv2.createTrackbar('Mask Upper S',      'CV: Blocks', 255,  255, lambda x: x)
    cv2.createTrackbar('Mask Upper V',      'CV: Blocks', 255,  255, lambda x: x)
    cv2.createTrackbar('Canny 1',           'CV: Blocks', 0,    255, lambda x: x)
    cv2.createTrackbar('Canny 2',           'CV: Blocks', 0,    255, lambda x: x)
    cv2.createTrackbar('Dilate Kernel',     'CV: Blocks', 1,    10, lambda x: x)
    cv2.createTrackbar('Min Contour Area',  'CV: Blocks', 20,   200, lambda x: x)
    cv2.createTrackbar('Corner Accuracy',   'CV: Blocks', 7,    1000, lambda x: x)

    cv2.namedWindow('CV: Shadow')
    cv2.createTrackbar('Mask Lower H',      'CV: Shadow', 0,    255, lambda x: x)
    cv2.createTrackbar('Mask Lower S',      'CV: Shadow', 0,    255, lambda x: x)
    cv2.createTrackbar('Mask Lower V',      'CV: Shadow', 47,   255, lambda x: x)
    cv2.createTrackbar('Mask Upper H',      'CV: Shadow', 57,   255, lambda x: x)
    cv2.createTrackbar('Mask Upper S',      'CV: Shadow', 255,  255, lambda x: x)
    cv2.createTrackbar('Mask Upper V',      'CV: Shadow', 255,  255, lambda x: x)
    cv2.createTrackbar('Canny 1',           'CV: Shadow', 0,    255, lambda x: x)
    cv2.createTrackbar('Canny 2',           'CV: Shadow', 0,    255, lambda x: x)
    cv2.createTrackbar('Dilate Kernel',     'CV: Shadow', 1,    10, lambda x: x)
    cv2.createTrackbar('Min Contour Area',  'CV: Shadow', 20,   200, lambda x: x)
    cv2.createTrackbar('Corner Accuracy',   'CV: Shadow', 7,    1000, lambda x: x)

create_trackbar_uis()


def process_image(img) -> Tuple[List[Block], Shadow]:

    # blur image to reduce noise & smooth out edges
    kernel_size = cv2.getTrackbarPos('Blur Kernel', 'CV: General')
    blur_kernel = (kernel_size, kernel_size)
    img_blurred = cv2.GaussianBlur(img, blur_kernel, 1)

    blocks = find_blocks(img_blurred)
    shadow = find_shadow(img_blurred)

    return blocks, shadow


def find_blocks(img) -> List[Block]:
    polygons = find_polygons(img, 'CV: Blocks')
    
    blocks = []

    return blocks


def find_shadow(img) -> Shadow:
    polygons = find_polygons(img, 'CV: Shadow')

    shadow = None

    return shadow


def find_polygons(img, window_name) -> List[Tuple[int, int]]:
    img_mask = color_mask(img, window_name)
    
    img_edge = find_edges(img_mask, window_name)

    for contour in find_contours(img_edge):

        if contour_too_small(contour):
            continue

        draw_contour(img, contour)

        corners = find_corners(contour, window_name)

        draw_corners(img, corners)
        


        #======================================#
        # label contour with number of corners #
        #======================================#

        num_corners = len(corners)
        x, y, _, _ = cv2.boundingRect(corners)
        cv2.putText(img, str(num_corners), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)



        #=======================#
        # mark contour's center #
        #=======================#

        x_sum = 0
        y_sum = 0
        
        for corner in corners:
            x_sum += corner[0][0]
            y_sum += corner[0][1]

        x_sum //= num_corners
        y_sum //= num_corners

        cv2.circle(img, (x_sum, y_sum), 2, (0, 0, 0), -1)
        cv2.circle(img, (x_sum, y_sum), 1, (255, 0, 0), -1)

        # label contour's center with relative coordinates
        shape = img.shape
        cv2.putText(img, str(round(x_sum/shape[0], 2)) + ' ' + str(round(y_sum/shape[1], 2)), (x_sum, y_sum), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)



    return []


def color_mask(img, window_name):
    lower_h = cv2.getTrackbarPos('Lower H', window_name)
    lower_s = cv2.getTrackbarPos('Lower S', window_name)
    lower_v = cv2.getTrackbarPos('Lower V', window_name)
    upper_h = cv2.getTrackbarPos('Upper H', window_name)
    upper_s = cv2.getTrackbarPos('Upper S', window_name)
    upper_v = cv2.getTrackbarPos('Upper V', window_name)

    lower = (lower_h, lower_s, lower_v)
    upper = (upper_h, upper_s, upper_v)

    img_masked = cv2.inRange(img, lower, upper)

    return img_masked


def find_edges(img, window_name):
    threshold_1 = cv2.getTrackbarPos('Canny 1', window_name)
    threshold_2 = cv2.getTrackbarPos('Canny 2', window_name)

    img_canny = cv2.Canny(img, threshold_1, threshold_2)
    
    kernel_size = cv2.getTrackbarPos('D-Kernel', window_name)

    kernel = np.ones((kernel_size, kernel_size))
    img_edges = cv2.dilate(img_canny, kernel, iterations=1)

    return img_edges


def find_contours(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours


def contour_too_small(contour, window_name):
    area = cv2.contourArea(contour)

    min_contour_area = cv2.getTrackbarPos('Contour Area', window_name)

    return area < min_contour_area


def find_corners(contour, window_name):
    accuracy = cv2.getTrackbarPos('Corner Accuracy', window_name)

    perimeter = cv2.arcLength(contour, True)

    corners = cv2.approxPolyDP(contour,  perimeter * 0.01 * accuracy, True)

    return corners



def draw_contour(img, contour):
    cv2.drawContours(img, contour, -1, (0, 0, 0), 2)
    cv2.drawContours(img, contour, -1, (0, 0, 255), 1)


def draw_corners(img, corners):
    for corner in corners:
        cv2.circle(img, corner[0], 2, (0, 0, 0), -1)
        cv2.circle(img, corner[0], 1, (0, 255, 0), -1)

