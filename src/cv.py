import cv2
import numpy as np

def color_mask(img, lower_threshold, upper_threshold):
    # Blur to reduce noise
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    # Convert to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_threshold, upper_threshold)

    return mask

def find_contours(img, threshold_1, threshold_2):
    # Blur to reduce noise
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    # Convert to grayscale
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

    # Find and dilate edges
    canny = cv2.Canny(gray, threshold_1, threshold_2)
    dilate = cv2.dilate(canny, np.ones((2, 2)), iterations=1)

    contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours

def find_corners(contour):
    peri = cv2.arcLength(contour, True)
    corners = cv2.approxPolyDP(contour, 0.02 * peri, True)

    return corners

def perspective_transformation(img, corners_from, corners_to):
    p1 = np.float32(corners_from)
    p2 = np.float32(corners_to)

    matrix = cv2.getPerspectiveTransform(p1, p2)

    result = cv2.warpPerspective(img, matrix, (200, 200)) # TODO: replace tupel with size of p2

    return result