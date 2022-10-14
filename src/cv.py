import logging
import numpy as np
from typing import List, Tuple
from pyniryo import cv2, show_img_and_check_close
from tangram import Block, Shadow


L = logging.getLogger('CV')

NW_BLOCKS = 'CV: Blocks'
NW_SHADOW = 'CV: Shadow'


def create_trackbar_uis():
    cv2.namedWindow('CV: Blocks')
    cv2.createTrackbar('Blur Kernel',       NW_BLOCKS,  1,      10,     lambda x: x)
    cv2.createTrackbar('Mask Lower H',      NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Mask Lower S',      NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Mask Lower V',      NW_BLOCKS,  30,     255,    lambda x: x)
    cv2.createTrackbar('Mask Upper H',      NW_BLOCKS,  115,    255,    lambda x: x)
    cv2.createTrackbar('Mask Upper S',      NW_BLOCKS,  255,    255,    lambda x: x)
    cv2.createTrackbar('Mask Upper V',      NW_BLOCKS,  255,    255,    lambda x: x)
    cv2.createTrackbar('Canny 1',           NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Canny 2',           NW_BLOCKS,  0,      255,    lambda x: x)
    cv2.createTrackbar('Dilate Kernel',     NW_BLOCKS,  1,      10,     lambda x: x)
    cv2.createTrackbar('Min Contour Area',  NW_BLOCKS,  200,    500,    lambda x: x)
    cv2.createTrackbar('Corner Accuracy',   NW_BLOCKS,  5,      1000,   lambda x: x)

    cv2.namedWindow('CV: Shadow')
    cv2.createTrackbar('Blur Kernel',       NW_SHADOW,  2,      10,     lambda x: x)
    cv2.createTrackbar('Canny 1',           NW_SHADOW,  0,      255,    lambda x: x)
    cv2.createTrackbar('Canny 2',           NW_SHADOW,  0,      255,    lambda x: x)
    cv2.createTrackbar('Dilate Kernel',     NW_SHADOW,  1,      10,     lambda x: x)
    cv2.createTrackbar('Min Contour Area',  NW_SHADOW,  200,    500,    lambda x: x)
    cv2.createTrackbar('Corner Accuracy',   NW_SHADOW,  5,      1000,   lambda x: x)


def find_blocks(img) -> List[Block]:
    # Blur image to reduce noise
    img_blur = blur(img, NW_BLOCKS)
    
    # Apply color mask to find colored areas
    img_mask = color_mask(img_blur, NW_BLOCKS)

    show_img_and_check_close('Color Mask', img_mask)
    
    # Apply edge detection
    img_edge = find_edges(img_mask, NW_BLOCKS)

    centers = []

    for contour in find_contours(img_edge):

        # Skip if contour is too small
        if contour_too_small(contour, NW_BLOCKS):
            continue

        draw_contour(img, contour)

        # Find corners of the contour
        corners = find_corners(contour, NW_BLOCKS)

        draw_corners(img, corners)
        


        #======================================#
        # label contour with number of corners #
        #======================================#

        num_corners = len(corners)
        x, y, _, _ = cv2.boundingRect(corners)
        cv2.putText(img, str(num_corners) + ' ' + str(round(cv2.contourArea(contour), 2)), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)



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

        centers.append((x_sum/img.shape[1], y_sum/img.shape[0]))

        cv2.circle(img, (x_sum, y_sum), 2, (0, 0, 0), -1)
        cv2.circle(img, (x_sum, y_sum), 1, (255, 0, 0), -1)

        # label contour's center with relative coordinates
        shape = img.shape
        # cv2.putText(img, str(round(x_sum/shape[0], 2)) + ' ' + str(round(y_sum/shape[1], 2)), (x_sum, y_sum), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)

    show_img_and_check_close('Blocks', img)

    return centers



def find_shadow(img) -> Shadow:
    # Blur image to reduce noise
    img_blur = blur(img, NW_SHADOW)
    
    # Apply edge detection
    img_edge = find_edges(img_blur, NW_SHADOW)

    for contour in find_contours(img_edge):

        # Skip if contour is too small
        if contour_too_small(contour, NW_SHADOW):
            continue

        draw_contour(img, contour)

        # Find corners of the contour
        corners = find_corners(contour, NW_SHADOW)

        draw_corners(img, corners)
        

        #======================================#
        # label contour with number of corners #
        #======================================#

        num_corners = len(corners)
        x, y, _, _ = cv2.boundingRect(corners)
        cv2.putText(img, str(num_corners) + ' ' + str(round(cv2.contourArea(contour), 2)), (x, y-5), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)

    show_img_and_check_close('Shadow', img)

    return None




#=====================#
# CV HELPER FUNCTIONS #
#=====================#

def blur(img, window_name):
    kernel_size = cv2.getTrackbarPos('Blur Kernel', window_name) * 2 + 1
    
    blur_kernel = (kernel_size, kernel_size)

    img_blurred = cv2.GaussianBlur(img, blur_kernel, 1)

    return img_blurred


def color_mask(img, window_name):
    lower_h = cv2.getTrackbarPos('Mask Lower H', window_name)
    lower_s = cv2.getTrackbarPos('Mask Lower S', window_name)
    lower_v = cv2.getTrackbarPos('Mask Lower V', window_name)
    upper_h = cv2.getTrackbarPos('Mask Upper H', window_name)
    upper_s = cv2.getTrackbarPos('Mask Upper S', window_name)
    upper_v = cv2.getTrackbarPos('Mask Upper V', window_name)

    lower = (lower_h, lower_s, lower_v)
    upper = (upper_h, upper_s, upper_v)

    img_masked = cv2.inRange(img, lower, upper)

    return img_masked


def find_edges(img, window_name):
    threshold_1 = cv2.getTrackbarPos('Canny 1', window_name)
    threshold_2 = cv2.getTrackbarPos('Canny 2', window_name)

    img_canny = cv2.Canny(img, threshold_1, threshold_2)
    
    kernel_size = cv2.getTrackbarPos('Dilate Kernel', window_name)

    kernel = np.ones((kernel_size, kernel_size))
    img_edges = cv2.dilate(img_canny, kernel, iterations=1)

    return img_edges


def find_contours(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours


def contour_too_small(contour, window_name):
    area = cv2.contourArea(contour)

    min_contour_area = cv2.getTrackbarPos('Min Contour Area', window_name)

    return area < min_contour_area


def find_corners(contour, window_name):
    accuracy = cv2.getTrackbarPos('Corner Accuracy', window_name)

    perimeter = cv2.arcLength(contour, True)

    corners = cv2.approxPolyDP(contour, perimeter * 0.01 * accuracy, True)

    return corners



def draw_contour(img, contour):
    cv2.drawContours(img, contour, -1, (0, 0, 0), 2)
    cv2.drawContours(img, contour, -1, (0, 0, 255), 1)


def draw_corners(img, corners):
    for corner in corners:
        cv2.circle(img, corner[0], 2, (0, 0, 0), -1)
        cv2.circle(img, corner[0], 1, (0, 255, 0), -1)

