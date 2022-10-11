import logging
from typing import List, Tuple
from pyniryo import show_img_and_check_close, cv2
import numpy as np

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



def process_image(img) -> Tuple[List[Block], Shadow]:

    # blur image to reduce noise & smooth out edges
    kernel_size = cv2.getTrackbarPos('Blur Kernel', 'CV: General')
    blur_kernel = (kernel_size, kernel_size)
    img_blurred = cv2.GaussianBlur(img, blur_kernel, 1)

    blocks = find_blocks(img_blurred)
    shadow = find_shadow(img_blurred)

    return blocks, shadow


def find_blocks(img) -> List[Block]:

    lower_h = cv2.getTrackbarPos('Lower H', 'CV: Blocks')
    lower_s = cv2.getTrackbarPos('Lower S', 'CV: Blocks')
    lower_v = cv2.getTrackbarPos('Lower V', 'CV: Blocks')
    upper_h = cv2.getTrackbarPos('Upper H', 'CV: Blocks')
    upper_s = cv2.getTrackbarPos('Upper S', 'CV: Blocks')
    upper_v = cv2.getTrackbarPos('Upper V', 'CV: Blocks')

    canny_t1 = cv2.getTrackbarPos('Canny 1', 'CV: Blocks')
    canny_t2 = cv2.getTrackbarPos('Canny 2', 'CV: Blocks')
    d_kernel_size = cv2.getTrackbarPos('D-Kernel', 'CV: Blocks')
    corner_acc = cv2.getTrackbarPos('Corner Accuracy', 'CV: Blocks')


    # apply color mask to find blocks
    lower = (lower_h, lower_s, lower_v)
    upper = (upper_h, upper_s, upper_v)
    img_masked = cv2.inRange(img, lower, upper)

    # find edges
    img_canny = cv2.Canny(img_masked, canny_t1, canny_t2)
    kernel = np.ones((d_kernel_size, d_kernel_size))
    img_edges = cv2.dilate(img_canny, kernel, iterations=1)

    # find contours
    min_contour_area = cv2.getTrackbarPos('Contour Area', 'Corner Detection')
    contours, _ = cv2.findContours(img_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        # get contour area
        area = cv2.contourArea(contour)

        # skip if contour is too small
        if area < min_contour_area:
            continue

        # draw contour
        cv2.drawContours(img, contour, -1, (0, 0, 0), 2)
        cv2.drawContours(img, contour, -1, (0, 0, 255), 1)

        # find corners
        peri = cv2.arcLength(contour, True)
        corners = cv2.approxPolyDP(contour, corner_acc * 0.01 * peri, True)

        x_sum = 0
        y_sum = 0
        
        # mark corners
        for corner in corners:
            x_sum += corner[0][0]
            y_sum += corner[0][1]

            cv2.circle(img, corner[0], 2, (0, 0, 0), -1)
            cv2.circle(img, corner[0], 1, (0, 255, 0), -1)

        num_corners = len(corners)

        x_sum //= num_corners
        y_sum //= num_corners

        # mark contour's center
        cv2.circle(img, (x_sum, y_sum), 2, (0, 0, 0), -1)
        cv2.circle(img, (x_sum, y_sum), 1, (255, 0, 0), -1)

        # label contour with number of corners
        x, y, _, _ = cv2.boundingRect(corners)
        cv2.putText(img, str(num_corners), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)

        # label contour's center with relative coordinates
        shape = img.shape
        cv2.putText(img, str(round(x_sum/shape[0], 2)) + ' ' + str(round(y_sum/shape[1], 2)), (x_sum, y_sum), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1)

    return []


def find_shadow(img) -> Shadow:

    lower_h = cv2.getTrackbarPos('Lower H', 'CV: Shadow')
    lower_s = cv2.getTrackbarPos('Lower S', 'CV: Shadow')
    lower_v = cv2.getTrackbarPos('Lower V', 'CV: Shadow')
    upper_h = cv2.getTrackbarPos('Upper H', 'CV: Shadow')
    upper_s = cv2.getTrackbarPos('Upper S', 'CV: Shadow')
    upper_v = cv2.getTrackbarPos('Upper V', 'CV: Shadow')

    canny_t1 = cv2.getTrackbarPos('Canny 1', 'CV: Shadow')
    canny_t2 = cv2.getTrackbarPos('Canny 2', 'CV: Shadow')
    d_kernel_size = cv2.getTrackbarPos('D-Kernel', 'CV: Shadow')
    corner_acc = cv2.getTrackbarPos('Corner Accuracy', 'CV: Shadow')

    return None
