from pyniryo import cv2
import numpy as np
import trackbar as tb


def blur(img, window_name):
    kernel_size = cv2.getTrackbarPos(tb.TB_BLUR_K, window_name) * 2 + 1
    
    blur_kernel = (kernel_size, kernel_size)

    img_blurred = cv2.GaussianBlur(img, blur_kernel, 1)

    return img_blurred


def color_mask(img, window_name):
    lower_h = cv2.getTrackbarPos(tb.TB_MASK_L_H, window_name)
    lower_s = cv2.getTrackbarPos(tb.TB_MASK_L_S, window_name)
    lower_v = cv2.getTrackbarPos(tb.TB_MASK_L_V, window_name)
    upper_h = cv2.getTrackbarPos(tb.TB_MASK_U_H, window_name)
    upper_s = cv2.getTrackbarPos(tb.TB_MASK_U_S, window_name)
    upper_v = cv2.getTrackbarPos(tb.TB_MASK_U_V, window_name)

    lower = (lower_h, lower_s, lower_v)
    upper = (upper_h, upper_s, upper_v)

    img_masked = cv2.inRange(img, lower, upper)

    return img_masked


def find_edges(img, window_name):
    threshold_1 = cv2.getTrackbarPos(tb.TB_CANNY_1, window_name)
    threshold_2 = cv2.getTrackbarPos(tb.TB_CANNY_2, window_name)

    img_canny = cv2.Canny(img, threshold_1, threshold_2)
    
    kernel_size = cv2.getTrackbarPos(tb.TB_DILATE_K, window_name)

    kernel = np.ones((kernel_size, kernel_size))
    img_edges = cv2.dilate(img_canny, kernel, iterations=1)

    return img_edges


def find_contours(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours


def contour_too_small(contour, window_name):
    area = cv2.contourArea(contour)

    min_contour_area = cv2.getTrackbarPos(tb.TB_CONT_AR, window_name)

    return area < min_contour_area


def find_corners(contour, window_name):
    accuracy = cv2.getTrackbarPos(tb.TB_CORN_ACC, window_name)

    perimeter = cv2.arcLength(contour, True)

    corners = cv2.approxPolyDP(contour, perimeter * 0.01 * accuracy, True)

    return corners


def get_center(corners):
    x_sum = 0
    y_sum = 0
    
    for corner in corners:
        x_sum += corner[0][0]
        y_sum += corner[0][1]

    num_corners = len(corners)

    x_sum //= num_corners
    y_sum //= num_corners

    return (x_sum, y_sum)
